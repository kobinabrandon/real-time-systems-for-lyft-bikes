from typing import NamedTuple


class Feeds(NamedTuple):
    url: str
    name: str


class FeedCollection(NamedTuple):
    name: str
    feeds: list[Feeds]


class LanguageOptions(NamedTuple):
    language_name: str
    info: dict[str, FeedCollection]


class CompleteData(NamedTuple):
    name: str
    data: dict[str, LanguageOptions]

