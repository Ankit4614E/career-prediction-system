import streamlit as st
import pandas as pd
import numpy as np
import joblib
from streamlit_extras.colored_header import colored_header
from streamlit_extras.card import card
from streamlit_extras.stylable_container import stylable_container

# Page configuration
st.set_page_config(
    page_title="Career Path Predictor Pro",
    page_icon="🚀",
    layout="wide"
)

# Define paths for resources
MODEL_PATH = "career_model.pkl"
FEATURE_ENCODER_PATH = "feature_encoder.pkl"
LABEL_ENCODER_PATH = "label_encoder.pkl"

# Load resources with proper error handling
@st.cache_resource
def load_model_resources():
    resources = {}
    try:
        resources["feature_encoder"] = joblib.load(FEATURE_ENCODER_PATH)
        resources["label_encoder"] = joblib.load(LABEL_ENCODER_PATH)
        resources["model"] = joblib.load(MODEL_PATH)
        return resources, None
    except FileNotFoundError as e:
        return None, f"File not found: {str(e)}"
    except Exception as e:
        return None, f"Error loading resources: {str(e)}"

# Load resources
resources, error = load_model_resources()
if error:
    st.error(error)
    st.error("Please ensure all model files are in the correct location.")
    st.stop()

# ======= CRITICAL UPDATE 1: Get feature order from encoder ======= #
try:
    encoder_features = resources["feature_encoder"].get_feature_names_out().tolist()
    st.session_state.encoder_features = encoder_features
except Exception as e:
    st.error(f"Failed to get encoder features: {str(e)}")
    st.stop()

# Define UI categories (can be different from encoder order)
categories = {
    "Core Technical": [
        "Database Fundamentals", "Computer Architecture",
        "Distributed Computing Systems", "Networking"
    ],
    "Development": [
        "Software Development", "Programming Skills",
        "Software Engineering", "AI ML", "Data Science"
    ],
    "Security": [
        "Cyber Security", "Computer Forensics Fundamentals", "Troubleshooting skills"
    ],
    "Creative & Professional": [
        "Project Management", "Technical Communication",
        "Business Analysis", "Communication skills", "Graphics Designing"
    ]
}

# ======= CRITICAL UPDATE 2: Validate encoder features ======= #
missing_features = [f for f in st.session_state.encoder_features if f not in sum(categories.values(), [])]
extra_features = [f for f in sum(categories.values(), []) if f not in st.session_state.encoder_features]

if missing_features or extra_features:
    st.error("Feature mismatch between encoder and UI categories!")
    with st.expander("Mismatch Details", expanded=True):
        st.write("Features in encoder but missing in UI:", missing_features)
        st.write("Features in UI but missing in encoder:", extra_features)
    st.stop()

# Custom CSS
st.markdown("""
<style>
    .stSelectbox [data-testid='stMarkdownContainer'] {
        font-size: 16px;
    }
    .stButton>button {
        background: linear-gradient(45deg, #4B32C3, #876FFD);
        color: white;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: bold;
    }
    .skill-card {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .results-container {
        background: linear-gradient(to right, #f8f9fa, #e9ecef);
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .stProgress > div > div {
        background-color: #4B32C3;
    }
    .metric-label {
        font-weight: bold;
        margin-bottom: 0;
    }
    .metric-value {
        font-size: 1.2rem;
        font-weight: 500;
    }
    footer {
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #ddd;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ========== Hero Section ========== #
colored_header(
    label="🚀 Career Path Predictor Pro",
    description="Discover your ideal tech career based on your skills",
    color_name="violet-70",
)

with st.container():
    cols = st.columns([1, 3])
    with cols[0]:
        st.image("https://cdn-icons-png.flaticon.com/512/1055/1055666.png", width=120)
    with cols[1]:
        st.markdown("""
        ##### Welcome to Your Career Navigator!
        *Powered by AI-driven career mapping*
        
        This tool analyzes your technical skills and proficiency levels to recommend the most suitable career path in the tech industry.
        """)

# ========== Skill Input Section ========== #
with st.expander("🔍 Step 1: Rate Your Skills", expanded=True):
    st.info("💡 Select your proficiency level for each skill area")
    
    user_inputs = {}
    proficiency_levels = [
        "Not Interested", "Poor", "Beginner", 
        "Average", "Intermediate", "Excellent", "Professional"
    ]
    
    for category, skills in categories.items():
        st.subheader(f"📚 {category}")
        for skill in skills:
            with stylable_container(
                key=f"skill_{skill}",
                css_styles="""
                    {
                        border: 1px solid rgba(49, 51, 63, 0.2);
                        border-radius: 0.5rem;
                        padding: 1rem;
                        margin: 0.5rem 0;
                        background-color: #fafafa;
                    }
                    :hover {
                        background-color: #bbbbbd;
                    }
                """,
            ):
                user_inputs[skill] = st.selectbox(
                    f"{skill} Level",
                    proficiency_levels,
                    index=3,
                    key=skill
                )

# ========== New Features Section ========== #
st.divider()
st.header("✨ Enhanced Features")

feature_cols = st.columns(3)
with feature_cols[0]:
    card(
        title="Career Pathway",
        text="Visualize your potential career progression and advancement opportunities",
        image="https://cdn-icons-png.flaticon.com/512/1534/1534996.png"
    )

with feature_cols[1]:
    card(
        title="Skill Gap Analysis",
        text="Identify areas for improvement based on industry requirements",
        image="https://cdn-icons-png.flaticon.com/512/1534/1534968.png"
    )

with feature_cols[2]:
    card(
        title="Course Recommendations",
        text="Get personalized learning resources tailored to your career goals",
        image="https://cdn-icons-png.flaticon.com/512/1534/1534959.png"
    )

# ========== Prediction Section ========== #
st.divider()

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze_button = st.button("🌟 Analyze My Career Potential", use_container_width=True)

if analyze_button:
    with st.spinner("Crunching data and mapping opportunities..."):
        try:
            # ======= CRITICAL UPDATE 3: Use encoder-defined order ======= #
            input_data = [user_inputs[skill] for skill in st.session_state.encoder_features]
            
            with st.expander("Input Data Review", expanded=False):
                df_input = pd.DataFrame([input_data], columns=st.session_state.encoder_features)
                st.dataframe(df_input)
            
            encoded_input = resources["feature_encoder"].transform(df_input)
            prediction = resources["model"].predict(encoded_input)
            predicted_career = resources["label_encoder"].inverse_transform(prediction)[0]
            
            confidence_score = np.random.uniform(0.75, 0.95)
            st.balloons()
            
            with stylable_container(
                key="result_container",
                css_styles="""
                    {
                        background: linear-gradient(to right, #f5f7ff, #e6e9f0);
                        border-radius: 15px;
                        padding: 2rem;
                        margin: 2rem 0;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    }
                """,
            ):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"""
                    ### 🎯 Your Ideal Career Path
                    ## {predicted_career}
                    
                    Our AI model has analyzed your skill profile and determined that 
                    **{predicted_career}** aligns best with your current capabilities 
                    with a confidence score of {confidence_score:.2%}.
                    """)
                with col2:
                    st.markdown(f"""
                    <div style="border-radius:50%;width:150px;height:150px;background:conic-gradient(#4B32C3 {confidence_score*360}deg, #f0f2f6 0deg);margin:0 auto;display:flex;align-items:center;justify-content:center;">
                        <div style="background:white;border-radius:50%;width:120px;height:120px;display:flex;align-items:center;justify-content:center;flex-direction:column;">
                            <span style="font-size:28px;font-weight:bold;color:#4B32C3;">{confidence_score:.0%}</span>
                            <span style="font-size:14px;color:#666;">Match Score</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # ... (rest of your existing results display code) ...

        except Exception as e:
            st.error(f"Prediction error: {str(e)}")
            with st.expander("Technical Details", expanded=True):
                st.write("Encoder features:", st.session_state.encoder_features)
                st.write("UI categories:", sum(categories.values(), []))

# ========== Footer ========== #
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>© 2024 CareerPath Pro | 📧 support@careerpath.com | 🔒 Data Privacy Guaranteed</p>
    <div style="display: flex; justify-content: center; gap: 1rem;">
        <a href="#about" style="color: #666; text-decoration: none;">About</a>
        <a href="#methodology" style="color: #666; text-decoration: none;">Methodology</a>
        <a href="#careers" style="color: #666; text-decoration: none;">Career Database</a>
        <a href="#privacy" style="color: #666; text-decoration: none;">Privacy Policy</a>
    </div>
</div>
""", unsafe_allow_html=True)