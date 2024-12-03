"""
Creating custom types for the data that is being provided by the various GBFS data sources.
"""

from dataclasses import dataclass, field


@dataclass
class Feed:
    data: dict[str, str] = field(default_factory=dict)
    
    def __getitem__(self, key: str):
        if key in self.data:
            return self.data[key]
        else:
            raise KeyError(f"There is no key named {key}")
    
    def __setitem__(self, key: str, url: str):
        self.data[key] = url
                                                                                                                      

@dataclass
class FeedsPerLanguage:
    data: dict[str, list[Feed]] = field(default_factory=dict)

    def __getitem__(self, language: str):
        if language in self.data:
            return self.data[language]
        else:
            raise KeyError(f"There is no key named {language}")

    def __setitem__(self, language: str, feed_for_language: list[Feed]):
        self.data[language] = feed_for_language


@dataclass
class LanguageOptions:
    data: dict[str, FeedsPerLanguage] = field(default_factory=dict)

    def __getitem__(self, language: str):
        if language in self.data: 
            return self.data[language]
        else:
            raise KeyError(f"There is no key named {language}")

    def __setitem__(self, language: str, feeds_of_all_languages: FeedsPerLanguage):
        self.data[language] = feeds_of_all_languages 


@dataclass
class AllData:
    data: dict[str, LanguageOptions] = field(default_factory=dict)

    def __getitem__(self, name: str):
        if name in self.data:
            return self.data[name]
        else:
            raise KeyError(f"There is no key name {name}")

    def __setitem__(self, name: str, data: LanguageOptions):
        self.data[name] = data

