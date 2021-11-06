import os
import pandas as pd
import numpy as np
import json
from typing import Dict
from codicefiscale import codicefiscale
from .utils import random_birthday


class RandomItalianHouse:

    addresses = None

    def __init__(self,city:str):
        """Create a new random Italian house."""
        if RandomItalianHouse.addresses is None:
            self._load_data()

        address_data = RandomItalianHouse.addresses[city].sample(n=1)
        
        self._data = {
            **address_data.reset_index(drop=True).iloc[0].to_dict()
        }

    @staticmethod
    def _load_data():
        # read 'datasets_to_read' that contains as keys the name of the city to read and as values the name
        # of its file.
        datasets_to_read = pd.read_csv(
            "{}/datasets/datasets_to_read.txt".format(
                os.path.dirname(os.path.abspath(__file__)))
        )
        # create a dictionary containing for each city all its possible addresses
        RandomItalianHouse.addresses = {}
        for index, row in datasets_to_read.iterrows():
            RandomItalianHouse._read_city(row['value'], row['key'])

    @staticmethod
    def _read_city(file_name: str, name_key: str):
        RandomItalianHouse.addresses[name_key] = pd.read_csv(
                "{}/datasets/{}".format(
                    os.path.dirname(os.path.abspath(__file__)), file_name),
                dtype={"cap": str})

    @property
    def municipality(self) -> str:
        return self._data["municipality"]

    @property
    def address(self) -> str:
        return self._data["address"] + ", " + self._data["house_number"]

    def __repr__(self) -> str:
        return json.dumps(self._data, indent=4)

    __str__ = __repr__
