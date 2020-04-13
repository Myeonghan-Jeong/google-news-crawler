from selenium.webdriver.support import ui, expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from datetime import datetime
from random import randint
from tqdm import tqdm
import pandas as pd
import time
import sys

options = webdriver.ChromeOptions()
options.add_argument('headless')  # headless 설정
options.add_argument('window-size=1920x1080')
options.add_argument('lang=ko_KR')  # 이 아래들은 headless 탐지 방지용
options.add_argument(
    'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36')

driver = webdriver.Chrome('.\\chromedriver.exe', options=options)
driver.implicitly_wait(10)


def get_top_companies(target='ko'):
    global driver

    if target == 'ko':
        stock_url = 'https://finance.naver.com/sise/sise_market_sum.nhn?sosok=0'
    elif target == 'us':
        stock_url = 'https://www.nasdaq.com/market-activity/quotes/nasdaq-ndx-index'

    driver.get(stock_url)
    time.sleep(randint(10, 20))

    companies = []
    if target == 'ko':
        titles = driver.find_elements_by_css_selector('a.tltle')
        for title in titles:
            if len(companies) == 30:
                break
            if title.text == '삼성전자우':
                continue
            companies.append(title.text)
    elif target == 'us':
        titles = driver.find_elements_by_css_selector(
            'td.nasdaq-ndx-index__cell--0')
        titles = [title.text for title in titles]
        caps = driver.find_elements_by_css_selector(
            'td.nasdaq-ndx-index__cell--1')
        caps = [int(''.join(cap.text.split(','))) for cap in caps]

        infos = sorted(list(zip(titles, caps)), key=lambda x: -x[1])
        companies = []
        for company, _ in infos[:30]:
            name = company.split(' ')
            print()
            command = input(
                f'{name} 중 몇 번째 block까지 회사 이름인지 확인해주세요.(제일 첫 번째가 1번): ')
            ckpt = name[int(command)]
            if ckpt.endswith(','):
                name[int(command)] = ckpt[:len(ckpt) - 1]
            companies.append(' '.join(name[:int(command)]))

    for c in range(len(companies)):
        print()
        command = input(f'{companies[c]}(은)는 올바른 회사명이 맞습니까?(y/n): ')
        if command != 'n':
            new = input('→ 올바른 회사명을 입력해주세요.: ')
            companies[c] = new

    driver.close()
    return companies


def make_news_urls(q, year=None, start=None, end=None):
    today = list(map(int, datetime.today().strftime('%Y-%m-%d').split('-')))
    year, start, end = year or today[0] - 1, start or today[1], end or today[1]

    urls = {}
    for m in range(start, end + 1):
        if m in [1, 3, 5, 7, 8, 10, 12]:
            day_range = range(1, 32)
        elif m in [4, 6, 9, 11]:
            day_range = range(1, 31)
        else:
            day_range = range(1, 29)

        for d in day_range:
            if year >= today[0] and m >= today[1] and d >= today[2]:
                return urls
            sy, sm, sd = str(year), str(m), str(d)
            date = sy + '-' + sm + '-' + sd
            news_url = f'https://www.google.com/search?q=intitle:{q}&tbm=nws&tbs=cdr:1'
            duration = f',cd_min:{sm}.{sd}.{sy},cd_max:{sm}.{sd}.{sy}'
            news_url += duration + '&num=100'
            urls[date + '|' + q] = news_url

    return urls


urls = {}
# companies = get_top_companies()

companies = [
    '삼성전자', 'SK하이닉스', '삼성바이오로직스', 'NAVER', '셀트리온', 'LG화학', '현대차', 'LG생활건강', '삼성SDI', '삼성물산',
    '현대모비스', 'SK텔레콤', '엔씨소프트', 'POSCO', '카카오', '신한금융지주', 'KB금융지주', '한국전력', '삼성SDS', '기아차',
    'SK', 'KT&G', 'LG', '아모레퍼시픽', 'SK이노베이션', 'LG전자', '삼성생명', '삼성화재', '넷마블', 'S-Oil'
]  # KOSPI

# companies = [
#     'Microsoft', 'Apple', 'Amazon.com', 'Alphabet', 'Facebook', 'Intel', 'PepsiCo', 'Cisco Systems', 'Comcast', 'NVIDIA',
#     'Netflix,', 'Adobe', 'Costco Wholesale', 'Amgen', 'PayPal', 'ASML', 'Charter Communications', 'T-Mobile', 'Broadcom', 'Texas Instruments',
#     'Tesla', 'Gilead Sciences', 'Starbucks', 'QUALCOMM', 'Mondelez International', 'Fiserv', 'Vertex Pharmaceuticals', 'Intuit', 'JD.com', 'Intuitive Surgical'
# ]  # NASDAQ

'''
하단의 year의 range 시작점과 끝점 모두 2015 ~ 2019 중 하나로 바꿔주세요.
'''
for company in companies:
    for year in range(2020, 2020 + 1):
        urls.update(make_news_urls(q=company, year=year, start=1, end=12))


def get_news(url, company):
    global driver

    driver.get(url)
    time.sleep(randint(10, 20))

    recaptcha = driver.find_element_by_css_selector('div.g-recaptcha')
    if len(recaptcha) > 0:
        driver.close()
        print('CRAWLING IS BLOCKED. PLEASE WAIT 600SEC.')
        return None

    contents_urls = driver.find_elements_by_css_selector('a.l.lLrAF')
    contents_news = driver.find_elements_by_css_selector('div.gG0TJc')

    news = []
    for c in contents_news:
        names = c.find_elements_by_css_selector('span.xQ82C.e8fRJf')
        for name in names:
            news.append(name.text)

    urls = []
    for u in contents_urls:
        urls.append(u.get_attribute('href'))

    titles = []
    for t in contents_urls:
        titles.append(t.text)

    data = [news, titles, urls, [company] * len(news)]
    columns = ['news', 'title', 'url', 'company']
    df = pd.DataFrame(data).T
    df.columns = columns

    driver.close()
    return df


# 추후에 적당한 신문사들 선정하기
def filter_company(df):
    companies = []
    df = df[df['company'].isin(companies)]
    return df


def add_date_column(df, date):
    dates = []
    for d in range(len(df.index)):
        dates.append(date)
    df.insert(0, 'date', dates)
    return df


start = datetime.now()
print('시작 시간:', start.strftime('%Y-%m-%d %p %I:%M:%S'))

bp = 0
idx, articles = 0, []
urls = list(urls.items())
while idx < len(urls):
    date_info, url = urls[idx]
    date, company = date_info.split('|')

    print('Crawling:', idx, '/', len(urls), '회사:', company, 'URL:', url)
    news_df = get_news(url, company)
    if type(news_df) == type(None):
        for _ in tqdm(range(600)):
            time.sleep(1)
    else:
        df = add_date_column(news_df, date)
        articles.append(df)
        idx += 1

print('총 걸린 시간:', datetime.now() - start)
driver.close()

# 데이터 확인
print('수집된 기사 전체 갯수:', len(articles))
res = pd.concat(articles)
s = pd.Series(range(len(res)), dtype='int32')
res.set_index([s], inplace=True)

# 저장 파일 이름 국가에 따라 변경하기
res.to_csv('.\\articles_ko.csv', encoding='CP949', sep=',')  # KOSPI
# res.to_csv('.\\articles_us.csv', encoding='utf-8', sep=',')  # NASDAQ
