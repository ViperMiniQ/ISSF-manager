from typing_extensions import TypedDict


class FontSettings(TypedDict):
    size: int
    family: str
    weight: str
    slant: str
    underline: int
    overstrike: int


class FontModeSettings(FontSettings):
    mode: str
    divisor: int
