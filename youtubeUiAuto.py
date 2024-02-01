import time

import os
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging
import random
import re
import requests
from openai import OpenAI

import chatGpt

# 로깅 설정
# logging.basicConfig(filename='youtube_search.log', level=logging.INFO, format='%(asctime)s - %(message)s')
logging.basicConfig(level=logging.DEBUG)

edge_options = EdgeOptions()
edge_options.add_argument("--log-level=DEBUG")
edge_options.add_argument("disable-blink-features=AutomationControlled")
edge_options.add_experimental_option('excludeSwitches', ['enable-automation'])
edge_options.add_experimental_option('useAutomationExtension', False)

edge_service = EdgeService(EdgeChromiumDriverManager().install())
driver = webdriver.Edge(service=edge_service, options=edge_options)

use_account=True

# API 엔드포인트
api_endpoint = "https://esaydroid.softj.net/api/google-account"

# API 요청
response = requests.get(api_endpoint)
if response.status_code == 200:
    data = response.json()
    google_account_email = data.get('email', '')
    google_account_passwd = data.get('password', '')
    google_table_id = data.get('id', '')
    google_account_level = data.get('level', '')
else:
    print("API 요청 실패")

if use_account :
    # YouTube 로그인 URL
    youtube_login_url = "https://accounts.google.com/ServiceLogin?service=youtube"

    # YouTube에 접속
    driver.get(youtube_login_url)

    # 로그인 요소 찾기
    try:
        # 사용자 이름 입력
        username_input = driver.find_element(By.ID, "identifierId")
        username_input.send_keys(google_account_email)  # 실제 사용자 이름으로 변경
        username_input.send_keys(Keys.ENTER)
        time.sleep(5)  # 페이지 로드 대기

        # 비밀번호 입력
        password_input = driver.find_element(By.NAME, "Passwd")
        password_input.send_keys(google_account_passwd)  # 실제 비밀번호로 변경
        password_input.send_keys(Keys.ENTER)
        time.sleep(3)  # 로그인 후 페이지 로드 대기

        logging.info("YouTube 로그인 성공")
    except Exception as e:
        logging.error(f"로그인 중 오류 발생: {e}")



# YouTube 페이지 열기
driver.get('https://www.youtube.com')

# 페이지 로딩 대기

# time.sleep(random.uniform(60, 300))
# API 엔드포인트
api_endpoint = "https://esaydroid.softj.net/api/search-title-for-admin"

# API 요청
response = requests.get(api_endpoint)
if response.status_code == 200:
    data = response.json()
    search_keyword = data.get('keyword', '')
    search_title = data.get('title', '')
else:
    print("API 요청 실패")
    search_keyword = ''
    search_title=''

# 검색창 요소 찾기
search_box = driver.find_element(By.NAME, 'search_query')

# 검색창 클릭 및 검색어 입력
search_box.click()
# if google_account_level == 100:
#     메니저인경우
# search_box.send_keys(search_title)
# else:
search_box.send_keys(search_keyword)

# 검색 실행
search_box.send_keys(Keys.ENTER)
# 스크립트 종료 전 대기
time.sleep(2)

# 필터 아이콘 요소 찾기

try:
    filter_icon = driver.find_element(By.XPATH, "//button[@aria-label='검색 필터']")
except NoSuchElementException:
    try:
        filter_icon = driver.find_element(By.XPATH, "//button[@aria-label='Search filters']")
    except NoSuchElementException:
        print("검색 필터 아이콘을 찾을 수 없습니다.")
        # 다른 처리 또는 예외 처리 로직을 추가하세요.

# 필터 아이콘을 클릭하기 위해 ActionChains를 사용
if filter_icon:
    action = ActionChains(driver)
    action.click(filter_icon).perform()
    time.sleep(2)
else:
    print("검색 필터 아이콘을 찾을 수 없어 검색 필터를 클릭할 수 없습니다.")
    # 다른 처리 또는 예외 처리 로직을 추가하세요
time.sleep(2)
try:
    # "실시간 검색" 또는 "Search for Live"를 포함하는 CSS 선택자
    css_selector = "div[title*='실시간 검색'], div[title*='Search for Live'] yt-formatted-string"

    # 해당 CSS 선택자로 요소를 찾습니다.
    elements = driver.find_elements(By.CSS_SELECTOR, css_selector)

    # 찾은 요소들 중에서 "실시간" 또는 "Search for Live" 텍스트를 가진 요소를 찾습니다.
    target_element = None
    for element in elements:
        if "실시간" in element.text or "Live" in element.text:
            target_element = element
            break

    # "실시간" 또는 "Search for Live" 요소를 클릭합니다.
    if target_element:
        target_element.click()

    else:
        print("해당 요소를 찾을 수 없습니다.")
        # 요소를 찾지 못했을 경우 예외 발생
        raise Exception("실시간 검색 또는 Search for Live를 찾을 수 없습니다.")

except Exception as e:
    # 예외 처리: 요소를 찾지 못한 경우
    print(f"오류 발생: {e}")
    # 다른 동작을 수행하거나 오류 처리를 할 수 있습니다.


# 첫 번째 검색 결과 영상 클릭 후 30~40초 시청 후 다시검색
# first_video = driver.find_elements(By.TAG_NAME, "ytd-video-renderer")[1]
# first_video.click()
# time.sleep(random.randint(30, 40))

# search_box = driver.find_element(By.NAME, 'search_query')
# search_box.click()
# search_box.send_keys(search_keyword)
# search_box.send_keys(Keys.ENTER)

# 스크립트 종료 전 대기
time.sleep(2)

# 페이지 넘김 제한 설정
page_limit = 15
current_page = 0

# 일치하는 문자열이 있는지 확인하면서 아래로 스크롤
found = False

while not found and current_page < page_limit:
    try:
        videos = driver.find_elements(By.TAG_NAME, "ytd-video-renderer")
        for video in videos:
            title_element = video.find_element(By.ID, "video-title")
            title_text = title_element.get_attribute('title')
            # 특수문자 및 공백 제거 후 소문자로 변환
            title_text_clean = re.sub(r'\W+', '', title_text).lower()
            search_title_clean = re.sub(r'\W+', '', search_title).lower()
            logging.info(f'Comparing video title: {title_text_clean}')

            # search_title_clean의 길이 계산
            keyword_length = len(search_title_clean)

            # title_text_clean을 search_title_clean과 길이를 맞추기 위해 잘라냅니다.
            title_text_clean = title_text_clean[:keyword_length]

            if title_text_clean == search_title_clean:
                time.sleep(random.randint(5, 15))  # 랜덤한 대기 시간
                title_element.click()  # 일치하는 제목을 가진 첫 번째 요소 클릭

                use_chat = True
                if use_chat:
                    chatGpt.handle_chat(driver)
                time.sleep(random.randint(5, 15))  # 랜덤한 대기 시간

                found = True
                break  # 일치하는 제목을 찾으면 내부 루프 탈출

        if found:
            break  # 일치하는 제목을 찾으면 외부 루프도 탈출

        # 스크롤 전 현재 위치 저장
        last_height = driver.execute_script("return window.pageYOffset;")

        # 페이지 끝까지 스크롤
        driver.execute_script("window.scrollBy(0, document.documentElement.clientHeight);")
        time.sleep(random.randint(2, 5))

        # 스크롤 후 위치 확인
        new_height = driver.execute_script("return window.pageYOffset;")
        logging.info(f"Scrolled from {last_height} to {new_height}")

        # 페이지 카운터 증가
        current_page += 1

        if new_height == last_height:
            break  # 더 이상 스크롤되지 않으면 반복 중단

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        break  # 예외 발생 시 루프 탈출

driver.close()