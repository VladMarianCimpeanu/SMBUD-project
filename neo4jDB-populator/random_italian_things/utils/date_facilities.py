import datetime
import random
from datetime import timedelta


def random_dates(max_freq: int, min_freq: int, start_date: tuple, end_date: tuple):
    dates = []
    START = datetime.date(start_date[0], start_date[1], start_date[2])
    END = datetime.date(end_date[0], end_date[1], end_date[2])
    day_to_add = START
    while day_to_add < END:
        day_to_add += timedelta(days=1*random.randint(max_freq, min_freq))
        dates.append(day_to_add)
    return dates


if __name__ == "__main__":
    print(random_dates(1, 3, (2020, 6, 19), (2021, 6, 19)))