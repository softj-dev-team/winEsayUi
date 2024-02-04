import time

import requests
import logging
import os

api_url = os.environ.get("API_URL")


def post(endpoint,params=None, max_retries=3, delay=2):
    for attempt in range(max_retries):
        try:
            # API 엔드포인트 URL 조합
            api_endpoint = api_url + endpoint
            # API 요청 (POST 메소드 사용, JSON 본문 전송)
            response = requests.post(api_endpoint, json=params)
            # 응답 상태 코드가 200 대가 아닐 경우 HTTPError 예외 발생
            response.raise_for_status()
            # 성공적인 응답 처리
            data = response.json()
            return data
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTPError 발생: {http_err}. URL: {endpoint}")
            if attempt < max_retries - 1:
                logging.error(f"{attempt + 1}회 시도 실패. {delay}초 후 재시도합니다...")
                time.sleep(delay)  # 지정된 시간만큼 대기 후 재시도
            else:
                logging.error("최대 재시도 횟수를 초과했습니다. 프로그램을 종료합니다.")
                raise  # 최대 재시도 횟수를 초과한 경우 예외를 다시 발생시켜 호출자에게 알림
        except Exception as e:
            logging.error(f"요청 중 예외 발생: {e}")
            raise  #
def get(endpoint, params=None,max_retries=3, delay=2):
    for attempt in range(max_retries):
        try:
            # API 엔드포인트 URL 조합
            api_endpoint = api_url + endpoint
            # API 요청 (GET 메소드 사용, 파라미터 전달)
            response = requests.get(api_endpoint, params=params)
            # 응답 상태 코드가 200 대가 아닐 경우 HTTPError 예외 발생
            response.raise_for_status()
            # 성공적인 응답 처리 및 JSON 데이터 반환
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTPError 발생: {http_err}. URL: {endpoint}")
            if attempt < max_retries - 1:
                logging.error(f"{attempt + 1}회 시도 실패. {delay}초 후 재시도합니다...")
                time.sleep(delay)  # 지정된 시간만큼 대기 후 재시도
            else:
                logging.error("최대 재시도 횟수를 초과했습니다. 프로그램을 종료합니다.")
                raise  # 최대 재시도 횟수를 초과한 경우 예외를 다시 발생시켜 호출자에게 알림
        except Exception as e:
            logging.error(f"요청 중 예외 발생: {e}")
            raise  #