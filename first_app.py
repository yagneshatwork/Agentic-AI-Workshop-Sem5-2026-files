import streamlit as st
from langchain_groq import ChatGroq

st.title('AI Powered Medicine Recommendation')

llm = ChatGroq(model='openai/gpt-oss-120b',temperature=2,
api_key = "Your API Key")

symptons = st.text_input('Enter Symptons')

prompt = '''Act like a medical student and suggest medicine to me based on the given symptoms.
symptoms:{}''',format(symptons)

if st.button('Recommend Medicine'):
    
    # Here we will use our LLM to recommend the medicine
    response = llm.invoke(prompt)
    st.write(response.text)
