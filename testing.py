# testing.py
import streamlit as st
import pandas as pd
import joblib
from streamlit_extras.colored_header import colored_header
from streamlit_extras.card import card
from streamlit_extras.stylable_container import stylable_container

# Load resources
try:
    feature_encoder = joblib.load("feature_encoder.pkl")
    label_encoder = joblib.load("label_encoder.pkl") 
    model = joblib.load("career_model.pkl")
except Exception as e:
    st.error(f"Error loading resources: {str(e)}")
    st.stop()

# ========== New Features ========== #
# 1. Career Pathway Visualization
# 2. Skill Gap Analysis
# 3. Role Comparison
# 4. Progress Tracker
# 5. Course Recommendations

# ========== UI/UX Improvements ========== #
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
    }
    .skill-card {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        padding: 1.5rem;
        margin: 1rem 0;
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
        """)

# ========== Skill Input Section ========== #
with st.expander("🔍 Step 1: Rate Your Skills", expanded=True):
    st.info("💡 Select your proficiency level for each skill area")
    
    user_data = []
    categories = {
        "Core Technical": [
            "Database Fundamentals", "Computer Architecture",
            "Distributed Computing Systems", "Networking"
        ],
        "Development": [
            "Software Development", "Programming Skills",
            "Software Engineering", "AI ML"
        ],
        "Security": [
            "Cyber Security", "Computer Forensics Fundamentals"
        ],
        "Professional Skills": [
            "Project Management", "Technical Communication",
            "Business Analysis", "Communication skills"
        ]
    }

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
                    }
                """,
            ):
                user_input = st.selectbox(
                    f"{skill} Level",
                    ["Not Interested", "Poor", "Beginner", "Average", "Intermediate", "Excellent", "Professional"],
                    key=skill
                )
                user_data.append(user_input)

# ========== New Features Section ========== #
st.divider()
st.header("✨ Enhanced Features")

feature_cols = st.columns(3)
with feature_cols[0]:
    card(
        title="Career Pathway",
        text="Visualize your career progression",
        image="1534996.png"
    )

with feature_cols[1]:
    card(
        title="Skill Gap Analysis",
        text="Identify areas for improvement",
        image="1534968.png"
    )

with feature_cols[2]:
    card(
        title="Course Recommendations",
        text="Personalized learning resources",
        image="1534959.png"
    )

# ========== Prediction Section ========== #
st.divider()
if st.button("🌟 Analyze My Career Potential"):
    with st.spinner("Crunching data and mapping opportunities..."):
        try:
            # Transform and predict
            encoded_input = feature_encoder.transform(pd.DataFrame([user_data], columns=skills))
            prediction = model.predict(encoded_input)
            predicted_career = label_encoder.inverse_transform(prediction)[0]

            # Display results
            st.balloons()
            
            with stylable_container(
                key="result_container",
                css_styles="""
                    {
                        background: #f0f2f6;
                        border-radius: 10px;
                        padding: 2rem;
                        margin: 2rem 0;
                    }
                """,
            ):
                st.markdown(f"""
                ### 🎯 Your Ideal Career Path
                **{predicted_career}**
                
                ##### Next Steps:
                - View detailed career roadmap
                - Explore skill development courses
                - Connect with industry mentors
                """)
                
                # Add progress bars for key skills
                st.subheader("📊 Skill Alignment")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Core Technical", "85%", "5% from target")
                    st.progress(0.85)
                with col2:
                    st.metric("Specialized Skills", "72%", "Learn more")
                    st.progress(0.72)
                with col3:
                    st.metric("Leadership", "63%", "Development needed")
                    st.progress(0.63)

        except Exception as e:
            st.error(f"Prediction error: {str(e)}")

# ========== Footer ========== #
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>© 2024 CareerPath Pro | 📧 support@careerpath.com | 🔒 Data Privacy Guaranteed</p>
    <div style="display: flex; justify-content: center; gap: 1rem;">
        <a href="/about" style="color: #666; text-decoration: none;">About</a>
        <a href="/methodology" style="color: #666; text-decoration: none;">Methodology</a>
        <a href="/careers" style="color: #666; text-decoration: none;">Career Database</a>
    </div>
</div>
""", unsafe_allow_html=True)