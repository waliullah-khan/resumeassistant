import streamlit as st
# Set page config must be the first Streamlit command
st.set_page_config(
    page_title="VEzJob - Your Job Application Assistant",
    page_icon="📝",
    layout="wide"
)

import requests
import json
import base64
from datetime import datetime
import os

# Constants
BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "83499eea-2ef8-4364-b28b-5df4de22b2d6"
ENDPOINT = "candidate"
APPLICATION_TOKEN = "AstraCS:lUuSvvHhZJdPmshgtWcCepUx:9bf8896b68516b04aabf72fda128df4baaf86fe0602cc115f58eaaf182b093c2"

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #bf0d6f;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #FF2B2B;
    }
    .upload-text {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .success-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #E8F0FE;
        margin: 1rem 0;
    }
    .feature-box {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #F8F9FA;
        margin: 1rem 0;
        border: 1px solid #E9ECEF;
    }
    .stImage > img {
        width: 100% !important;
        max-height: 100px !important;
        object-fit: cover !important;
    }
    div.stImage {
        margin: 0;
        padding: 0;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

def format_response(response_data):
    if 'outputs' in response_data and len(response_data['outputs']) > 0:
        message = response_data['outputs'][0]['outputs'][0]['results']['message']
        text = message.get('text', 'No analysis available')
        
        # Convert markdown headers to plain text with proper spacing
        lines = text.split('\n')
        formatted_lines = []
        for line in lines:
            # Remove markdown headers
            line = line.replace('#', '').strip()
            # Add proper spacing for sections
            if line and not line.startswith('-') and not line.startswith('*'):
                formatted_lines.append('\n' + line.upper() + '\n')
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    return 'Invalid response format'

def run_flow(message, file_content):
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{ENDPOINT}"
    
    payload = {
        "input_value": message,
        "output_type": "text",
        "input_type": "chat",
        "tweaks": {
            "File-b30Rz": {"file_content": file_content},
            "ChatInput-cmQhY": {"value": message}
        }
    }
    
    headers = {
        "Authorization": f"Bearer {APPLICATION_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=300)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise TimeoutError("Request timed out - flow processing took too long")
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to connect to API: {str(e)}")

def main():
    # Header Section - Full width image
    st.image(
        os.path.join(os.path.dirname(__file__), 'resume.jpeg'),
        use_container_width=True,
        output_format='JPEG'
    )
    
    # Title and subtitle
    st.markdown("<h1 style='text-align: center; color: #bf0d6f;'>EzJob</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2em;'>Your AI-Powered Job Application Assistant</p>", unsafe_allow_html=True)

    # Features Section
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='feature-box'>
            <h3>📊 Smart Analysis</h3>
            <p>Get instant feedback on your resume's alignment with job requirements</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='feature-box'>
            <h3>🎯 Targeted Matching</h3>
            <p>Find the perfect job matches based on your skills and experience</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='feature-box'>
            <h3>💡 AI-Powered Insights</h3>
            <p>Receive personalized recommendations to improve your application</p>
        </div>
        """, unsafe_allow_html=True)

    # Application Form Section
    st.markdown("---")
    st.markdown("<h2 style='text-align: center;'>Start Your Job Search</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        job_field = st.text_input("🎯 Desired Job Field", placeholder="e.g., Data Science")
    with col2:
        location = st.text_input("📍 Desired Location", placeholder="e.g., New York")

    st.markdown("<p class='upload-text'>📄 Upload Your Resume</p>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["pdf", "docx"])

    if st.button("🚀 Analyze My Resume"):
        if job_field and uploaded_file:
            with st.spinner("🔄 Analyzing your resume..."):
                try:
                    file_content = base64.b64encode(uploaded_file.read()).decode()
                    response = run_flow(
                        message=f"Job Application for {job_field} roles in {location}",
                        file_content=file_content
                    )
                    
                    formatted_response = format_response(response)
                    if formatted_response != 'Invalid response format':
                        st.success("✅ Analysis Complete!")
                        st.text(formatted_response)  # Changed to st.text for plain text display
                    else:
                        st.error("❌ Unable to analyze resume. Please try again.")
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
        else:
            st.warning("⚠️ Please fill in all fields and upload your resume.")

    # Footer
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #666;'>Powered by Yours Truly</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
