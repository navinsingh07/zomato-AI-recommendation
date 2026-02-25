import streamlit as st
import pandas as pd
import os
import sys
from dotenv import load_dotenv

# Add the root directory to sys.path to import from backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.data_service import get_data_service
from backend.groq_service import get_groq_service

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Zomato AI Recommendation",
    page_icon="🍴",
    layout="wide"
)

# Custom CSS for Glassmorphism & Zomato Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    .main {
        background: linear-gradient(to bottom, #0a0a0a 0%, #2d0a0a 100%);
    }

    .stApp {
        background: transparent;
    }

    /* Glass Effect for blocks */
    div[data-testid="stVerticalBlock"] > div:has(div.glass-card) {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(25px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 2rem;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4), 0 0 20px rgba(226, 55, 68, 0.1);
    }

    .main-heading {
        font-size: 3rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 0.2em;
        text-align: center;
        background: linear-gradient(to bottom, #fff, #aaa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    .sub-heading {
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.6);
        text-transform: uppercase;
        letter-spacing: 0.3em;
        text-align: center;
        margin-bottom: 3rem;
    }

    .highlight {
        color: #E23744;
        font-weight: 800;
        text-shadow: 0 0 15px rgba(226, 55, 68, 0.6);
    }

    /* Form Styling */
    .stSelectbox, .stMultiSelect, .stSlider {
        margin-bottom: 1.5rem;
    }

    /* Recommendation Card */
    .rec-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    .rec-name {
        font-size: 1.5rem;
        font-weight: 800;
        color: #E23744;
        margin-bottom: 0.5rem;
    }

    .rating-pill {
        background: #28a745;
        color: white;
        padding: 2px 10px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.9rem;
        display: inline-block;
        margin-bottom: 0.5rem;
    }

    .expert-box {
        background: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #E23744;
        padding: 1rem;
        border-radius: 0 12px 12px 0;
        margin-top: 1rem;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# App Data Initialization
data_svc = get_data_service()
groq_svc = get_groq_service()

# Header
st.markdown('<h1 class="main-heading">ZOMATO AI RECOMMENDATION</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-heading">Find the best picks in <span class="highlight">Bangalore</span></p>', unsafe_allow_html=True)

# Main Form Area
with st.container():
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        locations = data_svc.get_unique_locations()
        location = st.selectbox("Where are you looking for? *", ["Select Location"] + locations)
        
        price_range = st.selectbox("Price Range *", ["Under ₹500", "₹500 - ₹1500", "Above ₹1500"])
        
    with col2:
        cuisines_list = data_svc.get_unique_cuisines()
        selected_cuisines = st.multiselect("Cuisines (optional)", cuisines_list)
        
        min_rating = st.select_slider("Min Rating (optional)", options=["Any", "3.5+", "4.0+", "4.5+"], value="Any")

    submit = st.button("GET EXPERT PICKS ✨", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Logic
if submit:
    if location == "Select Location":
        st.error("Please select a location to proceed.")
    else:
        with st.spinner("Wait, we are finding the best matches for you..."):
            # Prepare preferences
            rating_val = None
            if min_rating != "Any":
                rating_val = float(min_rating.replace("+", ""))
                
            preferences = {
                "location": location,
                "price_range": price_range,
                "cuisines": selected_cuisines if selected_cuisines else None,
                "min_rating": rating_val
            }
            
            # 1. Filter candidates
            candidates = data_svc.filter_restaurants(
                location=location,
                selected_cuisines=selected_cuisines,
                min_rating=rating_val,
                price_range=price_range
            )
            
            if not candidates:
                st.warning("No restaurants found matching your exact criteria. Try broadening your search!")
            else:
                # 2. Get AI recommendations
                result = groq_svc.get_recommendations(preferences, candidates)
                
                if "error" in result:
                    st.error(result["error"])
                else:
                    st.markdown("---")
                    st.markdown(f"### 🎯 Expert Summary\n{result.get('summary', '')}")
                    
                    st.markdown("## Here are the best picks for you")
                    
                    for rec in result.get("recommendations", []):
                        with st.container():
                            st.markdown(f"""
                            <div class="rec-card">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div class="rec-name">{rec['name']}</div>
                                    <div class="rating-pill">★ {rec['rating']}</div>
                                </div>
                                <div style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-bottom: 0.5rem;">
                                    📍 {rec['full_address']}
                                </div>
                                <div style="font-weight: 700; color: white; background: rgba(255,255,255,0.1); padding: 4px 12px; border-radius: 8px; width: fit-content; font-size: 0.8rem; margin-bottom: 1rem;">
                                    {rec['price_for_two']} for two
                                </div>
                                <div class="expert-box">
                                    {rec['recommendation_reason']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

# Footer/Credits
st.markdown("---")
st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.4); font-size: 0.8rem;'>Created with ❤️ by Antigravity AI</p>", unsafe_allow_html=True)
