import streamlit as st
from tools import *

if 'messages' not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        st.markdown(msg['message'])

question = st.chat_input('Enter Question')
if question:
    
    st.session_state.messages.append({'role': 'user', 'message': question})
    with st.chat_message('user'):
        st.markdown(question)

    decision = select_tool(question)  # "query_generator_tool", "rag_pipeline_tool"
    if decision == "query_generator_tool":
        answer = query_generator_tool(question)  # ans from tools
    else:
        answer = rag_pipeline_tool(question=question)

    if answer:
        st.session_state.messages.append({'role': 'assistant', 'message': answer})
        with st.chat_message('assistant'):
            st.markdown(answer)