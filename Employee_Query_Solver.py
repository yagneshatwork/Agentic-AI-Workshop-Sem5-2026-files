import streamlit as st
from langchain_groq import ChatGroq 
import pandas as pd
from dotenv import load_dotenv
load_dotenv() 
import os
from tools import query_generator

llm = ChatGroq(model='openai/gpt-oss-120b', temperature=0)

st.title('AI Employee Query Solver with 3 CSV')

file_names = os.listdir('employee_info') 
df1_employee_details = pd.read_csv('employee_info/employee_details.csv')
df2_employee_leaves = pd.read_csv('employee_info/employee_leaves.csv')
df3_employee_projects = pd.read_csv('employee_info/employee_projects.csv')

question = st.text_input("Enter your query:")

if st.button("Get Answer"):
    if question.strip():
        df1_columns = list(df1_employee_details.columns)
        df2_columns = list(df2_employee_leaves.columns)
        df3_columns = list(df3_employee_projects.columns)

        prompt = '''You r given the 3 dataframes about employee 
        with the columns for each dataframe.
        file_names: {}
        df1_columns: {}
        df2_columns: {}
        df3_columns: {}
        
        You r suppose to analyse the user question and generate
        the dataframe name on which a query can be performed 
        according to the user question

        question:{}

        the output should only the dataframe name'''.format(
            file_names, df1_columns, df2_columns, df3_columns, question
        )

        # Step 1: LLM selects the filename
        router_response = llm.invoke(prompt)
        selected_file = router_response.content.strip().replace("`", "")

        # Construct relative path if LLM returns only the file name
        if not selected_file.startswith("employee_info/"):
            selected_file_path = os.path.join("employee_info", selected_file)
        else:
            selected_file_path = selected_file

        st.info(f"**Selected File:** `{selected_file_path}`")

        # Step 2: Execute query generator using the selected file
        try:
            generated_code, result = query_generator(
                selected_file_path, question
            )

            st.subheader("Generated Pandas Code:")
            st.code(generated_code, language="python")

            st.subheader("Answer:")
            st.write(result)

        except Exception as e:
            st.error(f"Error executing query on `{selected_file_path}`: {e}")
        else:
            st.warning("Please enter a question before submitting.")

