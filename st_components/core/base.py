import itertools

from . import _bridge

_component_counter = itertools.count()

from .context import KEY, set_context
from .models import ElementFiber, ElementState, Fiber, HookSlot, Props, State
from .refs import bind_ref
from .store import _cleanup_effect_slots, fibers, register_component, track_rendered_fiber, unregister_component


def to_tuple(value):
    if isinstance(value, tuple):
        return value
    return (value,)


def _auto_key_children(children):
    """Assign ``{classname}_{index}`` keys to children that have no explicit key."""
    for i, child in enumerate(children):
        if isinstance(child, Component) and child.props.key is None:
            child.props["key"] = f"{type(child).__name__}_{i}"


def _ensure_key(obj):
    """Assign a default key to a standalone object (no sibling index)."""
    if isinstance(obj, Component) and obj.props.key is None:
        obj.props["key"] = type(obj).__name__


_MAX_RENDER_DEPTH = 64


def render_to_element(obj, index=0, _depth=0):
    if isinstance(obj, Element):
        return obj
    if isinstance(obj, Component):
        if _depth >= _MAX_RENDER_DEPTH:
            raise RecursionError(
                f"Component render chain exceeded {_MAX_RENDER_DEPTH} levels — "
                f"likely an infinite loop in {type(obj).__name__}.render()."
            )
        return render_to_element(obj.render(), index, _depth + 1)
    return Value(key=f"value_{index}", value=obj)


def render(obj):
    """Render *obj* into the Streamlit output.

    - **Element** → calls ``obj.render()`` (imperative widget output).
    - **Component** → resolves to an Element, then renders it.
    - **Other** (str, number, etc.) → passed to ``st.write()``.
    - **None** → no-op.
    """
    if isinstance(obj, Element):
        return obj.render()
    if isinstance(obj, Component):
        return render_to_element(obj).render()
    if obj is not None:
        _bridge.write(obj)


class Component:
    """Base class for stateful UI building blocks.

    Subclass and implement :meth:`render` to return child Components or
    Elements.  State persists across Streamlit reruns via the fiber system.

    Define an inner ``State`` subclass for typed state with defaults::

        class Counter(Component):
            class CounterState(State):
                count: int = 0

            def render(self):
                self.state.count += 1
                return text(key="t")(str(self.state.count))

    Define an inner ``Props`` subclass for typed, validated props::

        class Card(Component):
            class CardProps(Props):
                title: str = "Untitled"
                bordered: bool = True

    Lifecycle hooks: :meth:`component_did_mount`, :meth:`component_did_update`,
    :meth:`component_did_unmount`.

    For scoped re-rendering (Streamlit fragments), wrap the subtree in a
    ``fragment(scoped=True)`` element instead of annotating the component::

        from st_components.elements import fragment

        class Live(Component):
            def render(self):
                return fragment(key="f", scoped=True, run_every="5s")(
                    my_chart, my_controls,
                )
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for attr in list(vars(cls).values()):
            if isinstance(attr, type):
                if issubclass(attr, State) and attr is not State:
                    cls.__initial_state_class__ = attr
                elif issubclass(attr, Props) and attr is not Props:
                    cls.__props_class__ = attr

    def __init__(self, **props):
        props_cls = getattr(type(self), "__props_class__", Props)
        self.props = props_cls(props)
        self._state = None  # created lazily by _ensure_initial_state()
        self._component_id = f"{type(self).__name__}:{next(_component_counter)}"
        self._fiber_key = None
        self._hook_index = 0
        self._pending_hook_effects = {}
        self._decorate_render()

    def _ensure_initial_state(self):
        """Lazily create the initial state object.  Skipped when the component
        will re-attach to an existing fiber (the common case on re-render)."""
        if self._state is None:
            initial_cls = getattr(type(self), "__initial_state_class__", None)
            self._state = initial_cls() if initial_cls is not None else State()
        return self._state

    @property
    def is_mounted(self):
        return self._fiber_key is not None and self._fiber_key in fibers()

    def component_did_mount(self):
        """Called once after the component's fiber is first created."""

    def component_did_unmount(self):
        """Called when the component is removed from the tree."""

    def component_did_update(self, prev_state):
        """Called after a render cycle where ``self.state`` differs from *prev_state*."""

    def mount(self):
        if self.is_mounted:
            raise RuntimeError("Can't mount a component that's already mounted")
        register_component(self._component_id, self)
        fibers()[self._fiber_key] = Fiber(state=self._ensure_initial_state(), component_id=self._component_id, previous_state=None)
        self.component_did_mount()

    def unmount(self):
        if not self.is_mounted:
            raise RuntimeError("Can't unmount a component that's not already mounted")
        unregister_component(self.fiber.component_id)
        del fibers()[self._fiber_key]
        self.component_did_unmount()

    @property
    def fiber(self):
        return fibers().get(self._fiber_key) if self._fiber_key else None

    @property
    def key(self):
        return self.props.key

    @key.setter
    def key(self, value):
        raise RuntimeError("Can't set a component key on a living instance, it must be passed as a prop during init.")

    @property
    def children(self):
        return self.props.children

    @children.setter
    def children(self, value):
        self.props.children = list(value)

    def _make_state(self, data):
        cls = getattr(type(self), "__initial_state_class__", State)
        if isinstance(data, cls):
            return data
        if isinstance(data, dict):
            return cls(**data)
        raise TypeError(f"Can only assign a dict to state, got {type(data)}")

    @property
    def state(self):
        if self.is_mounted:
            return self.fiber.state
        return self._ensure_initial_state()

    @state.setter
    def state(self, value):
        if not self.is_mounted:
            self._state = self._make_state(value)

    def set_state(self, other=None, /, **kwargs):
        """Update component state.

        Accepts a dict/State as positional arg (replaces state) and/or
        keyword args (merged into current state).
        """
        if other is not None:
            new = self._make_state(other)
            if self.is_mounted:
                self.fiber.state = new
            else:
                self._state = new
        self.state.update(**kwargs)

    @property
    def ref(self):
        """Ref to this component — chain with attribute or item access to reach children.

        ::

            self.ref                          # Ref to this component
            self.ref.panel.results            # Ref to a child (attribute nav)
            self.ref["panel"]["results"]      # same via __getitem__

            self.ref.panel.results("new children")
            self.ref.panel.results(color="blue")("child_a")
            self.ref.panel.results.reset()
            self.ref.parent                   # Ref to parent component
        """
        from .refs import Ref
        return Ref._from_path(self._fiber_key)

    def get_ref(self, path):
        """Return a :class:`Ref` to a child node by relative path.

        *path* is **relative to this component's fiber**::

            self.get_ref("panel.results")("new children")
            self.get_ref("panel.results").reset()
        """
        from .refs import Ref
        return Ref._from_path(f"{self._fiber_key}.{path}")

    @property
    def parent(self):
        """Ref to the parent node in the tree, or ``None`` for the root."""
        return self.ref.parent

    @property
    def root(self):
        """Ref to the root App node — equivalent to ``get_app()`` as a Ref."""
        from .refs import Ref
        return Ref._from_path("app")

    def sync_state(self, state_key):
        """Return a callback ``fn(value)`` that writes *value* into ``self.state[state_key]``.

        Useful for binding a widget's ``on_change`` directly to a state field::

            text_input(key="name", on_change=self.sync_state("name"))("Name")
        """
        def sync(value):
            self.state.update(**{state_key: value})
        return sync

    def _begin_hook_cycle(self):
        self._hook_index = 0
        self._pending_hook_effects = {}

    def _claim_hook_slot(self, kind):
        if not self.is_mounted:
            raise RuntimeError("Hooks require a mounted Component or Element.")

        hooks = self.fiber.hooks
        index = self._hook_index
        self._hook_index += 1

        if index == len(hooks):
            slot = HookSlot(kind=kind)
            hooks.append(slot)
            return index, slot

        slot = hooks[index]
        if slot.kind != kind:
            raise RuntimeError(
                f"Hook order changed for {type(self).__name__}: "
                f"expected {slot.kind!r} at slot {index}, got {kind!r}."
            )
        return index, slot

    def _use_hook_slot(self, kind):
        _, slot = self._claim_hook_slot(kind)
        return slot

    def _queue_hook_effect(self, index, effect):
        self._pending_hook_effects[index] = effect

    def _flush_hook_effects(self):
        if not self.is_mounted:
            return
        for index, effect in self._pending_hook_effects.items():
            slot = self.fiber.hooks[index]
            if slot.cleanup is not None:
                slot.cleanup()
                slot.cleanup = None
            cleanup = effect()
            if cleanup is not None and not callable(cleanup):
                raise TypeError(
                    f"use_effect() cleanup must be callable or None, got {type(cleanup)}."
                )
            slot.cleanup = cleanup
        self._pending_hook_effects.clear()

    def _cleanup_hook_effects(self):
        if self.fiber is not None:
            _cleanup_effect_slots(self.fiber.hooks)

    def _end_hook_cycle(self):
        if self.is_mounted and self._hook_index != len(self.fiber.hooks):
            raise RuntimeError(
                f"Hook count changed for {type(self).__name__}: "
                f"expected {len(self.fiber.hooks)}, got {self._hook_index}."
            )

    def __repr__(self):
        cls = type(self).__name__
        path = self._fiber_key or self.props.key or "(auto)"
        mounted = "mounted" if self.is_mounted else "unmounted"
        return f"<{cls} key={path!r} {mounted}>"

    def __getitem__(self, key):
        """Navigate to a child node: ``self["panel"]["results"]``."""
        return self.ref[key]

    def __getattr__(self, name):
        """Navigate to a child node: ``self.panel.results``.

        Only triggered for names not found on the instance or class —
        normal attributes (props, state, children, etc.) are unaffected.
        """
        if name.startswith("_"):
            raise AttributeError(name)
        try:
            return self.ref[name]
        except RuntimeError:
            raise AttributeError(name)

    def __call__(self, *children):
        self.props.children = list(children)
        _auto_key_children(self.props.children)
        return self

    def _decorate_render(self):
        if not hasattr(self.render, "_decorated"):
            self.render = self._render_decorator(self.render)

    def _apply_overrides(self):
        """Apply fiber overrides (from callbacks) to this instance's props."""
        overrides = self.fiber.overrides if self.fiber else None
        if overrides is None:
            return
        props_ov = overrides.get("props")
        if props_ov:
            self.props.update(props_ov)
        children_ov = overrides.get("children")
        if children_ov is not None:
            self.props.children = list(children_ov)
            _auto_key_children(self.props.children)

    def _render_component_body(self, render_func):
        _ensure_key(self)
        self._fiber_key = KEY(self.key)
        bind_ref(self, self._fiber_key, "component")
        if not self.is_mounted:
            self.mount()
        if self.fiber.component_id != self._component_id:
            unregister_component(self.fiber.component_id)
            self.fiber.component_id = self._component_id
        register_component(self._component_id, self)
        self._apply_overrides()
        track_rendered_fiber(self._fiber_key)
        with set_context(key=self.key, component=self):
            self._begin_hook_cycle()
            raw_children = to_tuple(render_func())
            _auto_key_children(raw_children)
            children = [render_to_element(child, i) for i, child in enumerate(raw_children)]
            self._end_hook_cycle()
            return Anchor(key=self.key)(*children)

    def _render_decorator(self, render_func):
        def decorated():
            return self._render_component_body(render_func)

        decorated._decorated = True
        return decorated

    def render(self):
        """Return child Component(s)/Element(s), a tuple of them, or None."""
        raise NotImplementedError(
            f"{type(self).__name__} must implement a render() method.  "
            f"Return child Components/Elements, a tuple of them, or None."
        )


class Element(Component):
    """Terminal node that renders a Streamlit widget imperatively.

    Subclass and implement :meth:`render` — it must return ``None`` and call
    ``st.*`` functions directly.  The widget's current value is exposed as
    ``self.state.output`` (read-only outside render).

    Set ``_default_output_prop`` to a prop name to use that prop as the
    initial output before the widget registers in session_state::

        class my_slider(Element):
            _default_output_prop = "value"

            def __init__(self, *, key, value=0, **kw):
                Element.__init__(self, key=key, value=value, **kw)

            def render(self):
                st.slider("Label", key=widget_key(), value=self.props.value)
    """

    __initial_state_class__ = ElementState
    _default_output_prop = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if "__initial_state_class__" not in vars(cls):
            cls.__initial_state_class__ = getattr(cls.__bases__[0], "__initial_state_class__", ElementState)

    def __init__(self, **props):
        super().__init__(**props)
        # Elements always need their state (it holds output/handle), but defer
        # to _ensure_initial_state which uses __initial_state_class__ = ElementState

    @property
    def is_mounted(self):
        return (
            self._fiber_key is not None
            and isinstance(fibers().get(self._fiber_key), ElementFiber)
        )

    def get_output(self, raw):
        """Transform the raw session_state value before exposing it as state.output.

        *raw* is ``None`` when the widget has not yet been registered in session_state.

        Subclasses can set ``_default_output_prop`` to a prop name (e.g. ``"value"``)
        instead of overriding this method: the prop value is returned when *raw* is None.
        """
        if raw is not None:
            return raw
        if self._default_output_prop is not None:
            return self.props.get(self._default_output_prop)
        return None

    def mount(self):
        if self.is_mounted:
            raise RuntimeError("Can't mount an element that's already mounted")
        from .access import widget_key
        fibers()[self._fiber_key] = ElementFiber(
            path=self._fiber_key,
            widget_key=widget_key(self._fiber_key),
            state=self._ensure_initial_state(),
        )

    def _current_output(self):
        """Read the current widget value from session_state and apply get_output()."""
        wk = self.fiber.widget_key if self.fiber else None
        raw = _bridge.get_widget_value(wk) if wk else None
        return self.get_output(raw)

    def _render_decorator(self, render_func):
        def decorated():
            from .access import widget_key
            _ensure_key(self)
            element_path = KEY(self.key)
            self._fiber_key = element_path
            bind_ref(self, element_path, "element")

            if not self.is_mounted:
                self.mount()
            else:
                self.fiber.widget_key = widget_key(element_path)

            self._apply_overrides()
            track_rendered_fiber(element_path)

            with set_context(key=self.key, component=self):
                with self.state._writable():
                    self._begin_hook_cycle()
                    result = render_func()
                    if result is not None:
                        raise TypeError(
                            f"Element.render() must return None, got {type(result).__name__!r} "
                            f"from {type(self).__name__}. Elements should render imperatively via st.* calls or recursively by calling render(child)."
                        )
                    self._end_hook_cycle()
                    self._flush_hook_effects()
                    self.state.output = self._current_output()

        decorated._decorated = True
        return decorated

    def render(self):
        raise NotImplementedError("Element subclasses must implement a render method")


class Anchor(Element):
    """Represents a Component's position in the element tree.

    An Anchor has the same key as its parent Component and renders its children
    in the right key_context, without creating its own fiber (the Component's
    Fiber already exists at this path).
    """

    def _render_decorator(self, render_func):
        def decorated():
            with set_context(key=self.key):
                render_func()
        decorated._decorated = True
        return decorated

    def render(self):
        for child in self.children:
            render(child)


class Value(Element):
    """Wraps a plain Python value as an Element, rendering it via st.write()."""

    def render(self):
        render(self.props.get("value"))
