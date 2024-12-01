from typing import NamedTuple


class Feeds(NamedTuple):
    url: str
    name: str


class FeedCollection(NamedTuple):
    name: str
    feeds: list[Feeds]


class LanguageOptions(NamedTuple):
    language_name: str
    info: FeedCollection


class DataDict(NamedTuple):
    name: str
    data: LanguageOptions


class CompleteData(NamedTuple):
    name: str 
    data: DataDict

