import streamlit as st
import time
import re
import ast
from openai import OpenAI
import os
# Set your Assistant ID here
ASSISTANT_ID = "asst_M87XGtBQDkk428dUOPSCZ0DY"

api_key_openai = os.getenv("OPENAI_API_KEY") 

# Initialize the OpenAI client with your API key
client = OpenAI(api_key=api_key_openai)

st.set_page_config(page_title="Research Paper Analyzer", layout="wide")

# Title for the app
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Research Paper Analyzer</h1>", unsafe_allow_html=True)

# Button to reset session state on rerun
if st.button("Reset App"):
    st.session_state.clear()

# Initialize session state for tracking API results
if 'api_result' not in st.session_state:
    st.session_state.api_result = None
if 'button_state' not in st.session_state:
    st.session_state.button_state = {}

# File uploader
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

# If the file is uploaded and no API result yet, process the file
if uploaded_file is not None and st.session_state.api_result is None:
    with open("uploaded_pdf.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success("File uploaded successfully!")

    st.write("Sending PDF to the Assistant...")

    # Avoid rerunning API calls by storing results in session state
    file = client.files.create(file=open("uploaded_pdf.pdf", "rb"), purpose="assistants")

    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": "Apply the instructions given to the assistant",
                "attachments": [{"file_id": file.id, "tools": [{"type": "code_interpreter"}]}]
            }
        ]
    )

    run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=ASSISTANT_ID)

    # Wait for the run to complete
    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        time.sleep(1)

    # Store the API result in session state to avoid reruns
    st.session_state.api_result = client.beta.threads.messages.list(thread_id=thread.id).data[0].content[0].text.value
    st.success("Processing Completed!")

# If the API result is already available in session state
if st.session_state.api_result is not None:
    #st.write(st.session_state.api_result)
    input_str = st.session_state.api_result

    # Parse the API result (already stored) from the session state
    t_p = re.search(r'top_10_points\s*=\s*"([^"]*)"', input_str, re.DOTALL)
    top_10_points = t_p.group(1).strip() if t_p else None

    t_a = re.search(r'top_achievements\s*=\s*"([^"]*)"', input_str, re.DOTALL)
    top_achievements = t_a.group(1).strip() if t_a else None

    p_r_s = re.search(r'potential_research_ideas\s*=\s*"([^"]*)"', input_str, re.DOTALL)
    potential_research_ideas = p_r_s.group(1).strip() if p_r_s else None

    b_c = re.search(r'buttons_content\s*=\s*{(.|\n)*?}', input_str)
    buttons_content = ast.literal_eval(b_c.group(0).split('=', 1)[1].strip()) if b_c else {}

    col1, col2, col3 = st.columns(3)

    # Display the parsed results
    with col1:
        st.markdown(f"""
        <div style="background-color: #f9f9f9; border-radius: 10px; padding: 15px; border: 1px solid #ddd; box-shadow: 2px 2px 12px rgba(0,0,0,0.1);">
            <h3 style="text-align: center; color: #4CAF50;">Top 10 Points</h3>
            <ul style="text-align: left; list-style-position: inside;">{top_10_points}</ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background-color: #f9f9f9; border-radius: 10px; padding: 15px; border: 1px solid #ddd; box-shadow: 2px 2px 12px rgba(0,0,0,0.1);">
            <h3 style="text-align: center; color: #4CAF50;">Achievements</h3>
            <ul style="text-align: left; list-style-position: inside;">{top_achievements}</ul>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="background-color: #f9f9f9; border-radius: 10px; padding: 15px; border: 1px solid #ddd; box-shadow: 2px 2px 12px rgba(0,0,0,0.1);">
            <h3 style="text-align: center; color: #4CAF50;">Research Ideas</h3>
            <ul style="text-align: left; list-style-position: inside;">{potential_research_ideas}</ul>
        </div>
        """, unsafe_allow_html=True)

    # Display buttons and handle interactions
    for key, value in buttons_content.items():
        if key not in st.session_state.button_state:
            st.session_state.button_state[key] = False

        if st.button(key):
            st.session_state.button_state[key] = not st.session_state.button_state[key]

        if st.session_state.button_state[key]:
            st.write(f"**{key}**")
            for item in value:
                st.write(f"- {item}")
