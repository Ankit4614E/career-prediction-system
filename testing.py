import streamlit as st
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Load or Train the Model
def load_model():
    try:
        with open("career_model.pkl", "rb") as file:
            model = pickle.load(file)
    except FileNotFoundError:
        # Dummy dataset (replace with actual dataset)
        data = pd.DataFrame({
            "math_score": [85, 70, 90, 65, 80, 50, 75, 95, 60, 85],
            "english_score": [70, 85, 75, 80, 65, 90, 60, 95, 50, 75],
            "science_score": [90, 75, 85, 60, 80, 55, 70, 95, 65, 90],
            "preferred_field": ["Engineering", "Arts", "Engineering", "Commerce", "Science", "Commerce", "Arts", "Engineering", "Commerce", "Science"]
        })

        # Encoding categorical values
        label_encoder = LabelEncoder()
        data["preferred_field_encoded"] = label_encoder.fit_transform(data["preferred_field"])
        
        # Splitting data
        X = data[["math_score", "english_score", "science_score"]]
        y = data["preferred_field_encoded"]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train the model
        model = RandomForestClassifier()
        model.fit(X_train, y_train)
        
        # Save the model
        with open("career_model.pkl", "wb") as file:
            pickle.dump(model, file)
    return model

model = load_model()

# Streamlit UI
st.title("Career Prediction System")
st.write("Fill in your scores to predict a suitable career field.")

# Input Fields
math_score = st.slider("Math Score", 0, 100, 50)
english_score = st.slider("English Score", 0, 100, 50)
science_score = st.slider("Science Score", 0, 100, 50)

if st.button("Predict Career"):
    prediction = model.predict([[math_score, english_score, science_score]])
    career_map = {0: "Arts", 1: "Commerce", 2: "Engineering", 3: "Science"}  # Adjust based on label encoding
    predicted_career = career_map.get(prediction[0], "Unknown")
    st.success(f"Your predicted career field is: {predicted_career}")
