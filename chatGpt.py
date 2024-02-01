import time

import os
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging

import requests
from openai import OpenAI

logging.basicConfig(level=logging.DEBUG)

edge_options = EdgeOptions()
edge_options.add_argument("--log-level=DEBUG")
edge_options.add_argument("disable-blink-features=AutomationControlled")
edge_options.add_experimental_option('excludeSwitches', ['enable-automation'])
edge_options.add_experimental_option('useAutomationExtension', False)
edge_service = EdgeService(EdgeChromiumDriverManager().install())
driver = webdriver.Edge(service=edge_service, options=edge_options)
def handle_chat(driver, response_threshold=1):
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    last_message_index = 0  # 마지막으로 처리한 메시지의 인덱스
    last_sent_message = None  # 마지막으로 전송한 메시지 저장

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
                    messages=[{"role": "system",
                               "content": "I avoid terms like 'AI', 'bot', and 'chatbot', and do not offer "
                                          "assistance. I ignore repetitive sentences over 30 characters, "
                                          "do not respond to other participants' questions, and exclude their "
                                          "repeated conversations. I can respond to greetings from other users. "
                                          "Additionally, I ensure not to reuse previously used sentences. When "
                                          "introducing myself to others, I am a '메니져'. When answering, "
                                          "the sentence length cannot exceed 100 characters. In conversation, "
                                          "I use concise and complete sentences limited to 50 characters."}] +
                             user_messages
                )

                generated_responses = [choice.message.content for choice in completions.choices]
                for generated_response in generated_responses:
                    if generated_response != last_sent_message:  # 이전에 전송한 메시지와 다른 경우에만 전송
                        WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "div[contenteditable]"))
                        )
                        send_long_text(chat_input, generated_response)
                        time.sleep(2)
                        chat_input.send_keys(Keys.ENTER)
                        last_sent_message = generated_response  # 마지막으로 전송된 메시지 업데이트
                    else:
                        print("Skipping message as it's the same as the last sent message.")

            time.sleep(5)
        driver.switch_to.default_content()

    except TimeoutException:
        print("TimeoutException occurred.")
    except NoSuchElementException:
        print("NoSuchElementException occurred.")

def google_login(driver, response_threshold=1):
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
# driver.get('https://www.youtube.com/watch?v=-j8e0xoH71M')

def send_long_text(element, text, delay=0.1):
    """ 긴 텍스트를 여러 부분으로 나누어 입력하는 함수 """
    for char in text:
        element.send_keys(char)
        time.sleep(delay)

# use_chat = True
# if use_chat:
#     handle_chat(driver)
# time.sleep(random.randint(5, 15))  # 랜덤한 대기 시간
