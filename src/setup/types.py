from dataclasses import dataclass


@dataclass
class Feed:
    url: str
    name: str




@dataclass
class FeedsPerLanguage:
    name: str
    items: list[Feed] 


@dataclass
class LanguageOptions:
    language: str
    language_feeds: FeedsPerLanguage 

    def __getitem__(self, item: str):
        if item == "language":
            return self.language
        elif item == "language_feeds":
            return self.language_feeds

@dataclass
class DataFromChosenFeed:
    name: str 
    language_data: LanguageOptions 

   def __getitem__(self, item: str):
        if item == "key":
            return self.key
        elif item == "value":
            return self.value
