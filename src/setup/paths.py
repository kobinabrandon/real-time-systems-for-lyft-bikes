import os
from tqdm import tqdm
from pathlib import Path 

from src.feature_pipeline.cities import CityInfo


PARENT_DIR = Path(__file__).parent.resolve().parent.resolve().parent.resolve()
DATA_DIR = PARENT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
MODELS_DIR = PARENT_DIR / "models"
GEOGRAPHICAL_DATA = DATA_DIR / "geographical"


def make_data_directories(
    city_names: list[str] = ["portland", "columbus", "new_york", "washington_dc", "chicago"]
):  
    primary_paths: list[Path] = [RAW_DATA_DIR, GEOGRAPHICAL_DATA, MODELS_DIR]

    for path in primary_paths:
        if not Path(path).exists():
            os.mkdir(path)
        
        for name in city_names:
            city = CityInfo(name=name)
            city.make_paths(primary_path=path)

