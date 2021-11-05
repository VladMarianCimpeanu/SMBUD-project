import os
import pandas as pd
import numpy as np
import json
from typing import Dict
from codicefiscale import codicefiscale
from .utils import random_birthday


class RandomItalianHouse:

    addresses = None

    def __init__(self):
        """Create a new random Italian house."""

        if RandomItalianHouse.addresses is None:
            RandomItalianHouse.addresses = pd.read_csv(
                "{}/datasets/addresses.csv".format(
                    os.path.dirname(os.path.abspath(__file__))),
                dtype={"cap": str}
            )

        address_data = RandomItalianHouse.addresses.sample(n=1)

        self._data = {
            **address_data.reset_index(drop=True).iloc[0].to_dict()
        }

    @property
    def municipality(self) -> str:
        return self._data["municipality"]

    @property
    def address(self) -> str:
        return self._data["address"] + ", " + self._data["house_number"]

    def __repr__(self) -> str:
        return json.dumps(self._data, indent=4)

    __str__ = __repr__
