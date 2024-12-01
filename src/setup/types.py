from typing import NamedTuple


class Feed(NamedTuple):
    url: str
    name: str


class FeedCollection(NamedTuple):
    name: str
    feeds: list[Feed]


class LanguageOptions(NamedTuple):
    language: str
    language_feeds: FeedCollection


class DataDict(NamedTuple):
    name: str
    language_data: LanguageOptions


class BaseData(NamedTuple):
    data: DataDict


class DataFromChosenFeed(NamedTuple):
    name: str
    vehicle_data: dict[str, list[dict[str, str|int]]] 
