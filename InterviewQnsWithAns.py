import streamlit as st
from langchain_groq import ChatGroq

st.title('AI Powered Interview Qns and Answers generator')

llm = ChatGroq(model='openai/gpt-oss-120b',temperature=2,
api_key = "Your API Key")

interview_qns = st.text_input('Enter Interview Questions')

prompt = '''Act like an experienced interviewer and provide detailed answers to the following questions.
Questions:{}''',format(interview_qns)

if st.button('Generate Answers'): 
    
    # Here we will use our LLM to recommend the medicine
    response = llm.invoke(prompt)
    st.write(response.text)
