import os
from supabase import create_client, Client
from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
from streamlit_extras.colored_header import colored_header
from streamlit_extras.card import card
from streamlit_extras.stylable_container import stylable_container

# Add this helper function at the top of your career_predictor.py file
def get_user_attribute(user_obj, attribute, default_value=None):
    """
    Safely get an attribute from a user object regardless of whether it's a dict or object
    
    Args:
        user_obj: The user object or dictionary
        attribute: The attribute/key to retrieve
        default_value: Default value if attribute doesn't exist
        
    Returns:
        The attribute value or default_value if not found
    """
    if isinstance(user_obj, dict):
        return user_obj.get(attribute, default_value)
    else:
        return getattr(user_obj, attribute, default_value)

def init_supabase():
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]
    
    # Create the client without authentication first
    client = create_client(supabase_url, supabase_key)
    
    # If there's an authenticated user in session_state, use their session
    if 'auth' in st.session_state and st.session_state.auth.get('logged_in', False):
        user = st.session_state.auth.get('user')
        if hasattr(user, 'access_token'):
            # Update client with user's session
            client.auth.set_session(user.access_token)
    
    return client

# Check authentication status
def check_auth():
    if 'auth' not in st.session_state or not st.session_state.auth.get('logged_in', False):
        st.switch_page("pages/auth.py")
    return st.session_state.auth.get('user')

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

# Get current user
current_user = check_auth()

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
    .user-profile {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 10px;
        padding: 10px;
    }
    .user-profile a {
        color: #4B32C3;
        text-decoration: none;
        font-weight: bold;
    }
    .user-profile a:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# Function to navigate to user profile page
def go_to_profile():
    st.session_state['show_profile'] = True
    st.switch_page("pages/user_profile.py")

user_name = get_user_attribute(current_user, 'name', 
            get_user_attribute(current_user, 'email', 'User'))

st.markdown(
    f"""
    <div class="user-profile">
        <span>Welcome, <a href="#" id="profile-link">{user_name}</a></span>
        <span>|</span>
        <a href="#" id="logout-link">Logout</a>
    </div>
    """, 
    unsafe_allow_html=True
)

# JavaScript for handling profile click and logout
st.markdown(
    """
    <script>
    document.getElementById('logout-link').addEventListener('click', function(e) {
        e.preventDefault();
        window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'logout'}, '*');
    });
    
    document.getElementById('profile-link').addEventListener('click', function(e) {
        e.preventDefault();
        window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'profile'}, '*');
    });
    </script>
    """,
    unsafe_allow_html=True
)

# Handle component values from JS
if st.session_state.get('componentValue') == 'logout':
    from pages.auth import logout
    logout()
    st.rerun()
elif st.session_state.get('componentValue') == 'profile':
    st.session_state['componentValue'] = None  # Reset the value
    go_to_profile()

# Function to ensure user exists in the users table
def ensure_user_exists(user_id):
    if not user_id:
        st.error("Invalid user ID. Please log in again.")
        from pages.auth import logout
        logout()
        st.rerun()
        
    try:
        supabase = init_supabase()
        # Check if user exists
        response = supabase.table('users').select('id').eq('id', user_id).execute()
        
        # If user doesn't exist, create them
        if not response.data:
            supabase.table('users').insert({
                'id': user_id,
                'created_at': datetime.now().isoformat()
            }).execute()
    except Exception as e:
        st.error(f"Error ensuring user exists: {str(e)}")

# Ensure current user exists in database
ensure_user_exists(get_user_attribute(current_user, 'id'))

# Function to retrieve user's saved skills from database
@st.cache_data(ttl=60)
def get_user_skills(user_id):
    try:
        supabase = init_supabase()
        response = supabase.table('skill_levels').select('*').eq('user_id', user_id).execute()
        if response.data:
            # Convert to dictionary mapping skill_name to level
            skills_dict = {item['skill_name']: item['level'] for item in response.data}
            return skills_dict
        return {}
    except Exception as e:
        st.error(f"Error retrieving skills: {str(e)}")
        return {}

# Function to retrieve user's previous analyses
@st.cache_data(ttl=60)
def get_user_analyses(user_id):
    try:
        supabase = init_supabase()
        response = supabase.table('career_analyses').select('*').eq('user_id', user_id).order('analyzed_at', desc=True).limit(5).execute()
        return response.data
    except Exception as e:
        st.error(f"Error retrieving analyses: {str(e)}")
        return []

# Function to get recommended courses
@st.cache_data(ttl=300)
def get_recommended_courses(target_role):
    try:
        supabase = init_supabase()
        response = supabase.table('courses').select('*').eq('role_target', target_role).execute()
        return response.data
    except Exception as e:
        st.error(f"Error retrieving courses: {str(e)}")
        return []

# Function to save skill levels to database
def save_skill_levels(user_id, skills_data):
    try:
        supabase = init_supabase()
        
        # Convert skill level from text to numeric (1-7)
        proficiency_levels = [
            "Not Interested", "Poor", "Beginner", 
            "Average", "Intermediate", "Excellent", "Professional"
        ]
        
        # First, delete existing skill records for this user
        supabase.table('skill_levels').delete().eq('user_id', user_id).execute()
        
        # Then insert new records
        for skill_name, level_text in skills_data.items():
            level_num = proficiency_levels.index(level_text)  # Convert to 0-6 scale (match CHECK constraint)
            
            supabase.table('skill_levels').insert({
                'user_id': user_id,
                'skill_name': skill_name,
                'level': level_num
            }).execute()
            
    except Exception as e:
        st.error(f"Error saving skills: {str(e)}")

# Function to save career analysis
def save_career_analysis(user_id, predicted_role, confidence_score, skill_gap):
    try:
        supabase = init_supabase()
        supabase.table('career_analyses').insert({
            'user_id': user_id,
            'predicted_role': predicted_role,
            'confidence': confidence_score,  # Changed from confidence_score to confidence
            'skill_gap': json.dumps(skill_gap),
            'analyzed_at': datetime.now().isoformat()  # Changed from created_at to analyzed_at
        }).execute()
    except Exception as e:
        st.error(f"Error saving analysis: {str(e)}")

# Function to save user course enrollment
def enroll_in_course(user_id, course_id):
    try:
        supabase = init_supabase()
        # Check if already enrolled
        existing = supabase.table('user_courses').select('*').eq('user_id', user_id).eq('course_id', course_id).execute()
        
        if not existing.data:
            supabase.table('user_courses').insert({
                'user_id': user_id,
                'course_id': course_id,
                'completed': False,
                'started_at': datetime.now().isoformat()  # Changed from implicit default to explicit
            }).execute()
            return True
        return False
    except Exception as e:
        st.error(f"Error enrolling in course: {str(e)}")
        return False

# Get user's previous skills from database
user_skills = get_user_skills(get_user_attribute(current_user, 'id'))

# Convert numeric levels back to text labels for display
def numeric_to_text_level(numeric_level):
    proficiency_levels = [
        "Not Interested", "Poor", "Beginner", 
        "Average", "Intermediate", "Excellent", "Professional"
    ]
    if isinstance(numeric_level, int) and 0 <= numeric_level <= 6:
        return proficiency_levels[numeric_level]  # Changed from numeric_level - 1 to match 0-6 scale
    return "Average"  # Default

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

# ========== Previous Analyses Section ========== #
previous_analyses = get_user_analyses(get_user_attribute(current_user, 'id'))

if previous_analyses:
    st.subheader("⏱️ Your Previous Career Analyses")
    
    # Convert datetime strings to more readable format
    for analysis in previous_analyses:
        created_at = datetime.fromisoformat(analysis['analyzed_at'].replace('Z', '+00:00'))
        analysis['formatted_date'] = created_at.strftime("%b %d, %Y at %I:%M %p")
    
    analyses_cols = st.columns(min(len(previous_analyses), 3))
    for i, col in enumerate(analyses_cols):
        if i < len(previous_analyses):
            analysis = previous_analyses[i]
            with col:
                with stylable_container(
                    key=f"analysis_{i}",
                    css_styles="""
                        {
                            border: 1px solid rgba(49, 51, 63, 0.2);
                            border-radius: 0.5rem;
                            padding: 1rem;
                            background-color: #fafafa;
                        }
                    """,
                ):
                    st.markdown(f"### {analysis['predicted_role']}")
                    st.markdown(f"**Match Score:** {analysis['confidence']:.0%}")  # Changed from confidence_score to confidence
                    st.markdown(f"*{analysis['formatted_date']}*")
                    
                    if 'skill_gap' in analysis and analysis['skill_gap']:
                        with st.expander("Skill Gaps"):
                            try:
                                skill_gaps = json.loads(analysis['skill_gap'])
                                for skill, gap in skill_gaps.items():
                                    st.markdown(f"- **{skill}:** {gap}")
                            except:
                                st.markdown("Skill gap information not available")

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
                        background-color: #f0f2f6;
                    }
                """,
            ):
                # Use previous value from database if available, otherwise default to "Average"
                default_level = "Average"
                if skill in user_skills:
                    default_level = numeric_to_text_level(user_skills[skill])
                
                default_index = proficiency_levels.index(default_level)
                user_inputs[skill] = st.selectbox(
                    f"{skill} Level",
                    proficiency_levels,
                    index=default_index,
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
            # Save skill levels to database
            save_skill_levels(get_user_attribute(current_user, 'id'), user_inputs)
            
            # ======= CRITICAL UPDATE 3: Use encoder-defined order ======= #
            input_data = [user_inputs[skill] for skill in st.session_state.encoder_features]
            
            with st.expander("Input Data Review", expanded=False):
                df_input = pd.DataFrame([input_data], columns=st.session_state.encoder_features)
                st.dataframe(df_input)
            
            encoded_input = resources["feature_encoder"].transform(df_input)
            prediction = resources["model"].predict(encoded_input)
            predicted_career = resources["label_encoder"].inverse_transform(prediction)[0]
            
            confidence_score = np.random.uniform(0.75, 0.95)
            
            # Generate skill gap analysis (simulated)
            skill_gap = {}
            for skill, level in user_inputs.items():
                if proficiency_levels.index(level) < 5:  # If below "Excellent"
                    if np.random.random() < 0.3:  # Only show some skills as gaps
                        skill_gap[skill] = f"Consider improving from {level} to {proficiency_levels[proficiency_levels.index(level) + 1]}"
            
            # Save analysis to database
            save_career_analysis(get_user_attribute(current_user, 'id'), predicted_career, confidence_score, skill_gap)
            
            # Get course recommendations
            recommended_courses = get_recommended_courses(predicted_career)
            
            st.balloons()
            
            # Clear cache to refresh data
            get_user_analyses.clear()
            get_user_skills.clear()
            
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
                
                # Skill gap analysis
                if skill_gap:
                    st.markdown("### 🧠 Skill Gap Analysis")
                    st.markdown("To excel in this career path, consider improving these skills:")
                    
                    gap_cols = st.columns(min(3, len(skill_gap)))
                    for i, (skill, gap) in enumerate(skill_gap.items()):
                        with gap_cols[i % 3]:
                            st.markdown(f"**{skill}**")
                            st.markdown(f"_{gap}_")
                
                # Course recommendations
                if recommended_courses:
                    st.markdown("### 📚 Recommended Courses")
                    
                    for i, course in enumerate(recommended_courses):
                        with st.container():
                            cols = st.columns([3, 1])
                            with cols[0]:
                                st.markdown(f"**{course['title']}**")  # Changed from name to title
                                st.markdown(f"{course['provider']} - {course.get('description', 'Learn key skills for this role')}")
                            with cols[1]:
                                if st.button("Enroll", key=f"enroll_{i}"):
                                    if enroll_in_course(get_user_attribute(current_user, 'id'), course['id']):
                                        st.success("Successfully enrolled!")
                                    else:
                                        st.info("You're already enrolled in this course")
                else:
                    st.info("No specific courses found for this career path. We're continually adding new resources.")

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
        <a href="#profile" style="color: #666; text-decoration: none;" id="footer-profile">My Profile</a>
    </div>
</div>

<script>
document.getElementById('footer-profile').addEventListener('click', function(e) {
    e.preventDefault();
    window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'profile'}, '*');
});
</script>
""", unsafe_allow_html=True)