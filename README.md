news-scrap-image-url-fix
# [issue] Daum/Naver 뉴스 수집기: image url 수집 오류건

- 2023-11-07 ~ 진행중

- [As-is] 현재 EffectMall에서 보여주는 "수집된 뉴스기사 중 이미지가 뜨지 않는 건"들이 종종 발생함.

- [To-be] 원본 기사에 이미지가 존재하는 경우에 EffectMall > 뉴스탭에 정상적으로 이미지 썸네일이 함께 보일 수 있도록 DB에 정확한 image url을 파싱해오도록 한다.



---



## [이슈 발생 원인]

### 1. Daum의 경우

1.1. `daum_scraper.py > get_image_url() 함수` 에서 XPATH 경로가 몇몇 페이지에서 다름.

 - 기존 : `//*[@id='mArticle']/div[2]/div[2]/section/figure/p/img`

 - 예외 case : `//*[@id='mArticle']/div[2]/div/section/figure/p/img`

1.2. 셀레니움 드라이버 변수(driver.driver)에서 find_element()함수를 수행시 적합한 XPATH를 찾지 못하면 에러처리가 나기 때문에 `if not img_element:` 라인을 수행하지 않음.

![image](https://github.com/Ruo-illunex/news-scrap-image-url-fix/assets/149987874/10b03a61-9e2d-40d6-8371-4adf26ffa760)



### 2. Naver의 경우

2.1. `util.py > get_common_image_extractor() 함수` 에서 XPATH 경로가 몇몇 기사 페이지에서 적합하지 않은 것으로 판단됨.

2.2. 셀레니움 드라이버 변수(driver.driver)에서 find_element()함수를 수행시 적합한 XPATH를 찾지 못하면 에러처리가 나기 때문에 `if not img_element:` 라인을 수행하지 않음.

![image](https://github.com/Ruo-illunex/news-scrap-image-url-fix/assets/149987874/11233270-f2f3-4e8f-b7e7-4a2b71884d5e)





### 3. 추가 오타발견

 - `daum_scraper.py > daum_search()함수 > line 156` : `meida` 를 `media`로 수정 필요
![image](https://github.com/Ruo-illunex/news-scrap-image-url-fix/assets/149987874/fbbab70a-3e39-4147-876c-23bb30c9c503)

 - `naver_scraper.py > get_detail_page_info() 함수 > line 94` : `meida` 를 `media`로 수정 필요
![image](https://github.com/Ruo-illunex/news-scrap-image-url-fix/assets/149987874/fc782e16-d1d5-4438-ae59-00da4f74486f)



## [세부 업무 내용]

### 1. 개선된 코드로 db에서 image_url 이 'no image'인 가장 최신 레코드 1000건 테스트 결과는 아래와 같음

- Daum 기사 - 테스트 결과
![image](https://github.com/Ruo-illunex/news-scrap-image-url-fix/assets/149987874/e08447eb-8537-4776-8075-59e82d3c7340)

- Naver 기사 - 테스트 결과
![image](https://github.com/Ruo-illunex/news-scrap-image-url-fix/assets/149987874/3cb979dd-ed8e-4f13-aa97-595d353a95fa)


# 프로젝트 구조
```
.
├── README.md
├── log
│   ├── 2023-11-08 18-07-28
│   │   ├── daum_test_result_summary.txt
│   │   ├── daum_urls_still_without_image_url.txt
│   │   └── daum_wrong_urls.txt
│   └── 2023-11-08 18-11-54
│       ├── naver_test_result_summary.txt
│       ├── naver_urls_still_without_image_url.txt
│       └── naver_wrong_urls.txt
├── poetry.lock
├── pyproject.toml
├── secret
│   └── secrets.yaml
└── src
    ├── __pycache__
    │   ├── settings.cpython-310.pyc
    │   └── utils.cpython-310.pyc
    ├── run.py
    ├── settings.py
    └── utils.py

10 directories, 23 files
```

# 실행
src/경로에서 아래 cmd 입력
```
python run.py [검사할 url 개수:int] [포털명: daum or naver]
```
