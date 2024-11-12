import openai
import boto3
import io
import streamlit as st

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
def synthesize_speech(text, voice_id="Seoyeon"):
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat="mp3",
        VoiceId=voice_id
    )

    # 음성 데이터를 메모리에 저장
    audio_stream = io.BytesIO(response['AudioStream'].read())
    audio_stream.seek(0)  # 스트림의 시작점으로 이동
    return audio_stream

st.title("친근한 챗봇")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

# 사용자 입력 받기
prompt = st.text_input("무엇을 도와드릴까요?")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Assistant 응답 생성
    with st.spinner("나제가 생각 중입니다..."):
        response = openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages=st.session_state.messages,
            max_tokens=500,
            temperature=1.0,
            top_p=0.1,
        )
        full_response = response['choices'][0]['message']['content']
        st.session_state.messages.append({"role": "assistant", "content": full_response})

    # 생성된 응답 표시
    st.write("챗봇:", full_response)

    # AI 응답을 음성으로 출력
    audio_stream = synthesize_speech(full_response)
    st.audio(audio_stream, format="audio/mp3")
