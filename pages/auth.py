# auth.py
import streamlit as st
from supabase import create_client
import re


# Initialize Supabase client
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# Session state management
def init_session():
    if 'auth' not in st.session_state:
        st.session_state.auth = {
            'user': None,
            'logged_in': False,
            'page': 'login'
        }

# Authentication UI components
def show_auth_page():
    init_session()
    supabase = init_supabase()
    
    # Check if already logged in
    if st.session_state.auth['logged_in']:
        st.switch_page("testing.py")
    
    # Page styling
    st.markdown("""
    <style>
        .auth-container {
            max-width: 500px;
            margin: 2rem auto;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .auth-form { margin-bottom: 1.5rem; }
        .toggle-page { text-align: center; margin-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
        
        # Page toggle
        if st.session_state.auth['page'] == 'login':
            show_login_form(supabase)
        else:
            show_register_form(supabase)
            
        st.markdown("</div>", unsafe_allow_html=True)

def show_login_form(supabase):
    st.header("Welcome Back! 🔐")
    with st.form("Login Form"):
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Sign In")
        
        if submit:
            handle_login(supabase, email, password)
            
    st.markdown(
        "<div class='toggle-page'>"
        "Don't have an account? "
        "<a href='#' onclick='window.streamlit.setComponentValue(\"register\")'>Register here</a>"
        "</div>", 
        unsafe_allow_html=True
    )

def show_register_form(supabase):
    st.header("Create Account 🚀")
    with st.form("Register Form"):
        email = st.text_input("Email Address")
        password = st.text_input("Create Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Create Account")
        
        if submit:
            if validate_registration(email, password, confirm_password):
                handle_registration(supabase, email, password)
            
    st.markdown(
        "<div class='toggle-page'>"
        "Already have an account? "
        "<a href='#' onclick='window.streamlit.setComponentValue(\"login\")'>Sign in here</a>"
        "</div>", 
        unsafe_allow_html=True
    )

# Authentication handlers
def handle_login(supabase, email, password):
    try:
        user = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        st.session_state.auth.update({
            'user': user.user,
            'logged_in': True
        })
        st.rerun()
        
    except Exception as e:
        st.error("Invalid credentials or user not found")

def handle_registration(supabase, email, password):
    try:
        user = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        # Create user profile in public table
        supabase.table('users').insert({
            "id": user.user.id,
            "email": email,
            "created_at": user.user.created_at
        }).execute()
        
        st.session_state.auth.update({
            'user': user.user,
            'logged_in': True
        })
        st.success("Account created successfully!")
        st.rerun()
        
    except Exception as e:
        st.error(f"Registration failed: {str(e)}")

# Validation functions
def validate_registration(email, password, confirm_password):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        st.error("Please enter a valid email address")
        return False
        
    if len(password) < 8:
        st.error("Password must be at least 8 characters")
        return False
        
    if password != confirm_password:
        st.error("Passwords do not match")
        return False
        
    return True

# Logout handler
def logout():
    supabase = init_supabase()
    supabase.auth.sign_out()
    st.session_state.auth = {
        'user': None,
        'logged_in': False,
        'page': 'login'
    }
    show_auth_page()
    def show_auth_page():
    if "auth" not in st.session_state:
        st.session_state.auth = {
            "user": None,
            "logged_in": False,
            "page": "login"
        }
    if authentication_successful:
    st.switch_page("testing")

    st.rerun()