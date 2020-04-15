from datetime import datetime, timedelta
from selenium import webdriver
from tqdm import tqdm
import pandas as pd
import time
import sys
import os

options = webdriver.ChromeOptions()
options.add_argument('headless')  # 수면시 주석 처리
options.add_argument('window-size=1920x1080')
options.add_argument('lang=ko_KR')
options.add_argument(
    'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36')

driver = webdriver.Chrome('.\\chromedriver.exe', options=options)


# KOSPI 및 NASDAQ 시가총액 30위 회사 수집
def get_top_companies(target='ko'):
    global driver

    if target == 'ko':
        stock_url = 'https://finance.naver.com/sise/sise_market_sum.nhn?sosok=0'
    elif target == 'us':
        stock_url = 'https://www.nasdaq.com/market-activity/quotes/nasdaq-ndx-index'

    driver.get(stock_url)
    driver.implicitly_wait(5)

    companies = []
    if target == 'ko':
        titles = driver.find_elements_by_css_selector('a.tltle')
        for title in titles:
            if len(companies) == 30:
                break
            if title.text != '삼성전자우':
                companies.append(title.text)
    elif target == 'us':
        titles = []
        for title in driver.find_elements_by_css_selector('td.nasdaq-ndx-index__cell--0'):
            titles.append(title.text)

        caps = []
        for cap in driver.find_elements_by_css_selector('td.nasdaq-ndx-index__cell--1'):
            caps.append(int(''.join(cap.text.split(','))))

        infos = sorted(list(zip(titles, caps)), key=lambda x: -x[1])
        for company, _ in infos:
            if len(companies) == 30:
                break
            companies.append(company)

    for c in range(len(companies)):
        print()
        cmd = input(f'{companies[c]}(은)는 찾는 회사입니까(y/n): ')
        if cmd == 'n':
            new = input('→ 올바른 이름을 입력해주세요: ')
            companies[c] = new

    return companies


# 뉴스 수집할 링크 생성기
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
            news_url = f'https://www.google.com/search?q=intitle:{q}&biw=1005&bih=842&source=lnt&tbs=cdr%3A1'
            duration = f'%2Ccd_min%3A{sm}%2F{sd}%2F{sy}%2Ccd_max%3A{sm}%2F{sd}%2F{sy}'
            news_url += duration + '&tbm=nws'
            urls[date + '|' + q] = news_url

    return urls


urls = {}
# companies = get_top_companies()

''' 하단의 두 회사 리스트 중 원하는 회사 리스트 하나를 선택해주세요. '''
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

''' 하단의 year의 range 시작점과 끝점 모두 2015 ~ 2019 중 하나로 바꿔주세요. '''
for company in companies:
    for year in range(2020, 2020 + 1):
        urls.update(make_news_urls(q=company, year=year, start=1, end=12))

# 수집이 필요없는 경우 필터링, 로직 작성 필요
is_exist = 'articles_ko.csv' in os.listdir('.\\')
if is_exist == True:
    df = pd.read_csv('.\\articles_ko.csv', encoding='utf-8', sep=',')
    date = list(df.date.drop_duplicates())[-1]
    targets = list(df.target.drop_duplicates())
    date = datetime.strptime(date, '%Y-%m-%d').date()

    keys = list(urls.keys())
    for key in keys:
        for target in targets:
            date_ = datetime.strptime(key.split('|')[0], '%Y-%m-%d').date()
            target_ = key.split('|')[-1]
            if date_ <= date and target_ == target:
                del urls[key]


# 뉴스 정보 1페이지 수집
def get_news(url, company):
    global driver

    driver.get(url)
    # driver.implicitly_wait(5)  # 비수면시
    time.sleep(30)  # 수면시

    recaptcha = driver.find_elements_by_css_selector('div.g-recaptcha')
    if len(recaptcha) > 0:
        print('CRAWLING IS BLOCKED. PLEASE SOLVE reCAPTCHA.')
        return None

    contents_urls = driver.find_elements_by_css_selector('a.l.lLrAF')
    contents_stations = driver.find_elements_by_css_selector('div.gG0TJc')

    stations = []
    for s in contents_stations:
        names = s.find_elements_by_css_selector('span.xQ82C.e8fRJf')
        for name in names:
            stations.append(name.text)

    urls = []
    for u in contents_urls:
        urls.append(u.get_attribute('href'))

    titles = []
    for t in contents_urls:
        titles.append(t.text)

    data = [stations, titles, urls, [company] * len(stations)]
    columns = ['station', 'title', 'url', 'target']
    df = pd.DataFrame(data).T
    df.columns = columns

    return df


# 신문사 필터링, 추후 적당한 신문사들 선정하기
def filter_company(df):
    companies = []
    df = df[df['company'].isin(companies)]
    return df


# 날짜 column 추가
def add_date_column(df, date):
    dates = []
    for d in range(len(df.index)):
        dates.append(date)
    df.insert(0, 'date', dates)
    return df


# 데이터 수집
start = datetime.now()
print('시작 시간:', start.strftime('%Y-%m-%d %p %I:%M:%S'))

bp = 0
idx, articles = 0, []
urls = list(urls.items())
while idx < len(urls):
    date_info, url = urls[idx]
    date, company = date_info.split('|')

    print('진행도:', idx + 1, '/', len(urls), '회사:', company, 'URL:', url)
    news_df = get_news(url, company)
    if type(news_df) == type(None):
        # if input('SOLVED?(y/n): ') == 'n':  # 비수면시
        #     if input('WAIT?(y/n): ') == 'y':
        #         for _ in tqdm(range(900)):
        #             time.sleep(1)
        #     else:
        #         break
        for _ in tqdm(range(900)):  # 수면시
            time.sleep(1)
    else:
        df = add_date_column(news_df, date)
        articles.append(df)
        idx += 1
        time.sleep(30)
    if datetime.now() - start >= timedelta(hours=7):
        break

print('총 걸린 시간:', datetime.now() - start)
driver.quit()

# 데이터 확인
print('수집된 기사 전체 갯수:', len(articles))
articles = pd.concat(articles)

print('=== COLLECTED ARTICLES ===')
print(articles)

# 기존 데이터와 합치기
if is_exist == True:
    res = pd.read_csv('.\\articles_ko.csv', encoding='utf-8', sep=',')
    res = res.append(articles)
    res.set_index('date', inplace=True)
else:
    res = articles.set_index('date')

''' 하단의 두 파일 중 본인이 위에서 주석을 해제한 국가에 맞는 이름으로 저장해주세요. '''
res.to_csv('.\\articles_ko.csv', encoding='utf-8', sep=',')  # KOSPI
# res.to_csv('.\\articles_us.csv', encoding='utf-8', sep=',')  # NASDAQ
