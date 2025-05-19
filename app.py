import streamlit as st
import os
from drive_utils import (
    load_erie_survey_zips,
    load_combined_survey_results,
    load_processed_pantry_data,
    load_geocoded_pantry_data,
    load_pantry_map
)

# Page config
st.set_page_config(
    page_title="SPCA Maps Dashboard",
    page_icon="🐾",
    layout="wide"
)

# Custom CSS for the landing page
st.markdown("""
    <style>
    .project-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .project-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .project-title {
        color: #262730;
        font-size: 1.5em;
        margin-bottom: 10px;
    }
    .project-description {
        color: #666666;
        font-size: 1em;
    }
    </style>
""", unsafe_allow_html=True)

# Authentication
def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        if st.session_state["password"] == "SPCAMaps*":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        return True

# Main content
st.title("SPCA Maps Dashboard")
st.markdown("Welcome to the SPCA Maps Dashboard. Please enter the password to continue.")

if check_password():
    # Create two columns for the project cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="project-card">
                <div class="project-title">SPCA Pet Pantry Reach</div>
                <div class="project-description">
                    Interactive map showing the distribution of pet pantry clients across Erie County.
                    Features include year-over-year analysis and multiple visualization options.
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
            <div class="project-card">
                <div class="project-title">SPCA Vaccine Clinic Reach</div>
                <div class="project-description">
                    Heat map visualization of vaccine clinic attendees, with demographic filters
                    and detailed statistics.
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style='text-align: center; margin-top: 20px;'>
            <p>Select a map from the sidebar to begin exploring the data.</p>
        </div>
    """, unsafe_allow_html=True)

# Load your data
erie_zips = load_erie_survey_zips()
survey_results = load_combined_survey_results()
pantry_data = load_processed_pantry_data()
geocoded_data = load_geocoded_pantry_data()
pantry_map = load_pantry_map() 