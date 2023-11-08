import os
import argparse

import pandas as pd
from sqlalchemy import text
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as Chrome

from src.settings import engine, driver_path
from src.utils import get_current_time, get_image_url_from_daum, get_image_url_from_naver, save_to_file

engine = engine()


if __name__ == "__main__":

    current_time = get_current_time()

    # 로그를 저장할 폴더를 생성합니다.
    folder_name = current_time.replace(':', '-')
    folder_path = os.path.join('..', 'log', folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # cmd line arguments 처리
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

    # db에서 이미지가 없는 URL을 가져옵니다.
    nq = text(
        f"""SELECT * FROM portal_news
WHERE image_url = 'no image' AND url LIKE '%{media}%'
ORDER BY id DESC
LIMIT {limit};
"""
    )

    df = pd.read_sql(nq, engine)
    urls_without_image_url = df['url'].tolist()

    # 결과에 보여줄 변수들을 초기화합니다.
    total_cnt = len(urls_without_image_url)
    wrong_cnt = 0
    wrong_urls = []
    urls_still_without_image_url = []

    # 크롬 드라이버를 실행합니다.
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-PORT=9222")

    driver = webdriver.Chrome(
        service=Chrome(executable_path=driver_path),
        options=chrome_options,
    )

    # 크롤링을 시작합니다.
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
            save_to_file(
                f'../log/{folder_name}/{media}_wrong_urls.txt',
                wrong_urls
                )
            save_to_file(
                f'../log/{folder_name}/{media}_urls_still_without_image_url.txt',
                urls_still_without_image_url
                )

            # 저장 후 리스트를 비워 다음 배치를 준비합니다.
            wrong_urls.clear()
            urls_still_without_image_url.clear()

    # 마지막 배치 처리
    save_to_file(
        f'../log/{folder_name}/{media}_wrong_urls.txt',
        wrong_urls
        )
    save_to_file(
        f'../log/{folder_name}/{media}_urls_still_without_image_url.txt',
        urls_still_without_image_url
        )

    driver.quit()

    summary = (
        "Done!\n"
        "----------------------------------\n"
        "------------[Summary]-------------\n"
        f"- 포털 : {media}\n"
        f"- 전체검사건수 : {len(urls_without_image_url)}\n"
        f"- 실제 이미지가 있는데 수집하지 않은 건수 : {wrong_cnt}\n"
        f"- 에러율 : {wrong_cnt/total_cnt*100}%\n"
        f"- 이미지가 없는 기사 건수 : {total_cnt - wrong_cnt}\n"
        "----------------------------------\n"
    )

    print(summary)

    # 결과를 파일에 저장합니다.
    save_to_file(
        f'../log/{folder_name}/{media}_test_result_summary.txt',
        [summary]
        )
