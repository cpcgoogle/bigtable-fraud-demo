import pandas as pd
from numpy.random import default_rng as rng
import sys

sys.path.insert(1, 'btconfig')
import btconfig as my_bt

def say_hi():
    return "hello from utils"

def return_df():
    return pd.DataFrame(
        rng(0).standard_normal((50, 20)), columns=("col %d" % i for i in range(20)))

def return_transaction_hx(credit_card_number):
    bt = my_bt.my_Bigtable()
    instance = bt.get_instance()
    return instance
