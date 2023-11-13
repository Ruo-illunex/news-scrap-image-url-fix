import os
import argparse

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as Chrome

from settings import engine, driver_path
from utils import get_current_time, get_image_url_from_daum, get_image_url_from_naver, save_to_file
import query.queries as q


engine = engine


if __name__ == "__main__":

    current_time = get_current_time()

    # 로그를 저장할 폴더를 생성합니다.
    folder_name = current_time.replace(':', '-')
    folder_path = os.path.join('log', folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # cmd line arguments 처리 > start_date, end_date, portal
    parser = argparse.ArgumentParser(description='News Image Scraper')

    parser.add_argument(
        '-s', '--start_date',
        type=str,
        help='Start date to search for in URLs'
    )

    parser.add_argument(
        '-e', '--end_date',
        type=str,
        help='End date to search for in URLs'
    )

    parser.add_argument(
        '-p', '--portal',
        type=str,
        default='daum',
        help='Media(Portal) to search for in URLs'
    )

    args = parser.parse_args()

    start_date = args.start_date
    end_date = args.end_date
    media = args.portal

    # db에서 이미지가 없는 URL을 가져옵니다.
    if start_date and end_date:
        GetDataWithoutImgUrl = q.get_data_with_date_range(
            start_date, end_date, media
            )

    df = pd.read_sql(GetDataWithoutImgUrl, engine)
    id_list = df['id'].tolist()
    urls_without_image_url = df['url'].tolist()

    # 결과에 보여줄 변수들을 초기화합니다.
    total_cnt = len(urls_without_image_url)
    wrong_cnt = 0
    error_cnt = 0
    wrong_urls = {}
    error_urls = {}
    urls_still_without_image_url = {}

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
    for index, (id, url) in enumerate(zip(id_list, urls_without_image_url), 1):

        driver.get(url)
        driver.implicitly_wait(.5)
        img_url = "no image"

        if media == 'daum':
            img_url = get_image_url_from_daum(driver)

        elif media == 'naver':
            img_url = get_image_url_from_naver(driver)

        if img_url != "no image":
            driver.get(img_url)
            # db에 이미지url을 업데이트합니다.
            UpdateImageUrl = q.update_image_url(id, img_url)

            # transaction 처리 > 성공시 wrong_urls에 추가 > 실패시 error_urls에 추가
            try:
                with engine.connect() as conn:
                    conn.execute(UpdateImageUrl)
                wrong_urls[id] = (get_current_time(), url)
                wrong_cnt += 1
            except Exception as e:
                error_urls[id] = (get_current_time(), url)
                print(f'Error Occured:\n{e}')
                error_cnt += 1
                pass
        else:
            urls_still_without_image_url[id] = (get_current_time(), url)

        print(f'{index}. id: {id}, image_url : {img_url}')

        # 매 10개의 URL을 처리할 때마다 파일에 결과를 저장
        if index % 10 == 0:
            save_to_file(
                f'log/{folder_name}/{media}_wrong_urls.txt',
                wrong_urls,
                "UPDATE"
                )

            save_to_file(
                f'log/{folder_name}/{media}_error_urls.txt',
                error_urls,
                "ERROR"
                )

            save_to_file(
                f'log/{folder_name}/{media}_urls_still_without_image_url.txt',
                urls_still_without_image_url,
                "DO NOTHING"
                )

            # 저장 후 리스트를 비워 다음 배치를 준비합니다.
            wrong_urls.clear()
            urls_still_without_image_url.clear()

    # 마지막 배치 처리
    save_to_file(
        f'log/{folder_name}/{media}_wrong_urls.txt',
        wrong_urls,
        "UPDATE"
        )

    save_to_file(
        f'log/{folder_name}/{media}_error_urls.txt',
        error_urls,
        "ERROR"
        )

    save_to_file(
        f'log/{folder_name}/{media}_urls_still_without_image_url.txt',
        urls_still_without_image_url,
        "DO NOTHING"
        )

    driver.quit()

    summary = (
        "Done!\n"
        "----------------------------------\n"
        "------------[Summary]-------------\n"
        f"- 포털 : {media}\n"
        f"- 전체검사건수 : {len(urls_without_image_url)}\n"
        f"- image_url필드 > db 업데이트 건수 : {wrong_cnt}\n"
        f"- 이미지 수집 혹은 db 업데이트 중 에러난 건수 : {error_cnt}\n"
        f"- 에러율 : {wrong_cnt/total_cnt*100}%\n"
        f"- 이미지가 없는 기사 건수 : {total_cnt - wrong_cnt - error_cnt}\n"
        "----------------------------------\n"
    )

    print(summary)

    # 결과 보고서를 파일에 저장합니다.
    with open(f'log/{folder_name}/{media}_summary.txt', 'w') as f:
        f.write(summary)
