from modict import modict

from .page import Page


class RouterProps(modict):
    position = "sidebar"
    expanded = False
    children = modict.factory(list)


class Router:

    def __init__(self, **props):
        unsupported = {
            field: props[field]
            for field in (
                "page_title",
                "page_icon",
                "layout",
                "initial_sidebar_state",
                "menu_items",
            )
            if field in props
        }
        if unsupported:
            names = ", ".join(sorted(unsupported))
            raise TypeError(
                f"Router does not accept global page config props ({names}). "
                "Pass them to App(...) instead."
            )
        self.props = RouterProps(props)

    @property
    def children(self):
        return self.props.children

    @children.setter
    def children(self, value):
        self.props.children = value

    def __call__(self, *children):
        for child in children:
            if not isinstance(child, Page):
                raise TypeError(
                    f"Router expects only Page children, got {type(child)}"
                )
        self.props.children = list(children)
        return self

    @property
    def pages(self):
        return self.props.children
