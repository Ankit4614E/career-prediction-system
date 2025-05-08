# auth.py
from datetime import datetime
import streamlit as st
from supabase import create_client
import re

# Initialize Supabase client
def init_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

# Session state management
def init_session():
    if 'auth' not in st.session_state:
        st.session_state.auth = {
            'user': None,
            'logged_in': False,
            'page': 'login'
        }

# Page configuration
st.set_page_config(
    page_title="Career Path Predictor Pro - Auth",
    page_icon="🔐",
    layout="wide"
)

# Authentication UI components
def show_auth_page():
    init_session()
    supabase = init_supabase()
    
    # Check if already logged in
    if st.session_state.auth['logged_in']:
        st.switch_page("pages/career_predictor.py")
    
    # Page styling
    st.markdown("""
    <style>
        .auth-container {
            max-width: 500px;
            margin: 2rem auto;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            background-color: white;
        }
        .auth-form { margin-bottom: 1.5rem; }
        .toggle-page { text-align: center; margin-top: 1rem; }
        .stButton>button {
            background: linear-gradient(45deg, #4B32C3, #876FFD);
            color: white;
            border-radius: 8px;
            padding: 10px 24px;
            font-weight: bold;
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
        
        # Logo and title
        col1, col2 = st.columns([1, 4])
        with col1:
            st.image("https://cdn-icons-png.flaticon.com/512/1055/1055666.png", width=60)
        with col2:
            st.markdown("## Career Path Predictor Pro")
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Page toggle
        if st.session_state.auth['page'] == 'login':
            show_login_form(supabase)
            
            # Toggle button to registration
            if st.button("Don't have an account? Register here"):
                st.session_state.auth['page'] = 'register'
                st.rerun()
        else:
            show_register_form(supabase)
            
            # Toggle button to login
            if st.button("Already have an account? Sign in here"):
                st.session_state.auth['page'] = 'login'
                st.rerun()
            
        st.markdown("</div>", unsafe_allow_html=True)

def show_login_form(supabase):
    st.header("Welcome Back! 🔐")
    with st.form("Login Form"):
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Sign In")
        
        if submit:
            handle_login(supabase, email, password)

def show_register_form(supabase):
    st.header("Create Account 🚀")
    with st.form("Register Form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        
        # New fields for age and designation
        age = st.number_input("Age", min_value=13, max_value=100, value=25)
        designation_options = [
            "Student", 
            "Professional", 
            "Recent Graduate", 
            "Career Changer", 
            "Entrepreneur", 
            "Other"
        ]
        designation = st.selectbox("Current Designation", designation_options)
        
        password = st.text_input("Create Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Create Account")
        
        if submit:
            if validate_registration(name, email, age, designation, password, confirm_password):
                handle_registration(supabase, name, email, age, designation, password)

# Authentication handlers
def handle_login(supabase, email, password):
    try:
        if not email or not password:
            st.error("Please enter both email and password")
            return

        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        # Fetch additional user data with authenticated session
        user_data = supabase.table('users').select('*').eq('id', response.user.id).execute()
        user_profile = user_data.data[0] if user_data.data else {}

        # Create a session user object (do NOT attach tokens to response.user)
        session_user = {
            "id": response.user.id,
            "email": response.user.email,
            "name": user_profile.get('name', ''),
            "age": user_profile.get('age', 0),
            "designation": user_profile.get('designation', ''),
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }

        st.session_state.auth.update({
            'user': session_user,
            'logged_in': True
        })
        st.success("Successfully logged in!")
        st.switch_page("pages/career_predictor.py")

    except Exception as e:
        error_message = str(e)
        if "Invalid login credentials" in error_message:
            st.error("Incorrect email or password. Please try again.")
        elif "Email not confirmed" in error_message:
            st.error("Please confirm your email address before logging in.")
        else:
            st.error(f"Login failed: {error_message}")

def handle_registration(supabase, name, email, age, designation, password):
    from datetime import datetime

    try:
        # Step 1: Sign up the user
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        # Step 2: Check if signup was successful
        if response.user and response.session:
            supabase.auth.set_session(
                response.session.access_token,
                response.session.refresh_token
            )

            created_at = getattr(response.user, 'created_at', datetime.now()).isoformat()

            # Step 3: Insert metadata into 'users' table
            user_data = {
                "id": response.user.id,
                "email": email,
                "name": name,
                "age": age,
                "designation": designation,
                "created_at": created_at
            }

            # Insert user data and handle any exceptions
            try:
                insert_result = supabase.table('users').insert(user_data).execute()
            except Exception as insert_error:
                st.error("Failed to store user details in the database.")
                st.error(f"Insert error: {str(insert_error)}")
                return

            # Create a session user object
            session_user = {
                "id": response.user.id,
                "email": email,
                "name": name,
                "age": age,
                "designation": designation,
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token
            }

            st.session_state.auth.update({
                'user': session_user,
                'logged_in': True
            })

            st.success("Account created successfully!")
            st.switch_page("pages/career_predictor.py")

        else:
            st.success("Check your email to confirm registration before logging in.")

    except Exception as e:
        error_message = str(e)
        
        # Check for specific error messages
        if "User already registered" in error_message or "already exists" in error_message.lower():
            st.error("This email is already registered. Please log in or use a different email address.")
        elif "password" in error_message.lower():
            st.error("Password error: " + error_message)
        else:
            st.error(f"Registration failed: {error_message}")

def validate_registration(name, email, age, designation, password, confirm_password):
    if not name:
        st.error("Please enter your full name")
        return False
        
    if not email:
        st.error("Please enter an email address")
        return False
        
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        st.error("Please enter a valid email address")
        return False
    
    if age < 13:
        st.error("You must be at least 13 years old to register")
        return False
        
    if len(password) < 8:
        st.error("Password must be at least 8 characters")
        return False
        
    if password != confirm_password:
        st.error("Passwords do not match")
        return False
        
    return True

# Logout handler (for use in other pages)
def logout():
    if 'auth' in st.session_state:
        st.session_state.auth = {
            'user': None,
            'logged_in': False,
            'page': 'login'
        }

# Run the authentication page
show_auth_page()