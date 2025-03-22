
import streamlit as st
import pandas as pd
import numpy as np
import joblib

# Load the trained model and encoders
model = joblib.load("career_model.pkl")
encoder = joblib.load("label_encoder.pkl")

# Define skills list
skills = [
    "Database Fundamentals", "Computer Architecture", "Distributed Computing Systems", "Cyber Security",
    "Networking", "Software Development", "Programming Skills", "Project Management",
    "Computer Forensics Fundamentals", "Technical Communication", "AI ML", "Software Engineering",
    "Business Analysis", "Communication skills", "Data Science", "Troubleshooting skills", "Graphics Designing"
]

# Streamlit UI
st.title("Career Prediction System")
st.write("Enter your skills to predict the best career for you.")

# User Inputs
user_data = []
for skill in skills:
    user_input = st.selectbox(f"{skill} Level", ["Not Interested", "Poor", "Beginner", "Average", "Intermediate", "Professional"])
    user_data.append(encoder.transform([user_input])[0])

# Convert user input to numpy array
input_data = np.array([user_data])

# Predict Career Path
if st.button("Predict Career"):
    prediction = model.predict(input_data)
    predicted_career = encoder.inverse_transform(prediction)
    st.success(f"Predicted Career: {predicted_career[0]}")
