import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from tools import query_generator

load_dotenv()

st.title('AI Powered Query Generator with CSV Upload')

llm = ChatGroq(model='openai/gpt-oss-120b', temperature=0)

# Check directory exists
folder_path = 'employee_info'
file_names = os.listdir(folder_path) if os.path.exists(folder_path) else []

# Read available dataframes to give LLM full schema awareness
df_schemas = {}
for file in file_names:
    if file.endswith('.csv'):
        file_path = os.path.join(folder_path, file)
        temp_df = pd.read_csv(file_path)
        df_schemas[file] = list(temp_df.columns)

question = st.text_input('Enter your question:')

if st.button("Get Answer"):
    if not question.strip():
        st.warning("Please enter a question before submitting.")
    else:
        # Step 1: LLM routes question to the correct CSV
        router_prompt = f"""You are given available CSV files and their column schema:
{df_schemas}

Analyze the user question and output ONLY the exact filename from the options above that contains the relevant data.
If the question asks for names/details of employees working on projects, identify which file holds project assignments or employee data.

User question: {question}

Return ONLY the filename (e.g., employee_projects.csv or employee_details.csv). Do not add markdown or quotes."""

        router_response = llm.invoke(router_prompt)
        selected_file = router_response.content.strip().replace("`", "").replace("'", "")

        selected_file_path = os.path.join(folder_path, selected_file)

        st.info(f"**Selected File:** `{selected_file_path}`")

        # Step 2: Generate Pandas code & execute
        try:
            generated_code, result = query_generator(selected_file_path, question)

            st.subheader("Generated Pandas Code:")
            st.code(generated_code, language="python")

            st.subheader("Answer:")
            st.write(result)

        except Exception as e:
            st.error(f"Error executing query on `{selected_file_path}`: {e}")