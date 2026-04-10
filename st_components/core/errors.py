"""Typed exception hierarchy for st-components.

All public exceptions inherit from :class:`StcError` so that user code can
catch the entire family with a single ``except StcError`` clause.

Categories
----------
- **Lifecycle** -- mount, unmount, render, hook ordering
- **State** -- state access, type mismatches, missing fibers
- **Context** -- render context, refs, callbacks
- **Config** -- App / Theme / Config / Router / Page validation
- **Component definition** -- @component decorator, Props/State classes
"""


# ── Base ────────────────────────────────────────────────────────────────────

class StcError(Exception):
    """Base class for all st-components errors."""


class StcTypeError(StcError, TypeError):
    """A value has the wrong type for the operation."""


class StcValueError(StcError, ValueError):
    """A value is invalid for the given context."""


# ── Lifecycle ───────────────────────────────────────────────────────────────

class LifecycleError(StcError, RuntimeError):
    """Error during the component/element lifecycle (mount, unmount, render)."""


class AlreadyMountedError(LifecycleError):
    """Component or Element is already mounted."""


class NotMountedError(LifecycleError):
    """Component or Element is not mounted."""


class RenderError(LifecycleError):
    """Error during a render cycle."""


class RenderDepthError(StcError, RecursionError):
    """Component render chain exceeded the maximum depth."""


# ── Hooks ───────────────────────────────────────────────────────────────────

class HookError(LifecycleError):
    """Error related to hook usage."""


class HookContextError(HookError):
    """Hook called outside a render context."""


class HookOrderError(HookError):
    """Hook order or count changed between renders."""


# ── State ───────────────────────────────────────────────────────────────────

class StateError(StcError, RuntimeError):
    """Error related to state access or manipulation."""


class FiberNotFoundError(StateError):
    """No live fiber found at the given path."""


class SharedStateError(StateError):
    """Shared state namespace not declared or invalid spec."""


class LocalStoreError(StateError):
    """Local store namespace not declared."""


# ── Context / Refs ──────────────────────────────────────────────────────────

class ContextError(StcError, RuntimeError):
    """Error related to the render context or context providers."""


class RefError(ContextError):
    """Error accessing or resolving a Ref."""


class UnresolvedRefError(RefError):
    """Ref has not been resolved to a fiber path yet."""


class CallbackError(ContextError):
    """Error wrapping or invoking a widget callback."""


# ── Config / Validation ────────────────────────────────────────────────────

class ConfigError(StcError):
    """Error in App, Theme, Config, or Router configuration."""


class AppError(ConfigError, RuntimeError):
    """Error in App setup or runtime."""


class RouterError(ConfigError, TypeError):
    """Error in Router setup or child validation."""


class PageError(ConfigError, TypeError):
    """Error in Page setup or child validation."""


# ── Component definition ───────────────────────────────────────────────────

class ComponentDefinitionError(StcError, TypeError):
    """Error in component or element class/function definition."""
