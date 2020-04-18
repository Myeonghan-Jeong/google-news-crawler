import pandas as pd
import os


def is_english(title):
    for t in range(len(title)):
        if title[t] not in '!"#$%&()*+.,-/:;=?@[\]^_`{|}~ \'':
            if not (ord('a') <= ord(title[t]) <= ord('z')):
                if not (ord('A') <= ord(title[t]) <= ord('Z')):
                    if not (ord('0') <= ord(title[t]) <= ord('9')):
                        return False
    return True


if 'articles_ko.csv' in os.listdir('.\\'):
    df = pd.read_csv('.\\articles_ko.csv', encoding='utf-8', sep=',')
    df.date = pd.to_datetime(df.date)
    df.sort_values(by=['target', 'date'], inplace=True)
    df.set_index('date', inplace=True)
    df.to_csv('.\\articles_ko.csv', encoding='utf-8', sep=',')

if 'articles_us.csv' in os.listdir('.\\'):
    # dfs = [df0, df1, df2, df3]  # if splited some articles
    # df = pd.concat(dfs)
    cks = []
    for i in range(len(df)):
        if is_english(df.iloc[i, 2]) == False:
            cks.append(i)

    df.drop(index=df.index[cks], inplace=True)
    df.date = pd.to_datetime(df.date)
    df.sort_values(by=['target', 'date'], inplace=True)
    df.set_index('date', inplace=True)
    df.to_csv('.\\articles_us.csv', encoding='utf-8', sep=',')
