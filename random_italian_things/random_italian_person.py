import os
import pandas as pd
import numpy as np
import json
from typing import Dict
from codicefiscale import codicefiscale
from .utils import random_birthday, random_phone_number


class RandomItalianPerson:

    municipalities = None
    names = None
    surnames = None
    addresses = None

    def __init__(self, surname=None):
        """Create a new random Italian person."""
        if RandomItalianPerson.municipalities is None:
            RandomItalianPerson.municipalities = pd.read_csv(
                "{}/datasets/municipalities.csv".format(
                    os.path.dirname(os.path.abspath(__file__))),
                dtype={"cap": str}
            )
        if RandomItalianPerson.names is None:
            RandomItalianPerson.names = pd.read_csv(
                "{}/datasets/names.csv".format(
                    os.path.dirname(os.path.abspath(__file__)))
            )
            RandomItalianPerson.frequencies = (
                RandomItalianPerson.names.number / RandomItalianPerson.names.number.sum()
            ).values
            RandomItalianPerson.names = RandomItalianPerson.names.drop(columns=[
                                                                       "number"])

        if RandomItalianPerson.surnames is None:
            RandomItalianPerson.surnames = pd.read_csv(
                "{}/datasets/surnames.csv".format(
                    os.path.dirname(os.path.abspath(__file__)))
            )

        if RandomItalianPerson.addresses is None:
            RandomItalianPerson.addresses = pd.read_csv(
                "{}/datasets/addresses.csv".format(
                    os.path.dirname(os.path.abspath(__file__))),
                dtype={"cap": str}
            )

        if surname is None:
            surname_data = RandomItalianPerson.surnames.sample(n=1)
        else:
            surname_data = surname

        name_data = RandomItalianPerson.names.iloc[np.random.choice(
            RandomItalianPerson.names.index, p=RandomItalianPerson.frequencies)]
        municipality_data = RandomItalianPerson.municipalities[
            RandomItalianPerson.municipalities.province.isin(
                surname_data.province)
        ].sample(n=1)

        address_data = RandomItalianPerson.addresses.sample(n=1)

        self._data = {
            **surname_data.reset_index(drop=True).iloc[0].to_dict(),
            **name_data.to_dict(),
            **{
                "birth_{}".format(c): v
                for c, v in municipality_data.reset_index(drop=True).iloc[0].to_dict().items()
            },
            "birthdate": random_birthday().isoformat(),
            **address_data.reset_index(drop=True).iloc[0].to_dict()
        }

        self._data["codice_fiscale"] = codicefiscale.encode(
            surname=self.surname,
            name=self.name,
            sex=self.sex,
            birthdate=self.birthdate,
            birthplace=self.birthplace
        )
        self._data["phone_number"] = random_phone_number()

        self.surname_data = surname_data

    @property
    def name(self) -> str:
        return self._data["name"]

    @property
    def surname(self) -> str:
        return self._data["surname"]

    @property
    def birthplace(self) -> str:
        return self._data["birth_municipality"]

    @property
    def tax_code(self) -> str:
        return self._data["codice_fiscale"]

    @property
    def birthdate(self) -> str:
        return self._data["birthdate"]

    @property
    def sex(self) -> str:
        return self._data["sex"]

    @property
    def phone_number(self) -> str:
        return self._data["phone_number"]

    @property
    def data(self) -> Dict:
        return self._data.copy()

    def describe(self) -> str:
        """Return short paragraph with human readable description of the person."""
        return (
            "{name} {surname} è nata/o a {birth_municipality} ({birth_province_code}) il {birthdate}."
            " Ora vive a {municipality} ({province_code}) in {address} {house_number}."
        ).format(**self._data)

    def __repr__(self) -> str:
        return json.dumps(self._data, indent=4)

    __str__ = __repr__
