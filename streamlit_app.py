import openai
import streamlit as st
import time
import sys
import ast
from openai import OpenAI
import os
import re
from streamlit_markmap import markmap

# Set your Assistant ID here
ASSISTANT_ID = "asst_M87XGtBQDkk428dUOPSCZ0DY"
ASSISTANT_ID_MINDMAP = "asst_58ASNnC1dqft28FsazSqjZH6"

st.set_page_config(page_title="ResearchXtract AI", layout="wide")

# Add a custom title with styling (font, size, background color, padding, etc.)
st.markdown("""
    <div style="
        background-color: #ADD8E6; 
        padding: 10px; 
        border-radius: 10px;
        text-align: center; 
        box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
        ">
        <h1 style='color: #4B4B4B; font-family: Arial, sans-serif; font-weight: bold;'>
            ResearchXtract AI
        </h1>
    </div>
    """, unsafe_allow_html=True)

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

openai.api_key = os.getenv("OPENAI_API_KEY")

#st.write(openai.api_key)

try:
    client = OpenAI(api_key=openai.api_key)
except Exception as e:
    st.error(f"Error initializing OpenAI client: {str(e)}")

st.markdown('<p></p>', unsafe_allow_html=True)
st.markdown('<p></p>', unsafe_allow_html=True)
st.markdown('<p></p>', unsafe_allow_html=True)

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
    try:
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
        progress_bar = st.progress(0)
        status_text = st.empty()

        progress = 0
        max_time = 100  # Maximum progress steps, adjust as needed

        while run.status != "completed":
            # Increment progress step
            progress += 1
            if progress >= max_time:
                progress = max_time - 1  # Keep progress under 100 until completion

            # Update the progress bar and status text
            progress_bar.progress(progress)
            status_text.text(f"Digging in ...")

            # Simulate the check by retrieving the run status again
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

            # Sleep for 1 second between checks
            time.sleep(1)

        progress_bar.progress(100)

        # Store the API result in session state to avoid reruns
        st.session_state.api_result = client.beta.threads.messages.list(thread_id=thread.id).data[0].content[0].text.value
        st.success("Successfully Retrieved The Insights!")
        
        # Run for Mind Map
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": "Apply the instructions given to the assistant",
                    "attachments": [
                        {
                            "file_id": file.id,
                            "tools": [{"type": "code_interpreter"}]
                        }
                    ]
                }
            ]
        )
        run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=ASSISTANT_ID_MINDMAP)
        progress_bar = st.progress(0)
        status_text = st.empty()

        progress = 0
        max_time = 100  # Maximum progress steps, adjust as needed

        while run.status != "completed":
            # Increment progress step
            progress += 1
            if progress >= max_time:
                progress = max_time - 1  # Keep progress under 100 until completion

            # Update the progress bar and status text
            progress_bar.progress(progress)
            status_text.text(f"Generating Mind Map of Uploaded Paper ...")

            # Simulate the check by retrieving the run status again
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

            # Sleep for 1 second between checks
            time.sleep(1)

        progress_bar.progress(100)

        # Get the assistant's response
        message_response = client.beta.threads.messages.list(thread_id=thread.id)
        messages = message_response.data

        # Print the latest message (response)
        latest_message = messages[0]

        st.session_state.api_result_mindmap = latest_message.content[0].text.value

    except Exception as e:
        st.error(f"Error during file processing or API call: {str(e)}")

# If the API result is already available in session state
if st.session_state.api_result is not None and st.session_state.api_result_mindmap is not None:
    try:
        input_str = st.session_state.api_result
        input_str_mindmap = st.session_state.api_result_mindmap
        #st.write(input_str)
        #st.write(input_str_mindmap)
        match = re.search(r"mindmap_data\s*=\s*'''(.*?)'''", input_str_mindmap, re.DOTALL)
        mindmap_data = match.group(1).strip() if match else None

        st.markdown("<hr style='border: 2px solid black;'>", unsafe_allow_html=True)
        st.markdown("""
        <div style="
            background-color: #FFFFE0; 
            padding: 10px; 
            border-radius: 10px;
            text-align: center; 
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
            ">
            <h1 style='color: red; font-family: Arial, sans-serif; font-weight: bold;'>
                MINDMAP
            </h1>
        </div>
        """, unsafe_allow_html=True)

        if mindmap_data:
            markmap(mindmap_data, height=400)
        else:
            st.error("No mindmap data found.")
        st.markdown("<hr style='border: 2px solid black;'>", unsafe_allow_html=True)

        # Parse the API result (already stored) from the session state
        # t_p = re.search(r'top_10_points\s*=\s*"([^"]*)"', input_str, re.DOTALL)
        # top_10_points = t_p.group(1).strip() if t_p else "No data available"

        # t_a = re.search(r'top_achievements\s*=\s*"([^"]*)"', input_str, re.DOTALL)
        # top_achievements = t_a.group(1).strip() if t_a else "No data available"

        # p_r_s = re.search(r'potential_research_ideas\s*=\s*"([^"]*)"', input_str, re.DOTALL)
        # potential_research_ideas = p_r_s.group(1).strip() if p_r_s else "No data available"

        t_p = re.search(r'top_10_points\s*=\s*["\'"]{1,3}(.*?)["\'"]{1,3}', input_str, re.DOTALL)
        top_10_points = t_p.group(1).strip() if t_p else "No data available"

        t_a = re.search(r'top_achievements\s*=\s*["\'"]{1,3}(.*?)["\'"]{1,3}', input_str, re.DOTALL)
        top_achievements = t_a.group(1).strip() if t_a else "No data available"

        p_r_s = re.search(r'potential_research_ideas\s*=\s*["\'"]{1,3}(.*?)["\'"]{1,3}', input_str, re.DOTALL)
        potential_research_ideas = p_r_s.group(1).strip() if p_r_s else "No data available"




        b_c = re.search(r'buttons_content\s*=\s*{(.|\n)*?}', input_str)
        buttons_content = ast.literal_eval(b_c.group(0).split('=', 1)[1].strip()) if b_c else {}

        col1, col2, col3 = st.columns(3)

        # Display the parsed results
        with col1:
            st.markdown(f"""
            <div style="background-color: #F5F5DC; border-radius: 10px; padding: 15px; border: 1px solid #ddd; box-shadow: 2px 2px 12px rgba(0,0,0,0.1);">
                <h3 style="text-align: center; color: red;">Top 10 Insights</h3>
                <ul style="text-align: left; list-style-position: inside;">{top_10_points}</ul>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div style="background-color: #F5F5DC; border-radius: 10px; padding: 15px; border: 1px solid #ddd; box-shadow: 2px 2px 12px rgba(0,0,0,0.1);">
                <h3 style="text-align: center; color: green;">Achievements/Innovations</h3>
                <ul style="text-align: left; list-style-position: inside;">{top_achievements}</ul>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div style="background-color: #F5F5DC; border-radius: 10px; padding: 15px; border: 1px solid #ddd; box-shadow: 2px 2px 12px rgba(0,0,0,0.1);">
                <h3 style="text-align: center; color: blue;">Potential Research Ideas</h3>
                <ul style="text-align: left; list-style-position: inside;">{potential_research_ideas}</ul>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("<hr style='border: 2px solid black;'>", unsafe_allow_html=True)

        # Display buttons and handle interactions
        for key, value in buttons_content.items():
            if key not in st.session_state.button_state:
                st.session_state.button_state[key] = False

            st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: white;
                color: black;
                height: 3em;
                width: 12em;
                border-radius:10px;
                border:3px solid #000000;
                font-size: 20px;
                font-weight: bold;
                margin: auto;
                display: block;
            }

            div.stButton > button:hover {
                background: linear-gradient(to bottom, #ffcccc 5%, #ff9999 100%);
                background-color: #ffcccc;
            }

            div.stButton > button:active {
                position:relative;
                top:3px;
            }
            </style>
            """, unsafe_allow_html=True)

            if st.button(key):
                st.session_state.button_state[key] = not st.session_state.button_state[key]

            if st.session_state.button_state[key]:
                st.write(f"**{key}**")
                for item in value:
                    st.write(f"- {item}")

        st.markdown("<hr style='border: 2px solid black;'>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
