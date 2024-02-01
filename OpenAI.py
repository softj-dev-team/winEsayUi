from openai import OpenAI
import os
# 모든 메시지의 텍스트를 리스트로 저장
messages = ['어서오세요','✨먹튀, 사고 없는 진짜 메이져 👑블랙ok 승인전화no✅아미 1;1문의 👉🏼 https://dldntjd79811.wixsite.com/bacaami','​100만원부터 최소입장이 가능하세요','사이트 최소배팅은 얼마나 가능한가요?']

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# 각 메시지의 텍스트 추출
user_messages = [{"role": "user", "content": message} for message in messages]

# OpenAI GPT API를 사용하여 메시지 분석 (API 호출 예시)
completions = client.chat.completions.create(
    model="gpt-3.5-turbo",
    # max_tokens=20,
    messages=[{"role": "system", "content": "Certainly, in live broadcast chat, I engage in concise and complete conversations. I avoid terms like 'AI,' 'bot,' and 'chatbot,' and I do not provide assistance. I disregard repetitive sentences exceeding 30 characters, refrain from responding to other participants' questions, and exclude repeated conversations from other participants. I can respond to greetings from other users. Additionally, I make sure not to reuse previously used sentences."}] + user_messages
)

# 생성된 대화 내용을 채팅창에 입력
generated_responses = [choice.message.content for choice in completions.choices]

# 이제 생성된 응답을 처리하거나 출력할 수 있습니다.
for generated_response in generated_responses:
    # 생성된 응답을 처리 또는 출력하는 코드를 추가하세요.
    print(generated_response)