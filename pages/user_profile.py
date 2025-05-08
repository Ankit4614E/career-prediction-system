import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime

# --- Helper functions ---
def init_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

def get_user_attribute(user_obj, attribute, default_value=None):
    if isinstance(user_obj, dict):
        return user_obj.get(attribute, default_value)
    else:
        return getattr(user_obj, attribute, default_value)

def check_auth():
    if 'auth' not in st.session_state or not st.session_state.auth.get('logged_in', False):
        st.switch_page("career_predictor.py")
    return st.session_state.auth.get('user')

# --- Page config ---
st.set_page_config(
    page_title="My Profile - Career Path Predictor Pro",
    page_icon="👤",
    layout="wide"
)

# --- Custom CSS for better UI ---
st.markdown("""
    <style>
    .profile-card {
        background: linear-gradient(90deg, #f5f7fa 60%, #c3cfe2 100%);
        border-radius: 1.2rem;
        padding: 2rem 2.5rem 1.5rem 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 16px rgba(80,80,120,0.07);
    }
    .section-card {
        background: #fff;
        border-radius: 1rem;
        padding: 1.5rem 1.5rem 1rem 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 8px rgba(80,80,120,0.06);
    }
    .back-btn {
        background: linear-gradient(90deg, #4B32C3 60%, #876FFD 100%);
        color: #fff !important;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 1.5rem;
        cursor: pointer;
    }
    .back-btn:hover {
        background: linear-gradient(90deg, #876FFD 60%, #4B32C3 100%);
        color: #fff !important;
    }
    .profile-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #4B32C3;
        margin-bottom: 0.5rem;
    }
    .profile-label {
        color: #666;
        font-weight: 500;
        margin-right: 0.5rem;
    }
    .profile-value {
        color: #222;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# --- Get current user ---
current_user = check_auth()
user_id = get_user_attribute(current_user, 'id')
supabase = init_supabase()

# --- Fetch user details ---
def fetch_user_details(user_id):
    try:
        res = supabase.table('users').select('*').eq('id', user_id).execute()
        return res.data[0] if res.data else {}
    except Exception as e:
        st.error(f"Error fetching user details: {str(e)}")
        return {}

def fetch_enrolled_courses(user_id):
    try:
        enrollments = supabase.table('user_courses').select('*').eq('user_id', user_id).execute().data
        if not enrollments:
            return []
        course_ids = [e['course_id'] for e in enrollments]
        courses = supabase.table('courses').select('*').in_('id', course_ids).execute().data
        # Merge enrollment info with course info
        for e in enrollments:
            for c in courses:
                if c['id'] == e['course_id']:
                    c['completed'] = e.get('completed', False)
                    c['started_at'] = e.get('started_at', '')
        return courses
    except Exception as e:
        st.error(f"Error fetching enrolled courses: {str(e)}")
        return []

def fetch_skill_levels(user_id):
    try:
        skills = supabase.table('skill_levels').select('*').eq('user_id', user_id).execute().data
        return skills
    except Exception as e:
        st.error(f"Error fetching skills: {str(e)}")
        return []

def fetch_career_analyses(user_id):
    try:
        analyses = supabase.table('career_analyses').select('*').eq('user_id', user_id).order('analyzed_at', desc=True).execute().data
        return analyses
    except Exception as e:
        st.error(f"Error fetching analyses: {str(e)}")
        return []

# --- Back Button ---
back_col, _ = st.columns([1, 8])
with back_col:
    if st.button("⬅️ Back to Dashboard", key="back_btn", help="Return to Career Predictor", use_container_width=True):
        st.switch_page("pages/career_predictor.py")

# --- Display user info ---
user_details = fetch_user_details(user_id)
with st.container():
    st.markdown('<div class="profile-card">', unsafe_allow_html=True)
    st.markdown('<span class="profile-title">👤 My Profile</span>', unsafe_allow_html=True)
    st.markdown(f'<span class="profile-label">Name:</span> <span class="profile-value">{user_details.get("name", "N/A")}</span>', unsafe_allow_html=True)
    st.markdown(f'<span class="profile-label">Email:</span> <span class="profile-value">{user_details.get("email", "N/A")}</span>', unsafe_allow_html=True)
    st.markdown(f'<span class="profile-label">Age:</span> <span class="profile-value">{user_details.get("age", "N/A")}</span>', unsafe_allow_html=True)
    st.markdown(f'<span class="profile-label">Designation:</span> <span class="profile-value">{user_details.get("designation", "N/A")}</span>', unsafe_allow_html=True)
    st.markdown(f'<span class="profile-label">Joined:</span> <span class="profile-value">{user_details.get("created_at", "N/A")[:10]}</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Enrolled Courses ---
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("📚 Courses Enrolled In")
courses = fetch_enrolled_courses(user_id)
if courses:
    for course in courses:
        st.markdown(f"**{course['title']}**  \n:books: Provider: {course.get('provider', 'N/A')}")
        st.markdown(f":calendar: Started: {course.get('started_at', 'N/A')[:10]}")
        st.markdown(f":white_check_mark: Completed: {'✅' if course.get('completed') else '❌'}")
        st.markdown("---")
else:
    st.info("You have not enrolled in any courses yet.")
st.markdown('</div>', unsafe_allow_html=True)

# --- Skill Levels ---
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("🧠 My Skills")
skills = fetch_skill_levels(user_id)
if skills:
    df_skills = pd.DataFrame(skills)
    proficiency_levels = [
        "Not Interested", "Poor", "Beginner", 
        "Average", "Intermediate", "Excellent", "Professional"
    ]
    df_skills['level_text'] = df_skills['level'].apply(lambda x: proficiency_levels[x] if 0 <= x < len(proficiency_levels) else "Unknown")
    st.dataframe(df_skills[['skill_name', 'level_text']], hide_index=True, use_container_width=True)
else:
    st.info("No skill ratings found. Please rate your skills in the Career Predictor page.")
st.markdown('</div>', unsafe_allow_html=True)

# --- Career Path Analyses ---
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.subheader("🗂️ Career Path Analyses")
analyses = fetch_career_analyses(user_id)
if analyses:
    for a in analyses:
        st.markdown(f"**Career:** {a['predicted_role']}  \n:star: Confidence: {a.get('confidence', 0):.0%}  \n:calendar: Date: {a.get('analyzed_at', '')[:19].replace('T', ' ')}")
        if a.get('skill_gap'):
            import json
            try:
                gaps = json.loads(a['skill_gap'])
                if gaps:
                    st.markdown("Skill Gaps:")
                    for skill, gap in gaps.items():
                        st.markdown(f"- **{skill}:** {gap}")
            except Exception:
                pass
        st.markdown("---")
else:
    st.info("No career analyses found. Run an analysis in the Career Predictor page.")
st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>© 2024 CareerPath Pro | 📧 support@careerpath.com | 🔒 Data Privacy Guaranteed</p>
</div>
""", unsafe_allow_html=True)