from ..core.base import Component, Element
from ..core.context import KEY
from ..core.models import Props
from ..core.store import mark_subtree_keep_alive


class _PreservedBranches(Component):

    def _preserve_hidden_child(self, child):
        if isinstance(child, (Component, Element)):
            mark_subtree_keep_alive(KEY(child.key))


class _SingleChildBranch(Component):

    def render(self):
        children = self.children
        if len(children) != 1:
            raise ValueError(f"{type(self).__name__} expects exactly one child.")
        return children[0]

    @property
    def child(self):
        return self.children[0]


class Conditional(_PreservedBranches):

    class ConditionalProps(Props):
        condition: bool

    def render(self):
        children = self.children
        if len(children) not in (1, 2):
            raise ValueError("Conditional expects exactly one or two children.")

        if self.props.condition:
            if len(children) == 2:
                self._preserve_hidden_child(children[1])
            return children[0]

        self._preserve_hidden_child(children[0])
        if len(children) == 2:
            return children[1]
        return None


class KeepAlive(_SingleChildBranch, _PreservedBranches):

    class KeepAliveProps(Props):
        active: bool = True

    def render(self):
        child = self.child
        if self.props.active:
            return child
        self._preserve_hidden_child(child)
        return None


class Case(_PreservedBranches):

    class CaseProps(Props):
        case: int

    def render(self):
        children = self.children
        selected_index = self.props.case
        if not 0 <= selected_index < len(children):
            selected_index = None

        for index, child in enumerate(children):
            if index != selected_index:
                self._preserve_hidden_child(child)

        if selected_index is None:
            return None
        return children[selected_index]


class Match(_SingleChildBranch):

    class MatchProps(Props):
        when: object


class Default(_SingleChildBranch):
    pass


class Switch(_PreservedBranches):

    class SwitchProps(Props):
        value: object

    def render(self):
        selected_child = None
        default_child = None

        for child in self.children:
            if isinstance(child, Match):
                if child.props.when == self.props.value:
                    if selected_child is not None:
                        raise ValueError("Switch found multiple matching Match children.")
                    selected_child = child
                continue

            if isinstance(child, Default):
                if default_child is not None:
                    raise ValueError("Switch expects at most one Default child.")
                default_child = child
                continue

            raise TypeError("Switch children must be Match or Default components.")

        selected_child = selected_child or default_child

        for child in self.children:
            if child is not selected_child:
                self._preserve_hidden_child(child)

        return selected_child
