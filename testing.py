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
        # Load actual dataset
        data = pd.read_csv("Career_Choices.csv")  # Make sure the file is in the same directory

        # Check column names
        expected_columns = ["math_score", "english_score", "science_score", "preferred_field"]
        if not all(col in data.columns for col in expected_columns):
            st.error("Dataset does not have the required columns!")
            return None

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
st.set_page_config(page_title="Career Predictor", layout="wide")
st.markdown("<h1 style='text-align: center; color: blue;'>Career Prediction System</h1>", unsafe_allow_html=True)
st.write("Enter your scores to predict the best career field for you.")

# Input Fields
col1, col2 = st.columns(2)

with col1:
    math_score = st.slider("Math Score", 0, 100, 50)
    english_score = st.slider("English Score", 0, 100, 50)

with col2:
    science_score = st.slider("Science Score", 0, 100, 50)

if st.button("Predict Career") and model:
    prediction = model.predict([[math_score, english_score, science_score]])
    career_map = {index: field for index, field in enumerate(pd.read_csv("Career_Choices.csv")["preferred_field"].unique())}
    predicted_career = career_map.get(prediction[0], "Unknown")

    st.markdown(f"<h2 style='text-align: center; color: green;'>Your predicted career field is: {predicted_career}</h2>", unsafe_allow_html=True)
