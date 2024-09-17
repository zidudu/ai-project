from openai import OpenAI
import streamlit as st

st.title("친근한 챗봇")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

system_message ='''
너의 이름은 나제야.
너는 항상 존댓말을 하는 챗봇이야. 그리고 언제나 친근하게 대답해줘. 
영어로 질문을 받아도 무조건 한글로 답변해줘.
한글이 아닌 답변일 때 다시 생각해서 꼭 한글로 만들어줘
모든 답변 끝에는 답변에 맞는 이모티콘도 추가해줘.
그리고 언제나 질문도 하나씩 해줘. 질문할때도 존댓말로 말해줘

'''
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages = [{"role": "user", "content": system_message}] #role은 시스템이고, content는 시스템 메세지야


for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): #이 부분은 Streamlit에서 사용자와 챗봇 간의 대화를 시각적으로 구분하기 위해 사용됩니다.
        st.markdown(prompt) #사용자가 입력한 텍스트(prompt)를 실제로 화면에 표시하는 역할을 합니다.st.markdown() 함수는 HTML처럼 텍스트를 표현할 수 있게 해주며, 기본적으로 사용자의 메시지를 그대로 출력합니다.

    with st.chat_message("assistant"):
        stream = client.chat.completions.create( #이 코드는 OpenAI API를 호출하는 부분,사용자가 보낸 메시지와 그동안의 대화 기록을 바탕으로 응답을 생성합니다
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]} #m은 리스트의 각 항목을 나타내는 임시 변수입니다. 즉, st.session_state.messages 리스트에 들어있는 각 메시지 항목을 m이라고 부르겠다는 뜻입니다.
                for m in st.session_state.messages
            ],
            temperature=1.0,  # 창의성 정도 조절 (0.0 ~ 1.0)
            top_p=0.1, # 다양한 응답을 생성하는 정도 조절 (0.0 ~ 1.0)
            stream=True,  # 스트리밍 방식으로 응답 받기
        )
        response = st.write_stream(stream) #st.write_stream()은 스트리밍 데이터를 실시간으로 처리해 화면에 바로 출력하는 함수입니다. 이 함수는 st.markdown()과 비슷하게 데이터를 화면에 표시하는 역할을 하지만, 스트리밍 데이터를 처리하는 데 특화되어 있습니다.
    st.session_state.messages.append({"role": "assistant", "content": response})