import pandas as pd
from numpy.random import default_rng as rng
import sys

sys.path.insert(1, 'bt_utils')
import btconfig as my_bt

def say_hi():
    return "hello from utils"

def return_transaction_hx(credit_card_number):
    bt = my_bt.my_Bigtable()
    rows = bt.execute_sql("SELECT * FROM v_transactions where orig_key =" + credit_card_number)
    return rows

def return_transaction_hx_df(credit_card_number):
    rows = return_transaction_hx(credit_card_number)
    df = pd.DataFrame()
    columns = ['credit_card_number','transaction_ts','amount', 'category', 'merchant', 'merchant_lat', 'merchant_lon','transaction_id']
    data_rows = []
    for row in rows:
        row_data = [row[1], row[2],row[3],row[4],row[5],row[6],row[7],row[8]]
        data_rows.append(row_data)
        df = pd.DataFrame(data_rows, columns=columns)
    return df
    

