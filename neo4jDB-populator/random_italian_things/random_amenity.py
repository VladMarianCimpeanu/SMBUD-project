import pandas as pd
import os


class Amenity:

    _amenities = None  # this static attribute contain all the available amenities

    def __init__(self, city: str):
        if Amenity._amenities is None:
            Amenity._load_data()
        self._new_amenity(city)

    @staticmethod
    def _load_data() -> None:
        configuration_file = pd.read_csv("{}/datasets/datasets_to_read.txt".format(
                os.path.dirname(os.path.abspath(__file__))))
        Amenity._amenities = {}
        for index, row in configuration_file.iterrows():
            Amenity._read_city(row['value'], row['key'])

    @staticmethod
    def _read_city(city_file: str, city_name: str) -> None:
        city_file = city_file.split(".")[0].lower() + "_amenities.csv"
        Amenity._amenities[city_name] = pd.read_csv(("{}/datasets/{}".format(
                os.path.dirname(os.path.abspath(__file__)), city_file)))

    def _new_amenity(self, city_name: str) -> None:
        """create a new amenity that has not been created yet"""
        amenity_data = Amenity._amenities[city_name].sample(n=1)
        # remove the created amenity from the available ones
        Amenity._amenities[city_name].drop(
            Amenity._amenities[city_name].index[Amenity._amenities[city_name]['id'] == amenity_data.iloc[0]['id']], inplace=True)
        self._data = {
            **amenity_data.reset_index(drop=True).iloc[0].to_dict()
        }

    @property
    def amenity(self) -> str:
        return self._data['amenity']

    @property
    def name(self) -> str:
        return self._data['name']

    @property
    def street(self) -> str:
        return self._data['addr:street']

    @property
    def city(self) -> str:
        return self._data['addr:city']
