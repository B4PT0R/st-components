from typing import Any, Literal

from modict import modict, MISSING


class Props(modict):
    key: str = modict.field(required="always")
    children: list = modict.factory(list)

    @modict.validator("children")
    def _filter_none_children(self, value):
        return [c for c in value if c is not None]


class State(modict):
    pass


class ContextData(modict):
    pass


class HookSlot(modict):
    _config = modict.config(require_all="never")

    kind: str = modict.field(required="always")
    initialized: bool = False
    value: Any = None
    deps: Any = None
    cleanup: Any = None


class Fiber(modict):
    state: State = modict.factory(State)
    component_id: str | None = None
    previous_state: State | None = None
    keep_alive: bool = False
    hooks: list[HookSlot] = modict.factory(list)


class ElementState(State):
    value: Any = None


class ElementFiber(modict):
    path: str = modict.field(required="always")
    widget_key: str | None = None  # set during render via _get_widget_key(); handles revision suffix
    keep_alive: bool = False
    hooks: list[HookSlot] = modict.factory(list)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "cache" not in self:
            self["cache"] = MISSING

    @modict.computed(cache=False)
    def state(self):
        from streamlit import session_state as ss
        cache = self.get("cache", MISSING)
        if cache is not MISSING:
            return ElementState(value=cache)
        value = ss.get(self.widget_key) if self.widget_key else None
        return ElementState(value=value)


class Fibers(modict):
    def __setitem__(self, key, value):
        # Coerce plain dicts to Fiber for backward compat; leave modict subclasses (ElementFiber) as-is
        if isinstance(value, dict) and not isinstance(value, modict):
            value = Fiber(**value)
        super().__setitem__(key, value)

    def __init__(self, data=None, /, **kwargs):
        super().__init__()
        if data is not None:
            items = data.items() if isinstance(data, dict) else data
            for k, v in items:
                self[k] = v
        for k, v in kwargs.items():
            self[k] = v


class SharedStates(modict[str, State]):
    pass


class PreviousStates(modict[str, State]):
    pass


class ClientConfig(modict):
    _config = modict.config(require_all="never")

    showErrorDetails: Literal["full", "stacktrace", "type", "none"] | bool | None = None
    showErrorLinks: Literal["auto"] | bool | None = None
    showSidebarNavigation: bool | None = None
    toolbarMode: Literal["auto", "developer", "viewer", "minimal"] | None = None

    @modict.model_validator(mode="after")
    def _prune_none_fields(self):
        for key in list(self.keys()):
            if self[key] is None:
                del self[key]


class RunnerConfig(modict):
    _config = modict.config(require_all="never")

    fastReruns: bool | None = None
    enforceSerializableSessionState: bool | None = None
    enumCoercion: Literal["off", "nameOnly", "nameAndValue"] | None = None

    @modict.model_validator(mode="after")
    def _prune_none_fields(self):
        for key in list(self.keys()):
            if self[key] is None:
                del self[key]


class BrowserConfig(modict):
    _config = modict.config(require_all="never")

    gatherUsageStats: bool | None = None

    @modict.model_validator(mode="after")
    def _prune_none_fields(self):
        for key in list(self.keys()):
            if self[key] is None:
                del self[key]


class ServerConfig(modict):
    _config = modict.config(require_all="never")

    runOnSave: bool | None = None

    @modict.model_validator(mode="after")
    def _prune_none_fields(self):
        for key in list(self.keys()):
            if self[key] is None:
                del self[key]


class Config(modict):
    _config = modict.config(require_all="never")

    client: ClientConfig | None = None
    runner: RunnerConfig | None = None
    browser: BrowserConfig | None = None
    server: ServerConfig | None = None

    @modict.model_validator(mode="after")
    def _prune_empty_fields(self):
        for key in list(self.keys()):
            value = self[key]
            if value is None or value == {} or value == []:
                del self[key]


class ThemeSection(modict):
    _config = modict.config(require_all="never")

    primaryColor: str | None = None
    backgroundColor: str | None = None
    secondaryBackgroundColor: str | None = None
    textColor: str | None = None
    linkColor: str | None = None
    codeTextColor: str | None = None
    codeBackgroundColor: str | None = None
    borderColor: str | None = None
    showWidgetBorder: bool | None = None
    baseRadius: str | int | float | None = None
    buttonRadius: str | int | float | None = None
    dataframeBorderColor: str | None = None
    dataframeHeaderBackgroundColor: str | None = None
    chartCategoricalColors: list[str] | None = None
    chartSequentialColors: list[str] | None = None
    font: str | None = None
    headingFont: str | None = None
    codeFont: str | None = None
    baseFontSize: str | int | float | None = None
    baseFontWeight: int | None = None
    headingFontWeights: list[int] | None = None
    codeFontSize: str | int | float | None = None

    @modict.model_validator(mode="after")
    def _prune_none_fields(self):
        for key in list(self.keys()):
            if self[key] is None:
                del self[key]


class ThemeFontFace(modict):
    _config = modict.config(require_all="never")

    family: str | None = None
    url: str | None = None
    weight: str | int | None = None
    style: str | None = None
    unicodeRange: str | None = None

    @modict.model_validator(mode="after")
    def _prune_none_fields(self):
        for key in list(self.keys()):
            if self[key] is None:
                del self[key]


class Theme(modict):
    _config = modict.config(require_all="never")

    base: Literal["light", "dark"] | None = None
    primaryColor: str | None = None
    backgroundColor: str | None = None
    secondaryBackgroundColor: str | None = None
    textColor: str | None = None
    linkColor: str | None = None
    codeTextColor: str | None = None
    codeBackgroundColor: str | None = None
    borderColor: str | None = None
    showWidgetBorder: bool | None = None
    baseRadius: str | int | float | None = None
    buttonRadius: str | int | float | None = None
    dataframeBorderColor: str | None = None
    dataframeHeaderBackgroundColor: str | None = None
    chartCategoricalColors: list[str] | None = None
    chartSequentialColors: list[str] | None = None
    font: str | None = None
    headingFont: str | None = None
    codeFont: str | None = None
    baseFontSize: str | int | float | None = None
    baseFontWeight: int | None = None
    headingFontWeights: list[int] | None = None
    codeFontSize: str | int | float | None = None
    sidebar: ThemeSection | None = None
    light: ThemeSection | None = None
    dark: ThemeSection | None = None
    fontFaces: list[ThemeFontFace] | None = None

    @modict.model_validator(mode="after")
    def _prune_empty_fields(self):
        for key in list(self.keys()):
            value = self[key]
            if value is None or value == {} or value == []:
                del self[key]
