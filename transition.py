import streamlit as st
import time

# Custom CSS for the transition effect
st.markdown("""
<style>
    .transition-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        text-align: center;
    }
    .loading-spinner {
        width: 50px;
        height: 50px;
        border: 5px solid rgba(0, 0, 0, 0.1);
        border-top: 5px solid #4B32C3;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

# Transition page content
st.markdown("""
<div class="transition-container">
    <h2>🚀 Welcome to Career Path Predictor Pro</h2>
    <p>Preparing your personalized experience...</p>
    <div class="loading-spinner"></div>
</div>
""", unsafe_allow_html=True)

# JavaScript-based redirect after 3 seconds
st.markdown("""
<script>
    setTimeout(function() {
        window.location.href = "testing.py";
    }, 3000);
</script>
""", unsafe_allow_html=True)
