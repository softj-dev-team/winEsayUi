import time
import logging
import random
import re
import os
import requests
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from openai import OpenAI

# 로깅 설정
# logging.basicConfig(filename='youtube_search.log', level=logging.DEBUG, format='%(asctime)s - %(message)s')
logging.basicConfig(level=logging.DEBUG)

def setup_driver():
    edge_options = EdgeOptions()
    edge_options.add_argument("--log-level=DEBUG")
    edge_options.add_argument("disable-blink-features=AutomationControlled")
    edge_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    edge_options.add_experimental_option('useAutomationExtension', False)

    edge_service = EdgeService(EdgeChromiumDriverManager().install())
    return webdriver.Edge(service=edge_service, options=edge_options)

def fetch_google_account_info(api_endpoint):
    response = requests.get(api_endpoint)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error("Google account API 요청 실패")
        return None

def login_youtube(driver, email, password):
    try:
        youtube_login_url = "https://accounts.google.com/ServiceLogin?service=youtube"
        driver.get(youtube_login_url)

        username_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "identifierId")))
        username_input.send_keys(email)
        username_input.send_keys(Keys.ENTER)
        time.sleep(5)

        password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "Passwd")))
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)
        time.sleep(3)

        logging.info("YouTube 로그인 성공")
    except Exception as e:
        logging.error(f"로그인 중 오류 발생: {e}")

def search_video(driver, query):
    try:
        search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'search_query')))
        search_box.click()
        search_box.send_keys(query)
        search_box.send_keys(Keys.ENTER)
        time.sleep(2)
    except Exception as e:
        logging.error(f"비디오 검색 중 오류 발생: {e}")

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)
def handle_chat(driver, client):
    try:
        # iframe으로 전환
        WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "chatframe")))

        # 채팅 입력 필드 찾기
        chat_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable]"))
        )

        # 메시지 요소 찾기
        message_elements = driver.find_elements(By.XPATH,
                                                "//yt-live-chat-text-message-renderer[@class='style-scope yt-live-chat-item-list-renderer']/div[@id='content']/span[@id='message']")
        # 모든 메시지의 텍스트를 리스트로 저장
        messages = [element.text for element in message_elements]

        # 메시지를 그룹으로 나누어 보낼 수량 설정
        batch_size = 5

        # 메시지를 배치로 나누어서 처리
        for i in range(0, len(messages), batch_size):
            batch_messages = messages[i:i + batch_size]
            user_messages = [{"role": "user", "content": message} for message in batch_messages]

            # OpenAI GPT API를 사용하여 메시지 분석
            completions = client.chat.completions.create(
                model="gpt-3.5-turbo",
                max_tokens=20,
                messages=[{"role": "system",
                           "content": "Certainly, in live broadcast chat, I engage in concise and complete conversations..."}] + user_messages
            )

            # 생성된 대화 내용을 채팅창에 입력
            generated_responses = [choice.message.content for choice in completions.choices]
            for generated_response in generated_responses:
                print(generated_response)
                time.sleep(12)
                chat_input.send_keys(generated_response)
                chat_input.send_keys(Keys.ENTER)

        # 원래 컨텍스트로 복귀
        driver.switch_to.default_content()

    except TimeoutException:
        print("요소를 찾는 데 시간이 초과되었습니다.")
    except NoSuchElementException:
        print("요소를 찾을 수 없습니다.")



def main():
    driver = setup_driver()

    account_info = fetch_google_account_info("https://esaydroid.softj.net/api/google-account")
    if account_info:
        login_youtube(driver, account_info['email'], account_info['password'])

    search_query = account_info.get('keyword', '') if account_info else ''
    search_video(driver, search_query)

    page_limit = 15
    current_page = 0
    found = False

    while not found and current_page < page_limit:
        try:

            current_page += 1
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            break

    driver.close()

if __name__ == "__main__":
    main()
