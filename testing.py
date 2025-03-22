import streamlit as st
import pandas as pd
import joblib
from sklearn.preprocessing import OrdinalEncoder, LabelEncoder

# Load artifacts with verification
try:
    feature_encoder = joblib.load("feature_encoder.pkl")
    label_encoder = joblib.load("label_encoder.pkl") 
    model = joblib.load("career_model.pkl")
    
    # Debug: Show known careers
    st.write("Known career paths:", list(label_encoder.classes_))
except Exception as e:
    st.error(f"Error loading resources: {str(e)}")
    st.stop()

# Updated skill levels (must match training)
skills = [
    "Database Fundamentals", "Computer Architecture", "Distributed Computing Systems",
    "Cyber Security", "Networking", "Software Development", "Programming Skills",
    "Project Management", "Computer Forensics Fundamentals", "Technical Communication",
    "AI ML", "Software Engineering", "Business Analysis", "Communication skills",
    "Data Science", "Troubleshooting skills", "Graphics Designing"
]

skill_levels = ["Not Interested", "Poor", "Beginner", "Average", 
               "Intermediate", "Excellent", "Professional"]  # Added Excellent

# Streamlit UI
st.title("Career Prediction System")
st.write("Enter your skills to predict the best career for you.")

# Collect Inputs
user_data = []
for skill in skills:
    user_input = st.selectbox(f"{skill} Level", skill_levels)
    user_data.append(user_input)

# Encode Inputs
try:
    encoded_input = feature_encoder.transform(pd.DataFrame([user_data], columns=skills))
except Exception as e:
    st.error(f"Encoding error: {str(e)}")
    st.stop()

# Make Prediction
if st.button("Predict Career"):
    try:
        prediction = model.predict(encoded_input)
        predicted_career = label_encoder.inverse_transform(prediction)
        st.success(f"Predicted Career: {predicted_career[0]}")
    except Exception as e:
        st.error(f"Prediction failed: {str(e)}")