import time

import os
import random
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
from openai import OpenAI
import re
import api

logging.basicConfig(level=logging.DEBUG)

edge_options = EdgeOptions()
edge_options.add_argument("--log-level=DEBUG")
edge_options.add_argument("disable-blink-features=AutomationControlled")
edge_options.add_experimental_option('excludeSwitches', ['enable-automation'])
edge_options.add_experimental_option('useAutomationExtension', False)
edge_service = EdgeService(EdgeChromiumDriverManager().install())
driver = webdriver.Edge(service=edge_service, options=edge_options)

def search_filter():
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
def handle_chat(driver, response_threshold=1):
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    last_message_index = 0  # 마지막으로 처리한 메시지의 인덱스
    sent_messages = set()  # 전송된 모든 메시지 저장 (중복 확인용)
    # 사전에 정의된 응답
    predefined_responses = {
        "안녕하세요": "안녕하세요! 어서오세요~",
        "결제": "지금은 시범 운영중입니다. 이용 문의는 텔레그렘 @EsayUiDev 로 해주세요",
        "설치": "지금은 시범 운영중입니다. 이용 문의는 텔레그렘 @EsayUiDev 로 해주세요",
        "이용문의": "지금은 시범 운영중입니다. 이용 문의는 텔레그렘 @EsayUiDev 로 해주세요",
        "문의": "지금은 시범 운영중입니다. 이용 문의는 텔레그렘 @EsayUiDev 로 해주세요",
        # 여기에 더 많은 사전 정의된 응답을 추가할 수 있습니다.
    }

    # 특정 주제에 대한 지식
    topic_knowledge = {
        "챗봇": "챗봇.",
        # 여기에 더 많은 주제에 대한 지식을 추가할 수 있습니다.
    }
    try:
        WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "chatframe")))
        while True:
            chat_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable]"))
            )

            message_elements = driver.find_elements(By.XPATH,
                                                    "//yt-live-chat-text-message-renderer[@class='style-scope yt-live-chat-item-list-renderer']/div[@id='content']/span[@id='message']")
            messages = [element.text for element in message_elements]
            new_messages = messages[last_message_index:]

            if len(new_messages) >= response_threshold:
                last_message_index += len(new_messages)

                user_messages = [{"role": "user", "content": message} for message in new_messages]
                completions = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    max_tokens=100,
                    temperature=0.6,
                    n=1,
                    messages=[{"role": "system", "content": os.environ.get("CONTENT")}] + user_messages
                )

                generated_responses = [choice.message.content for choice in completions.choices]
                for generated_response in generated_responses:

                    # 사전에 정의된 응답이나 주제에 대한 지식을 검사
                    response_to_send = predefined_responses.get(generated_response,
                                                                topic_knowledge.get(generated_response,
                                                                                    generated_response))


                    if generated_response not in sent_messages:  # 이전에 전송하지 않은 메시지만 전송
                        WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "div[contenteditable]"))
                        )
                        # 긴 텍스트를 입력하는 함수 호출
                        send_long_text(chat_input, generated_response, delay=0.1)
                        time.sleep(2)  # 메시지를 모두 입력한 후 잠시 기다림
                        chat_input.send_keys(Keys.ENTER)
                        sent_messages.add(response_to_send)  # 전송된 메시지 저장
                    else:
                        logging.info("Skipping message as it's the same as a previously sent message.")

                time.sleep(5)  # 새 메시지 확인 간의 지연
            else:
                time.sleep(5)  # 채팅 메시지가 없을 경우 대기
        driver.switch_to.default_content()

    except TimeoutException:
        logging.error("TimeoutException occurred.")
    except NoSuchElementException:
        logging.error("NoSuchElementException occurred.")


def google_login():
    global google_table_id
    use_account = True
    # API 요청
    response = api.get('/api/google-account', params=None)
    if 'id' in response:
        google_account_email = response.get('email', '')
        google_account_passwd = response.get('password', '')
        google_table_id = response.get('id', '')
        google_account_level = response.get('level', '')
    else:
        print("API 요청 실패")

    if use_account:
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
            api.post('/api/google-account_result', {"id": google_table_id})
            logging.error(f"로그인 중 오류 발생: {e}")


def send_long_text(element, text, delay=0.1):
    """ 긴 텍스트를 여러 부분으로 나누어 입력하는 함수 """
    for char in text:
        element.send_keys(char)
        time.sleep(delay)


use_chat = True
if use_chat:
    use_google_login = True
    if use_google_login:
        google_login()
        time.sleep(3)
        handle_chat(driver)
