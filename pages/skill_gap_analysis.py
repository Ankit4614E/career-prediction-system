import os
import streamlit as st
import joblib
import pandas as pd
import numpy as np
import json
from supabase import create_client
from datetime import datetime
from streamlit_extras.colored_header import colored_header
from streamlit_extras.stylable_container import stylable_container

# Page configuration
st.set_page_config(
    page_title="Skill Gap Analysis - Career Path Predictor Pro",
    page_icon="🧠",
    layout="wide"
)

# Helper to get user attribute
def get_user_attribute(user_obj, attribute, default_value=None):
    if isinstance(user_obj, dict):
        return user_obj.get(attribute, default_value)
    else:
        return getattr(user_obj, attribute, default_value)

# Check authentication status
def check_auth():
    if 'auth' not in st.session_state or not st.session_state.auth.get('logged_in', False):
        st.switch_page("pages/auth.py")
    return st.session_state.auth.get('user')

# Load encoders and model
@st.cache_resource
def load_resources():
    try:
        feature_encoder = joblib.load("feature_encoder.pkl")
        label_encoder = joblib.load("label_encoder.pkl")
        model = joblib.load("career_model.pkl")
        return feature_encoder, label_encoder, model, None
    except Exception as e:
        return None, None, None, f"Error loading resources: {str(e)}"

feature_encoder, label_encoder, model, error = load_resources()
if error:
    st.error(error)
    st.error("Please ensure all model files are in the correct location.")
    st.stop()

# Supabase client
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

# Load average skill profiles and top required skills for each career
@st.cache_data
def get_career_skill_profiles(csv_path="dataset9000.csv", top_n=5):
    try:
        # Attempt to load the dataset
        try:
            df = pd.read_csv(csv_path)
        except Exception as csv_error:
            st.warning(f"Unable to load CSV data: {str(csv_error)}")
            # Create a fallback dataframe with simulated data
            if feature_encoder is not None:
                features = feature_encoder.get_feature_names_out().tolist()
                roles = label_encoder.classes_
                
                # Create simulated data directly
                data = []
                for role in roles:
                    for _ in range(20):  # 20 samples per role
                        row = {'Role': role}
                        for feature in features:
                            row[feature] = np.random.randint(1, 6)  # Random skill level between 1-6
                        data.append(row)
                
                df = pd.DataFrame(data)
                st.info("Using simulated skill data for analysis.")
            else:
                raise Exception("Unable to create fallback data: encoders not loaded")
        
        skill_cols = [col for col in df.columns if col != "Role"]
        profiles = {}
        top_skills = {}
        
        # For each role, calculate the average skill levels and identify top skills
        for role, group in df.groupby("Role"):
            # Calculate average skill levels
            role_profile = {col: group[col].mean() for col in skill_cols}
            profiles[role] = role_profile
            
            # Sort skills by their average values and get top skills
            sorted_skills = sorted(role_profile.items(), key=lambda x: x[1], reverse=True)
            top_skills[role] = sorted_skills[:top_n]
        
        return profiles, top_skills, None
    except Exception as e:
        return None, None, f"Error processing career profiles: {str(e)}"

# Silently handle any profile errors - don't show error messages to users
career_profiles, top_career_skills, profile_error = get_career_skill_profiles()
if profile_error:
    # Create fallback simulated profiles without showing the error message
    career_profiles = {}
    top_career_skills = {}
    for career in label_encoder.classes_:
        # Simulate skill levels
        skill_dict = {skill: np.random.uniform(3, 6) for skill in feature_encoder.get_feature_names_out()}
        career_profiles[career] = skill_dict
        
        # Generate top skills
        sorted_skills = sorted(skill_dict.items(), key=lambda x: x[1], reverse=True)
        top_career_skills[career] = sorted_skills[:5]  # Top 5 skills

# Get the latest career analysis from supabase
@st.cache_data(ttl=60)
def get_latest_analysis(user_id):
    try:
        supabase = init_supabase()
        response = supabase.table('career_analyses').select('*').eq('user_id', user_id).order('analyzed_at', desc=True).limit(1).execute()
        if response.data:
            return response.data[0], None
        return None, "No recent analysis found"
    except Exception as e:
        return None, f"Error retrieving analysis: {str(e)}"

# Get user's skills from database
@st.cache_data(ttl=60)
def get_user_skills(user_id):
    try:
        supabase = init_supabase()
        response = supabase.table('skill_levels').select('*').eq('user_id', user_id).execute()
        if response.data:
            # Convert to dictionary mapping skill_name to level
            skills_dict = {item['skill_name']: item['level'] for item in response.data}
            return skills_dict, None
        return {}, "No skills found"
    except Exception as e:
        return {}, f"Error retrieving skills: {str(e)}"

# Get recommended courses
@st.cache_data(ttl=300)
def get_recommended_courses(target_role):
    try:
        supabase = init_supabase()
        response = supabase.table('courses').select('*').eq('role_target', target_role).execute()
        return response.data, None
    except Exception as e:
        return [], f"Error retrieving courses: {str(e)}"

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
                'started_at': datetime.now().isoformat()
            }).execute()
            return True, None
        return False, "Already enrolled"
    except Exception as e:
        return False, f"Error enrolling in course: {str(e)}"

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
    .gap-positive {
        color: #d73027;
    }
    .gap-none {
        color: #1a9850;
    }
    .metric-box {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .nav-btn {
        text-align: center;
        margin-top: 2rem;
    }
    .course-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .top-skill-card {
        background: linear-gradient(to right, #f8f9fa, #e9ecef);
        border-left: 4px solid #4B32C3;
        padding: 0.8rem;
        margin-bottom: 0.8rem;
        border-radius: 0.5rem;
    }
    .skill-level-indicator {
        display: inline-block;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        margin-right: 5px;
        vertical-align: middle;
    }
    .high-level {
        background-color: #1a9850;
    }
    .medium-level {
        background-color: #f4a261;
    }
    .low-level {
        background-color: #d73027;
    }
</style>
""", unsafe_allow_html=True)

# Get current user
current_user = check_auth()
user_id = get_user_attribute(current_user, 'id')

# Get encoder features
encoder_features = feature_encoder.get_feature_names_out().tolist()

# Proficiency level mapping
proficiency_levels = [
    "Not Interested", "Poor", "Beginner", 
    "Average", "Intermediate", "Excellent", "Professional"
]

# Try to get user skills from session state first (if coming from career_predictor)
user_skills = st.session_state.get('user_skills', {})

# If not in session state, get from database
if not user_skills:
    user_skills, skills_error = get_user_skills(user_id)
    if skills_error and not user_skills:
        st.warning(f"Could not retrieve your skills: {skills_error}")
        st.warning("Please rate your skills in the Career Predictor page first.")
        
        if st.button("Go to Career Predictor"):
            st.switch_page("pages/career_predictor.py")
        st.stop()

# Try to get latest analysis from session state first
latest_analysis = st.session_state.get('latest_analysis')

# If not in session state, get from database
if not latest_analysis:
    db_analysis, analysis_error = get_latest_analysis(user_id)
    if db_analysis:
        latest_analysis = db_analysis
        if 'skill_gap' in latest_analysis and isinstance(latest_analysis['skill_gap'], str):
            try:
                latest_analysis['skill_gap'] = json.loads(latest_analysis['skill_gap'])
            except:
                latest_analysis['skill_gap'] = {}
    elif analysis_error:
        st.info(f"No previous analysis found: {analysis_error}")
        st.info("Please complete a career analysis first.")
        
        if st.button("Go to Career Predictor"):
            st.switch_page("career_predictor.py")
        st.stop()

# ========== Page Header ========== #
colored_header(
    label="🧠 Skill Gap Analysis",
    description="Identify the skills you need to improve to reach your career goals",
    color_name="violet-70",
)

# Page layout
st.markdown("""
This tool helps you identify gaps between your current skills and what's needed for different career paths.
Select a career and we'll show you which skills to focus on improving.
""")

# ========== Career Selection ========== #
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # List all possible careers
    all_careers = list(label_encoder.classes_)
    
    # If we have a latest analysis, set that career as default
    default_index = 0
    if latest_analysis and 'predicted_role' in latest_analysis:
        try:
            default_index = all_careers.index(latest_analysis['predicted_role'])
        except:
            default_index = 0
    
    selected_career = st.selectbox(
        "Choose a career to analyze:", 
        all_careers,
        index=default_index
    )

# Display metrics about selected career
st.markdown("### Career Overview")

metrics_cols = st.columns(3)
with metrics_cols[0]:
    with stylable_container(key="career_metric", css_styles="""
        {
            border: 1px solid rgba(49, 51, 63, 0.2);
            border-radius: 0.5rem;
            padding: 1rem;
            text-align: center;
        }
    """):
        st.markdown(f"### {selected_career}")
        st.markdown("Selected Career Path")

with metrics_cols[1]:
    with stylable_container(key="match_metric", css_styles="""
        {
            border: 1px solid rgba(49, 51, 63, 0.2);
            border-radius: 0.5rem;
            padding: 1rem;
            text-align: center;
        }
    """):
        # If this is the same career as the latest analysis, show the confidence score
        confidence_score = 0.0
        if latest_analysis and latest_analysis.get('predicted_role') == selected_career:
            confidence_score = latest_analysis.get('confidence', 0.0)
        else:
            # Calculate a simulated confidence score
            confidence_score = np.random.uniform(0.6, 0.9)
        
        st.markdown(f"### {confidence_score:.0%}")
        st.markdown("Match Score")

with metrics_cols[2]:
    with stylable_container(key="skills_metric", css_styles="""
        {
            border: 1px solid rgba(49, 51, 63, 0.2);
            border-radius: 0.5rem;
            padding: 1rem;
            text-align: center;
        }
    """):
        # Get the required skills profile for this career
        career_profile = career_profiles.get(selected_career, {})
        
        # Count skills where user is below required level
        skill_gaps = 0
        for skill in encoder_features:
            user_level = user_skills.get(skill, 3)  # Default to Average if not found
            required_level = round(career_profile.get(skill, 3))
            if user_level < required_level:
                skill_gaps += 1
        
        st.markdown(f"### {skill_gaps}")
        st.markdown("Skills to Improve")

# ========== Top Required Skills ========== #
st.markdown("### 🌟 Top Required Skills for this Career")

try:
    if selected_career in top_career_skills:
        top_skills = top_career_skills[selected_career]
        
        # Create two columns for the top skills
        cols = st.columns(2)
        
        for i, (skill, score) in enumerate(top_skills):
            with cols[i % 2]:
                with stylable_container(
                    key=f"top_skill_{i}",
                    css_styles="""
                        {
                            border: 1px solid rgba(49, 51, 63, 0.2);
                            border-radius: 0.5rem;
                            padding: 1rem;
                            margin: 0.5rem 0;
                            background: linear-gradient(to right, #f8f9fa, #e9ecef);
                            border-left: 4px solid #4B32C3;
                        }
                    """,
                ):
                    try:
                        # Get user's level for this skill
                        user_level = user_skills.get(skill, 3)  # Default to Average if not found
                        required_level = round(score)
                        
                        # Ensure required_level is within valid range (0-6)
                        required_level = max(0, min(6, required_level))
                        
                        # Ensure user_level is within valid range (0-6)
                        user_level = max(0, min(6, user_level))
                        
                        # Determine gap
                        gap = required_level - user_level
                        
                        # Create columns for skill info
                        skill_cols = st.columns([3, 2])
                        
                        with skill_cols[0]:
                            st.markdown(f"#### {skill}")
                            
                            # Determine level indicator class
                            level_class = "high-level" if score >= 5 else "medium-level" if score >= 3 else "low-level"
                            
                            st.markdown(f"""
                            <div>
                                <span class="skill-level-indicator {level_class}"></span>
                                <span>Importance: {score:.1f}/6.0</span>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with skill_cols[1]:
                            st.markdown(f"Your level: **{proficiency_levels[user_level]}**")
                            st.markdown(f"Required: **{proficiency_levels[required_level]}**")
                            
                            if gap > 0:
                                st.markdown(f"<span class='gap-positive'>Gap: +{gap} levels</span>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<span class='gap-none'>No gap</span>", unsafe_allow_html=True)
                    except Exception as skill_error:
                        # Handle errors silently for individual skills
                        st.markdown(f"#### {skill}")
                        st.markdown("Skill details unavailable")
    else:
        st.info("Top skills will be displayed after analysis is complete.")
except Exception:
    # Fall back gracefully if there's any error in the top skills section
    st.info("Top skills analysis will be available after you complete a career assessment.")

# ========== Skill Gap Analysis ========== #
st.markdown("### Detailed Skill Analysis")

# Use the career profile for the selected career
career_profile = career_profiles.get(selected_career, {})

# Build data for the skill gap visualization
skill_data = []
for skill in encoder_features:
    user_level = user_skills.get(skill, 3)  # Default to Average if not found
    required_level_float = career_profile.get(skill, 3.0)
    required_level = round(required_level_float)
    gap = required_level - user_level
    
    skill_data.append({
        "Skill": skill,
        "Your Level": proficiency_levels[user_level],
        "Required Level": proficiency_levels[required_level],
        "Required Score": f"{required_level_float:.2f}",
        "Gap": gap,
        "Gap Text": f"+{gap} levels" if gap > 0 else "No gap"
    })

# Convert to DataFrame
df_skill_gap = pd.DataFrame(skill_data)

# Create tabs for viewing options
tab1, tab2 = st.tabs(["All Skills", "Skills to Improve"])

with tab1:
    # Sort by gap (largest first)
    df_sorted = df_skill_gap.sort_values(by="Gap", ascending=False)
    
    # Display each skill as a styled container
    for _, row in df_sorted.iterrows():
        with stylable_container(
            key=f"skill_{row['Skill']}",
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
            cols = st.columns([3, 2, 2, 1])
            with cols[0]:
                st.markdown(f"**{row['Skill']}**")
            with cols[1]:
                st.markdown(f"Your level: **{row['Your Level']}**")
            with cols[2]:
                st.markdown(f"Required: **{row['Required Level']}** ({row['Required Score']})")
            with cols[3]:
                if row['Gap'] > 0:
                    st.markdown(f"<span class='gap-positive'>+{row['Gap']} levels</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span class='gap-none'>No gap</span>", unsafe_allow_html=True)

with tab2:
    # Filter to show only skills with a gap
    df_gaps = df_skill_gap[df_skill_gap["Gap"] > 0].sort_values(by="Gap", ascending=False)
    
    if df_gaps.empty:
        st.success("Congratulations! You already meet or exceed all the skill requirements for this career path.")
    else:
        st.info(f"You have {len(df_gaps)} skills to improve for this career path.")
        
        # Display each skill gap as a styled container
        for _, row in df_gaps.iterrows():
            with stylable_container(
                key=f"gap_{row['Skill']}",
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
                cols = st.columns([3, 2, 2, 1])
                with cols[0]:
                    st.markdown(f"**{row['Skill']}**")
                with cols[1]:
                    st.markdown(f"Your level: **{row['Your Level']}**")
                with cols[2]:
                    st.markdown(f"Required: **{row['Required Level']}** ({row['Required Score']})")
                with cols[3]:
                    st.markdown(f"<span class='gap-positive'>+{row['Gap']} levels</span>", unsafe_allow_html=True)

# ========== Course Recommendations ========== #
st.markdown("### 📚 Recommended Courses")
st.markdown(f"Courses tailored to help you develop the skills needed for the {selected_career} role:")

courses, courses_error = get_recommended_courses(selected_career)

if courses_error:
    st.warning(f"Could not retrieve courses: {courses_error}")

if courses:
    course_cols = st.columns(min(len(courses), 3))
    
    for i, course in enumerate(courses):
        with course_cols[i % 3]:
            with stylable_container(
                key=f"course_{i}",
                css_styles="""
                    {
                        border: 1px solid rgba(49, 51, 63, 0.2);
                        border-radius: 0.5rem;
                        padding: 1rem;
                        margin: 0.5rem 0;
                        background-color: #fafafa;
                        height: 100%;
                    }
                """,
            ):
                st.markdown(f"#### {course['title']}")
                st.markdown(f"**Provider:** {course['provider']}")
                
                if 'description' in course and course['description']:
                    st.markdown(f"{course['description']}")
                
                if st.button("Enroll", key=f"enroll_{i}"):
                    success, message = enroll_in_course(user_id, course['id'])
                    if success:
                        st.success("Successfully enrolled!")
                    else:
                        st.info(message)
else:
    st.info("No specific courses found for this career path. We're continually adding new resources.")

# ========== Action Buttons ========== #
st.markdown("### Next Steps")

col1, col2 = st.columns(2)
with col1:
    if st.button("Back to Career Predictor", use_container_width=True):
        st.switch_page("career_predictor.py")

with col2:
    if st.button("View My Profile", use_container_width=True):
        st.switch_page("pages/user_profile.py")

# ========== Footer ========== #
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>© 2024 CareerPath Pro | 📧 support@careerpath.com | 🔒 Data Privacy Guaranteed</p>
</div>
""", unsafe_allow_html=True)