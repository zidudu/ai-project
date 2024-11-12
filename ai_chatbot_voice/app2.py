import openai
import boto3
import os
import io
import time
import pygame
import streamlit as st
import base64


# OpenAI API 설정
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Amazon Polly 설정
polly = boto3.client(
    'polly',
    region_name='us-west-2',
    aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"]
)
# 음성을 생성하고 재생하는 함수
def synthesize_and_play(text, voice_id="Seoyeon"):
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat="mp3",
        VoiceId=voice_id
    )

    # 음성 데이터를 메모리에 저장
    audio_stream = io.BytesIO(response['AudioStream'].read())

    # pygame 초기화 및 오디오 로드
    pygame.mixer.init()
    audio_stream.seek(0)  # 스트림의 시작점으로 이동
    pygame.mixer.music.load(audio_stream)
    pygame.mixer.music.play()

    # 오디오 재생이 끝날 때까지 대기
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

# Streamlit 설정
st.set_page_config(page_title="친근한 챗봇", page_icon="🤖")

# 배경 색상 및 스타일 수정
st.markdown(
    """
    <style>
    .stApp {
        background-color: black;
        color: white; /* 텍스트 색상 흰색으로 변경 */
    }
    .user-message {
        background-color: #e6f3ff;
        padding: 10px;
        border-radius: 15px;
        margin-bottom: 10px;
        color: black; /* 사용자 메시지 텍스트 색상은 검정으로 유지 */
    }
    .bot-message {
        background-color: #f0f0f0;
        padding: 10px;
        border-radius: 15px;
        margin-bottom: 10px;
        color: black; /* 봇 메시지 텍스트 색상은 검정으로 유지 */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("친근한 챗봇")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

system_message = '''
너의 이름은 나제.
너는 항상 존댓말을 하는 챗봇이야. 그리고 언제나 친근하게 대답해줘. 
영어로 질문을 받아도 무조건 한글로 답변해줘.
한글이 아닌 답변일 때 다시 생각해서 꼭 한글로 만들어줘
모든 답변 끝에는 답변에 맞는 이모티콘도 추가해줘.
그리고 언제나 질문도 하나씩 해줘. 질문할때도 존댓말로 말해줘
'''

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_message}]

# 사용자 입력 받기
prompt = st.chat_input("무엇을 도와드릴까요?")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Assistant 응답 생성
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        with st.spinner("나제가 생각 중입니다..."):
            response = openai.ChatCompletion.create(
                model=st.session_state["openai_model"],
                messages=st.session_state.messages,
                max_tokens=500,
                temperature=st.session_state.get("temperature", 1.0),
                top_p=st.session_state.get("top_p", 0.1),
                stream=True,
            )
            for chunk in response:
                if 'choices' in chunk and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if 'content' in delta:
                        full_response += delta['content']
                        message_placeholder.markdown(f'<div class="bot-message">{full_response}</div>', unsafe_allow_html=True)

        message_placeholder.markdown(f'<div class="bot-message">{full_response}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # AI 응답을 음성으로 출력
    synthesize_and_play(full_response)

# 모든 메시지 표시 (중복 방지)
for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">{message["content"]}</div>', unsafe_allow_html=True)

# 설정 및 옵션
with st.sidebar:
    st.title("설정")
    st.session_state["openai_model"] = st.selectbox("모델 선택", ["gpt-3.5-turbo", "gpt-4"])
    st.session_state["temperature"] = st.slider("창의성 조절", 0.0, 1.0, 1.0)
    st.session_state["top_p"] = st.slider("다양성 조절", 0.0, 1.0, 0.1)

    if st.button("대화 내용 다운로드"):
        chat_content = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[1:]])
        st.download_button("대화 내용 다운로드", chat_content, "chat_history.txt")
