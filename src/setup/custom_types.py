"""
Creating custom types for the data that is being provided by the various GBFS data sources.
"""
from typing import TypeAlias


Feed: TypeAlias = dict[str, str]
FeedsPerLanguage: TypeAlias = dict[str, list[Feed]]
LanguageOptions: TypeAlias = dict[str, FeedsPerLanguage]                                                                                       

AllData: TypeAlias = dict[str, LanguageOptions]
FeedData: TypeAlias = dict[str, dict[str, list[dict[str, int|str]]]]

# ExtractedGeodata: TypeAlias = dict[str, str | list[float]]
StationInformation: TypeAlias = list[dict[str, str | int | float | dict[str, str]]] 
BikeInformation: TypeAlias = list[dict[str, str | int | float | dict[str, str]]] 

ListOfCoordinates: TypeAlias = list[list[float]]
FoundGeodata: TypeAlias = dict[str, list[float]]
OfficialStationGeodata: TypeAlias = list[dict[str, list[float]]] | list[dict[str, str | list[float]]]

