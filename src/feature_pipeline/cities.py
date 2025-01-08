import os
from pathlib import Path


class CityInfo:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.base_url: str = self.get_base_url()

    def get_base_url(self) -> str:

        cities_and_feeds = {
            "chicago": "https://gbfs.divvybikes.com/gbfs/2.3/gbfs.json",
            "columbus": "https://gbfs.lyft.com/gbfs/2.3/cmh/gbfs.json",
            "new_york": "https://gbfs.citibikenyc.com/gbfs/2.3/gbfs.json",
            "washington_dc": "https://gbfs.capitalbikeshare.com/gbfs/2.3/gbfs.json",
            "portland": "https://gbfs.biketownpdx.com/gbfs/2.3/gbfs.json"
        }

        return cities_and_feeds[self.name]

    def make_paths(self, primary_path: Path):
    
        path_to_create = primary_path / self.name
        if not Path(path_to_create).exists():
            os.mkdir(path_to_create)

