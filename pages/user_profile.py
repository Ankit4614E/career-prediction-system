import streamlit as st
from supabase import create_client
import json
from datetime import datetime
from streamlit_extras.colored_header import colored_header
from streamlit_extras.stylable_container import stylable_container
import pandas as pd
import matplotlib.pyplot as plt

# Initialize Supabase client
def init_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

# Check authentication status
def check_auth():
    if 'auth' not in st.session_state or not st.session_state.auth.get('logged_in', False):
        st.switch_page("pages/auth.py")
    return st.session_state.auth.get('user')

# Page configuration
st.set_page_config(
    page_title="Career Path Predictor Pro - User Profile",
    page_icon="👤",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .profile-header {
        display: flex;
        align-items: center;
        gap: 20px;
        padding: 20px 0;
    }
    .profile-avatar {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background: linear-gradient(45deg, #4B32C3, #876FFD);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 36px;
        font-weight: bold;
    }
    .profile-info {
        flex: 1;
    }
    .profile-section {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .stat-card {
        background: linear-gradient(45deg, #f5f7ff, #e6e9f0);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        height: 100%;
    }
    .stat-value {
        font-size: 24px;
        font-weight: bold;
        color: #4B32C3;
    }
    .stat-label {
        font-size: 14px;
        color: #666;
    }
    .career-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid #4B32C3;
    }
    .stButton>button {
        background: linear-gradient(45deg, #4B32C3, #876FFD);
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .nav-button {
        background: transparent !important;
        color: #4B32C3 !important;
        border: 1px solid #4B32C3 !important;
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
    .edit-button {
        background: transparent;
        border: 1px solid #4B32C3;
        color: #4B32C3;
        border-radius: 5px;
        padding: 5px 10px;
        cursor: pointer;
        font-size: 14px;
    }
    .edit-button:hover {
        background: #f0f2ff;
    }
</style>
""", unsafe_allow_html=True)

# Get current user
current_user = check_auth()

# Fetch full user profile data
def get_user_profile(user_id):
    try:
        supabase = init_supabase()
        response = supabase.table('users').select('*').eq('id', user_id).execute()
        if response.data:
            return response.data[0]
        return {}
    except Exception as e:
        st.error(f"Error retrieving user profile: {str(e)}")
        return {}

# Fetch user's career analyses
def get_user_analyses(user_id):
    try:
        supabase = init_supabase()
        response = supabase.table('career_analyses').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        return response.data
    except Exception as e:
        st.error(f"Error retrieving analyses: {str(e)}")
        return []

# Fetch user's skills
def get_user_skills(user_id):
    try:
        supabase = init_supabase()
        response = supabase.table('skill_levels').select('*').eq('user_id', user_id).execute()
        return response.data
    except Exception as e:
        st.error(f"Error retrieving skills: {str(e)}")
        return []

# Fetch user's enrolled courses
def get_user_courses(user_id):
    try:
        supabase = init_supabase()
        response = supabase.table('user_courses').select('*,courses(*)').eq('user_id', user_id).execute()
        return response.data
    except Exception as e:
        st.error(f"Error retrieving courses: {str(e)}")
        return []

# Update user profile
def update_user_profile(user_id, update_data):
    try:
        supabase = init_supabase()
        supabase.table('users').update(update_data).eq('id', user_id).execute()
        return True
    except Exception as e:
        st.error(f"Error updating profile: {str(e)}")
        return False

# Function to navigate back to career predictor page
def back_to_predictor():
    st.switch_page("pages/career_predictor.py")

# Header with navigation
col1, col2 = st.columns([6, 1])
with col1:
    colored_header(
        label="👤 User Profile",
        description="View and manage your career profile",
        color_name="violet-70",
    )
with col2:
    if st.button("← Back", key="back_button", use_container_width=True):
        back_to_predictor()

# Get user data
user_profile = get_user_profile(current_user.id)
user_analyses = get_user_analyses(current_user.id)
user_skills = get_user_skills(current_user.id)
user_courses = get_user_courses(current_user.id)

# Format dates
for analysis in user_analyses:
    created_at = datetime.fromisoformat(analysis['created_at'].replace('Z', '+00:00'))
    analysis['formatted_date'] = created_at.strftime("%b %d, %Y at %I:%M %p")

# Profile header section
with st.container():
    st.markdown(
        f"""
        <div class="profile-header">
            <div class="profile-avatar">{user_profile.get('name', 'User')[0].upper()}</div>
            <div class="profile-info">
                <h1>{user_profile.get('name', 'User')}</h1>
                <p>{user_profile.get('email')}</p>
                <p>{user_profile.get('designation', 'No designation specified')} | Age: {user_profile.get('age', 'Not specified')}</p>
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )

# Edit profile section
with st.expander("✏️ Edit Profile Information", expanded=False):
    with st.form("edit_profile_form"):
        name = st.text_input("Full Name", value=user_profile.get('name', ''))
        
        age = st.number_input(
            "Age", 
            min_value=13, 
            max_value=100, 
            value=user_profile.get('age', 25)
        )
        
        designation_options = [
            "Student", 
            "Professional", 
            "Recent Graduate", 
            "Career Changer", 
            "Entrepreneur", 
            "Other"
        ]
        
        designation = st.selectbox(
            "Current Designation", 
            designation_options, 
            index=designation_options.index(user_profile.get('designation', 'Student')) 
                if user_profile.get('designation') in designation_options else 0
        )
        
        bio = st.text_area(
            "Professional Bio", 
            value=user_profile.get('bio', ''),
            height=150
        )
        
        submit = st.form_submit_button("Update Profile")
        
        if submit:
            update_data = {
                'name': name,
                'age': age,
                'designation': designation,
                'bio': bio
            }
            
            if update_user_profile(current_user.id, update_data):
                st.success("Profile updated successfully!")
                st.rerun()  # Refresh the page to show updated data

# Career statistics
st.subheader("📊 Career Insights")
stat_cols = st.columns(4)

# Count of analyses
with stat_cols[0]:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-value">{len(user_analyses)}</div>
            <div class="stat-label">Career Analyses</div>
        </div>
        """, 
        unsafe_allow_html=True
    )

# Count of skills rated
with stat_cols[1]:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-value">{len(user_skills)}</div>
            <div class="stat-label">Skills Rated</div>
        </div>
        """, 
        unsafe_allow_html=True
    )

# Count of courses enrolled
with stat_cols[2]:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-value">{len(user_courses)}</div>
            <div class="stat-label">Courses Enrolled</div>
        </div>
        """, 
        unsafe_allow_html=True
    )

# Most recent analysis date
with stat_cols[3]:
    latest_date = user_analyses[0]['formatted_date'] if user_analyses else "No analyses yet"
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-value" style="font-size: 16px;">{latest_date}</div>
            <div class="stat-label">Latest Analysis</div>
        </div>
        """, 
        unsafe_allow_html=True
    )

# Career predictions section
st.subheader("🎯 Your Career Path Predictions")

if user_analyses:
    # Latest prediction in detail
    latest = user_analyses[0]
    st.markdown("### Latest Career Prediction")
    
    with stylable_container(
        key="latest_prediction",
        css_styles="""
            {
                background: linear-gradient(to right, #f5f7ff, #e6e9f0);
                border-radius: 15px;
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            }
        """,
    ):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"## {latest['predicted_role']}")
            st.markdown(f"**Analyzed on:** {latest['formatted_date']}")
            st.markdown(f"**Match Score:** {latest['confidence_score']:.0%}")
            
            if 'skill_gap' in latest and latest['skill_gap']:
                st.markdown("### Skill Gaps")
                try:
                    skill_gaps = json.loads(latest['skill_gap'])
                    for skill, gap in skill_gaps.items():
                        st.markdown(f"- **{skill}:** {gap}")
                except:
                    st.markdown("Skill gap information not available")
        
        with col2:
            # Circle progress visualization
            confidence = float(latest['confidence_score'])
            st.markdown(f"""
            <div style="border-radius:50%;width:150px;height:150px;background:conic-gradient(#4B32C3 {confidence*360}deg, #f0f2f6 0deg);margin:0 auto;display:flex;align-items:center;justify-content:center;">
                <div style="background:white;border-radius:50%;width:120px;height:120px;display:flex;align-items:center;justify-content:center;flex-direction:column;">
                    <span style="font-size:28px;font-weight:bold;color:#4B32C3;">{confidence:.0%}</span>
                    <span style="font-size:14px;color:#666;">Match Score</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Career history visualization - if more than one analysis
    if len(user_analyses) > 1:
        st.markdown("### Career Prediction History")
        
        # Convert data for visualization
        history_data = {
            'date': [datetime.fromisoformat(a['created_at'].replace('Z', '+00:00')) for a in user_analyses],
            'role': [a['predicted_role'] for a in user_analyses],
            'confidence': [float(a['confidence_score']) for a in user_analyses]
        }
        
        history_df = pd.DataFrame(history_data)
        history_df = history_df.sort_values('date')
        
        # Display in a table
        with st.expander("View detailed history", expanded=False):
            st.dataframe(
                history_df.rename(columns={
                    'date': 'Analysis Date',
                    'role': 'Predicted Role',
                    'confidence': 'Confidence Score'
                }).sort_values('Analysis Date', ascending=False),
                hide_index=True,
                column_config={
                    'Analysis Date': st.column_config.DatetimeColumn(format="MMM DD, YYYY"),
                    'Confidence Score': st.column_config.ProgressColumn(
                        width="medium",
                        format="%.0f%%",
                        min_value=0,
                        max_value=1
                    )
                }
            )
else:
    st.info("You haven't completed any career predictions yet. Go to the Career Predictor page to get started!")
    if st.button("Go to Career Predictor", use_container_width=False):
        back_to_predictor()

# Skills section
st.subheader("🧠 Your Skills Profile")

if user_skills:
    # Convert skills data for visualization
    proficiency_levels = [
        "Not Interested", "Poor", "Beginner", 
        "Average", "Intermediate", "Excellent", "Professional"
    ]
    
    skills_data = {
        'skill': [skill['skill_name'] for skill in user_skills],
        'level_num': [skill['level'] for skill in user_skills],
        'level': [proficiency_levels[skill['level']-1] for skill in user_skills]
    }
    
    skills_df = pd.DataFrame(skills_data)
    
    # Categorize skills
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
    
    # Add category to dataframe
    def get_category(skill_name):
        for category, skills in categories.items():
            if skill_name in skills:
                return category
        return "Other"
    
    skills_df['category'] = skills_df['skill'].apply(get_category)
    
    # Display skills by category
    for category, skills in categories.items():
        with st.expander(f"{category} Skills", expanded=True):
            cat_skills = skills_df[skills_df['category'] == category]
            
            if not cat_skills.empty:
                # Display skills in this category
                for i, row in cat_skills.iterrows():
                    st.markdown(f"**{row['skill']}:** {row['level']}")
                    st.progress(row['level_num'] / 7)  # Scale to 0-1 for progress bar
            else:
                st.markdown("No skills rated in this category yet.")
else:
    st.info("You haven't rated any skills yet. Go to the Career Predictor page to rate your skills!")

# Enrolled courses section
st.subheader("📚 Your Courses")

if user_courses:
    for course in user_courses:
        course_data = course['courses']
        
        with stylable_container(
            key=f"course_{course['course_id']}",
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
            cols = st.columns([3, 1])
            
            with cols[0]:
                st.markdown(f"**{course_data['name']}**")
                st.markdown(f"Target Role: *{course_data['target_role']}*")
                st.markdown(course_data.get('description', 'No description available'))
                
            with cols[1]:
                status = "✅ Completed" if course['completed'] else "⏳ In Progress"
                st.markdown(f"**Status:** {status}")
                
                if not course['completed']:
                    if st.button("Mark as Completed", key=f"complete_{course['id']}"):
                        try:
                            supabase = init_supabase()
                            supabase.table('user_courses').update({
                                'completed': True
                            }).eq('id', course['id']).execute()
                            st.success("Course marked as completed!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error updating course: {str(e)}")
else:
    st.info("You're not enrolled in any courses yet. Check out course recommendations in your career prediction!")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p>© 2024 CareerPath Pro | 📧 support@careerpath.com | 🔒 Data Privacy Guaranteed</p>
</div>
""", unsafe_allow_html=True)