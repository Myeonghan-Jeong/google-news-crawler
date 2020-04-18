import pandas as pd
import os

if 'articles_ko.csv' in os.listdir('.\\'):
    df = pd.read_csv('.\\articles_ko.csv', encoding='utf-8', sep=',')
    df.date = pd.to_datetime(df.date)
    df.sort_values(by=['target', 'date'], inplace=True)
    df.set_index('date', inplace=True)
    df.to_csv('.\\articles_ko.csv', encoding='utf-8', sep=',')
