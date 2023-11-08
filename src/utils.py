import time

from selenium.webdriver.common.by import By


# 현재 시간을 가져오는 함수를 정의합니다.
def get_current_time():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


current_time = get_current_time()


# 이미지 URL을 가져오는 함수를 정의합니다.
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


# 파일에 결과를 저장하는 함수를 정의합니다.
def save_to_file(file_name, data_list):
    with open(file_name, 'a') as f:  # 'a'는 파일에 추가(append)하기 위한 모드입니다.
        for url in data_list:
            f.write(url + '\n')
