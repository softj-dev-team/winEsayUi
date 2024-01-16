from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()

driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

# 유튜브 접속
driver.get("https://www.youtube.com")

# 이후 원하는 작업을 수행하세요
# 예를 들어, 검색어 입력과 검색 버튼 클릭 등