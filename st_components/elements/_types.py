from typing import Any, Callable, Iterable, Literal


WidgetCallback = Callable[..., Any]
LabelVisibility = Literal["visible", "hidden", "collapsed"]
ButtonType = Literal["primary", "secondary", "tertiary"]
Width = Literal["content", "stretch"] | int
WidthWithoutContent = Literal["stretch"] | int
Height = Literal["content", "stretch"] | int
HeightWithoutContent = Literal["stretch"] | int
IconPosition = Literal["left", "right"]
BindOption = Any
SelectWidgetFilterMode = Literal["fuzzy", "contains", "startswith"]
SelectionMode = Literal["single", "multi"]
FeedbackOptions = Literal["thumbs", "faces", "stars"]
DialogWidth = Literal["small", "large"]
Gap = Literal["small", "medium", "large", None]
HorizontalAlignment = Literal["left", "center", "right"]
VerticalAlignment = Literal["top", "center", "bottom", "distribute"]
DismissBehavior = Literal["ignore", "rerun"] | Callable[..., Any]
TextAlignment = Literal["left", "center", "right"]
Anchor = str | Literal[False] | None
Divider = bool | Literal["gray", "rainbow", "blue", "green", "orange", "red", "violet"]
BadgeColor = Literal["red", "orange", "yellow", "blue", "green", "violet", "gray", "grey", "primary"]
SpaceSize = Literal["small", "medium", "large"]
DataSelectionMode = Literal["single-row", "multi-row", "single-column", "multi-column", "single-cell", "multi-cell"]
DeltaArrow = Literal["auto", "up", "down", "off"]
UseColumnWidth = Literal["auto", "always", "never"] | bool | None
SelectionBehavior = Literal["ignore", "rerun"] | Callable[..., Any]
PlotlySelectionMode = Literal["lasso", "points", "box"]
PydeckSelectionMode = Literal["single-object", "multi-object"]
ChartSelectionMode = PlotlySelectionMode | PydeckSelectionMode
MaybeSelectionModes = ChartSelectionMode | Iterable[ChartSelectionMode]
