from random import randint


def random_phone_number():
    phone_number = "+39"
    for i in range(10):
        phone_number += str(randint(0, 9))
    return phone_number
