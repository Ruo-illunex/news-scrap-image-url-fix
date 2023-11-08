import argparse
import time
import os

import pandas as pd
from sqlalchemy import create_engine, text
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as Chrome


USER = 'news'
PASSWORD = 'Illunex123!'
HOST = '220.118.147.58'
PORT = '3300'
DATABASE = 'portal_news_scraper'

engine = create_engine(f'mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}')


def get_image_url_from_daum(driver) -> str:
    image_url = "no image"
    try:
        img_element = driver.find_element(
            By.CLASS_NAME, 'thumb_g_article'
            )

        if img_element:
            image_url = img_element.get_attribute("src")
    except Exception as e:
        # current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # print(f'{current_time}Error Occured:\n{e}')
        pass

    return image_url


def get_image_url_from_naver(driver) -> str:
    image_url = "no image"
    try:
        img_element = driver.find_element(
            By.XPATH, "//span[@class='end_photo_org']//img"
            )

        if img_element:
            image_url = img_element.get_attribute("src")
    except Exception as e:
        # current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # print(f'{current_time}Error Occured:\n{e}')
        pass

    return image_url


def save_to_file(file_name, data_list):
    with open(file_name, 'a') as f:  # 'a'는 파일에 추가(append)하기 위한 모드입니다.
        for url in data_list:
            f.write(url + '\n')


if __name__ == "__main__":

    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    folder_name = current_time.replace(':', '-')
    folder_path = os.path.join('..', 'log', folder_name)
    os.makedirs(folder_path, exist_ok=True)

    parser = argparse.ArgumentParser(description='News Image Scraper')
    parser.add_argument(
        'limit',
        type=int,
        nargs='?',
        default=100,
        help='Limit for number of URLs to process'
        )
    parser.add_argument(
        '-m', '--media',
        type=str,
        default='daum',
        help='Media to search for in URLs'
    )

    args = parser.parse_args()

    limit = args.limit
    media = args.media

    nq = text(
        f"""SELECT * FROM portal_news
WHERE image_url = 'no image' AND url LIKE '%{media}%'
ORDER BY id DESC
LIMIT {limit};
"""
    )

    df = pd.read_sql(nq, engine)
    urls_without_image_url = df['url'].tolist()

    total_cnt = len(urls_without_image_url)
    wrong_cnt = 0
    wrong_urls = []
    urls_still_without_image_url = []

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-PORT=9222")

    driver = webdriver.Chrome(
        service=Chrome(executable_path="/usr/local/bin/chromedriver"),
        options=chrome_options,
    )

    for index, url in enumerate(urls_without_image_url, start=1):

        driver.get(url)
        driver.implicitly_wait(.5)
        img_url = "no image"

        if media == 'daum':
            img_url = get_image_url_from_daum(driver)

        elif media == 'naver':
            img_url = get_image_url_from_naver(driver)

        if img_url != "no image":
            driver.get(img_url)
            wrong_urls.append(url)
            wrong_cnt += 1
        else:
            urls_still_without_image_url.append(url)

        print(f'{index}. image_url : {img_url}')

        # 매 10개의 URL을 처리할 때마다 파일에 결과를 저장
        if index % 10 == 0:
            save_to_file(f'../log/{folder_name}/{media}_wrong_urls.txt', wrong_urls)
            save_to_file(f'../log/{folder_name}/{media}_urls_still_without_image_url.txt', urls_still_without_image_url)

            # 저장 후 리스트를 비워 다음 배치를 준비합니다.
            wrong_urls.clear()
            urls_still_without_image_url.clear()

    # 마지막 배치 처리
    save_to_file(f'../log/{folder_name}/{media}_wrong_urls.txt', wrong_urls)
    save_to_file(f'../log/{folder_name}/{media}_urls_still_without_image_url.txt', urls_still_without_image_url)

    driver.quit()

    print("Done!")
    print("----------------------------------")
    print("------------[Summary]-------------")
    print(f'- 포털 : {media}')
    print(f'- 전체검사건수 : {len(urls_without_image_url)}')
    print(f'- 실제 이미지가 있는데 수집하지 않은 건수 : {wrong_cnt}')
    print(f'- 에러율 : {wrong_cnt/total_cnt*100}%')
    print(f'- 이미지가 없는 기사 건수 : {total_cnt - wrong_cnt}')
    print("----------------------------------")
