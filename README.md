# Google News Crawler Demo

## 0. 시작하기 전에

1. `pip`를 이용해 `requirements.txt`의 라이브러리를 전부 설치하세요.

```bash
$ pip install -r requirements.txt
```

2. 본인의 컴퓨터에 설치된 chrome 버전에 맞는 `chromedriver.exe`를 다운로드 받아 본 폴더에 넣어주세요.

   - 링크는 [다음](https://chromedriver.chromium.org/downloads)과 같습니다.

## 1. 파일 설명

1. `.gitignore`: Git으로 관리하기 전에 올리지말아야 할 파일들을 관리하는 공간입니다. Mac에도 대응되어 있습니다.

2. `news_crawler.py`: crawling을 진행하는 파일입니다.

   - 해당 파일의 결과는 `csv` 파일로 저장됩니다.

3. `sample.py`: 연습용 코드가 존재했던 곳으로 무시해도 됩니다.

## 2. How to crawling

1. `news_crawler.py`에 `''' some message '''` 형식으로 강조된 부분을 읽어주세요.

2. CLI 환경에서 `news_crawler.py`를 싱행해주세요.

```bash
$ python news_crawler.py
```

## 주의사항

- 시간이 매우 오래 걸릴 수도 있는 코드입니다. 이에 유의하세요.
