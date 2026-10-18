import pandas as pd
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb 
import os

load_dotenv()

llm = ChatGroq(model='openai/gpt-oss-120b', temperature=0)

def query_generator_tool(question):

    df = pd.read_csv('employee_info/employee_details.csv')
    columns = list(df.columns)

    prompt = f"""You are a data analyst writing pandas queries.
    Write Python code to answer this question: "{question}"

    Dataframe variable name: df
    Available columns in this CSV: {columns}
    Sample rows:
    {df.head(2).to_dict(orient='records')}

    Instructions:
    1. ONLY use columns that exist in `Available columns`. Do NOT query columns like 'name' if they are not listed in `Available columns`.
    2. Treat string/integer comparisons flexibly (e.g., convert `project_id` to numeric or string matching: `df['project_id'].astype(str) == '2'`).
    3. Store the final answer in a variable named `result`.
    4. Output ONLY executable Python code. Do NOT wrap in markdown backticks or explanations."""

    response = llm.invoke(prompt)

    # Clean markdown formatting tags
    generated_code = response.content.strip()
    generated_code = generated_code.replace("```python", "").replace("```", "").strip()

    # Pass local scope dictionary so exec() accesses 'df' and outputs 'result'
    local_scope = {"df": df, "pd": pd}

    try:
        exec(generated_code, globals(), local_scope)
        result = local_scope.get("result", "No 'result' variable created by code.")
    except Exception as e:
        result = f"Error executing code: {e}"

    return generated_code, result

def rag_pipeline_tool(question: str, pdf_path: str = "Android-Lollipop-Quick-Start-Guide.pdf"):

    # 1. Read PDF
    reader = PdfReader(pdf_path)
    all_text = ""
    for page in reader.pages:
        all_text = all_text + page.extract_text()

    # 2. Text Splitting
    spliter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200) 
    chunks = spliter.split_text(all_text)

    # 3. ChromaDB setup
    client = chromadb.Client()
    vectordb = client.get_or_create_collection(pdf_path)
    
    # Avoid duplicate additions if collection exists
    if vectordb.count() == 0:
        vectordb.add(documents=chunks, ids=['c' + str(i) for i in range(len(chunks))])

    # 4. Query ChromaDB
    context = vectordb.query(query_texts=[question], n_results=4)

    # 5. Prompting
    prompt = '''you r a assistent that is given a question by the user and some context chunks
    you have to analyze the content(i.e. results) and give a cohesive and suitable answer according 
    to the info provided to you
    question: {}
    context: {}
    Answer Rules: no filler like 'im happy to help u' or other phrases, 
    answer in a concise manner'''.format(question, context["documents"][0][0])

    # 6. LLM Invocation
    response = llm.invoke(prompt)
    return response.content

def select_tool(tool_name):
    tools = {
        "query_generator_tool": query_generator_tool,
        "rag_pipeline_tool": rag_pipeline_tool
    }

    tool_name = llm.invoke(f"Given the user question: '{tool_name}', decide which tool to use: 'query_generator_tool' or 'rag_pipeline_tool'. Return only the tool name.").content.strip()

    return tool_name     
