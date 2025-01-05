import os
from pathlib import Path 

PARENT_DIR = Path(__file__).parent.resolve().parent.resolve().parent.resolve()
DATA_DIR = PARENT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"


def make_data_directories():

    for path in [DATA_DIR, RAW_DATA_DIR]:
        if not Path(path).exists():
            os.mkdir(path)

