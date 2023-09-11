from datetime import date
from hashlib import sha512
from time import time


# from work_with_db import db


def gen_pass(password):
    password = sha512("".join([password, "Eva"]).encode()).hexdigest()
    return password


def time_test(function):
    def wrapper(*args, **kwargs):
        t = time()
        result = function(*args, **kwargs)
        print(f"time: {time() - t}")
        return result

    return wrapper


# c4361038349ba1adbb2e70f72fc8b050f99912f55713c130c33e37c00a6ce4b23633d3274c6d723acb9d269fbafa2b55ac21635737de0ec95e4f4f9e5cbe3bb1
print(gen_pass("boba"))


# макс Maleckiy 77366286
# Бакуменко Полина Bacumenko 63056392
# Гончаров Дмитрий Goncharov 39977827

@time_test
def funk():
    return ''.join(['hello' for _ in range(1_000_000_00)])


# funk()


print(1 < 3 < 3)
