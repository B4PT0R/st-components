from typing import Any, Literal, Optional

import streamlit as st

from ...core import Element, Ref
from .._types import UseColumnWidth, Width, WidthWithoutContent


class image(Element):
    def __init__(
        self,
        image: Any = None,
        caption: Optional[str | list[str]] = None,
        width: Width = "content",
        use_column_width: UseColumnWidth = None,
        clamp: bool = False,
        channels: Literal["RGB", "BGR"] = "RGB",
        output_format: Literal["auto", "JPEG", "PNG"] = "auto",
        *,
        key: str,
        ref: Optional[Ref] = None,
        use_container_width: Optional[bool] = None,
        link: Optional[str] = None,
    ):
        Element.__init__(self, key=key, image=image, ref=ref, caption=caption, width=width, use_column_width=use_column_width, clamp=clamp, channels=channels, output_format=output_format, use_container_width=use_container_width, link=link)

    def render(self):
        image_data = self.children[0] if self.children else self.props.get("image")
        st.image(image_data, **self.props.exclude("key", "children", "image", "ref"))


class audio(Element):
    def __init__(
        self,
        data: Any = None,
        format: str = "audio/wav",
        start_time: int | float | str = 0,
        *,
        key: str,
        ref: Optional[Ref] = None,
        sample_rate: Optional[int] = None,
        end_time: Optional[int | float | str] = None,
        loop: bool = False,
        autoplay: bool = False,
        width: WidthWithoutContent = "stretch",
    ):
        Element.__init__(self, key=key, data=data, format=format, start_time=start_time, ref=ref, sample_rate=sample_rate, end_time=end_time, loop=loop, autoplay=autoplay, width=width)

    def render(self):
        data = self.children[0] if self.children else self.props.get("data")
        st.audio(data, **self.props.exclude("key", "children", "data", "ref"))


class video(Element):
    def __init__(
        self,
        data: Any = None,
        format: str = "video/mp4",
        start_time: int | float | str = 0,
        *,
        key: str,
        ref: Optional[Ref] = None,
        subtitles: Any = None,
        end_time: Optional[int | float | str] = None,
        loop: bool = False,
        autoplay: bool = False,
        muted: bool = False,
        width: WidthWithoutContent = "stretch",
    ):
        Element.__init__(self, key=key, data=data, format=format, start_time=start_time, ref=ref, subtitles=subtitles, end_time=end_time, loop=loop, autoplay=autoplay, muted=muted, width=width)

    def render(self):
        data = self.children[0] if self.children else self.props.get("data")
        st.video(data, **self.props.exclude("key", "children", "data", "ref"))
