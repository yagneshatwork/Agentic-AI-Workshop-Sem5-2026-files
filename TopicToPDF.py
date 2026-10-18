import streamlit as st
from langchain_groq import ChatGroq
from fpdf import FPDF

st.title("AI Study Guide")

# Initialize LLM
llm = ChatGroq(
    model="openai/gpt-oss-120b", 
    api_key="Your API Key"
)

# User Inputs
year = st.text_input("Year")
branch = st.text_input("Branch")
subject = st.text_input("Subject")
topic = st.text_input("Topic")

# Helper function to generate PDF
def create_pdf(text_content):
    pdf = FPDF()
    pdf.add_page()
    
    # Document Header
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(0, 8, f"{subject} - {topic} ({year}, {branch})", ln=True)
    pdf.ln(4)
    
    # Process text line by line
    # Convert special characters to simple ASCII to avoid encoding errors
    clean_text = text_content.encode("latin-1", "replace").decode("latin-1")
    
    for line in clean_text.split("\n"):
        line = line.strip().replace("**", "")
        
        # Check if line is a Heading or Bullet point
        if line.startswith("#"):
            pdf.set_font("Arial", style="B", size=11)
            pdf.multi_cell(0, 6, line.lstrip("#").strip())
        elif line.startswith(("-", "*")):
            pdf.set_font("Arial", style="", size=10)
            pdf.multi_cell(0, 6, f"- {line[1:].strip()}")
        elif line:
            pdf.set_font("Arial", style="", size=10)
            pdf.multi_cell(0, 6, line)
            
    return bytes(pdf.output())

# Button to generate output
if st.button("Generate") and all([year, branch, subject, topic]):
    prompt = f"Provide clear study notes for Year: {year}, Branch: {branch}, Subject: {subject}, Topic: {topic}."
    
    with st.spinner("Generating..."):
        response = llm.invoke(prompt)
        st.session_state["notes"] = response.content

# Display output and download button
if "notes" in st.session_state:
    st.write(st.session_state["notes"])
    
    pdf_bytes = create_pdf(st.session_state["notes"])
    st.download_button(
        label="Download PDF",
        data=pdf_bytes,
        file_name=f"{subject}_{topic}.pdf",
        mime="application/pdf"
    )