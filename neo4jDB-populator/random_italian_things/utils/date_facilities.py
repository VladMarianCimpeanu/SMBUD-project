import datetime
import random
from datetime import timedelta


""""it returns a list of random dates between start_date (represented by a tuple (year, month, day)) and end_date
    such that distance between each date can not be more than min_freq and less than max_freq."""


def random_dates(max_freq: int, min_freq: int, start_date: tuple, end_date: tuple) -> list:
    dates = []
    START = datetime.date(start_date[0], start_date[1], start_date[2])
    END = datetime.date(end_date[0], end_date[1], end_date[2])
    day_to_add = START
    while day_to_add < END:
        day_to_add += timedelta(days=1 * random.randint(max_freq, min_freq))
        dates.append(day_to_add.strftime("%Y/%m/%d"))
    return dates


def random_single_date(start_date: tuple, end_date: tuple):
    start = datetime.date(start_date[0], start_date[1], start_date[2])
    end = datetime.date(end_date[0], end_date[1], end_date[2])
    day_to_add = start
    days_delta = (end - start).days
    day_to_add += timedelta(days=1 * random.randint(0, days_delta))
    return day_to_add.strftime("%Y/%m/%d")


if __name__ == "__main__":
    print(random_dates(1, 3, (2020, 6, 19), (2021, 6, 19)))
