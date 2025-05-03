# train_model.py
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OrdinalEncoder, LabelEncoder
from sklearn.metrics import accuracy_score
import streamlit as st
from supabase import create_client


# 1. Load and Prepare Data
def load_data(file_path='dataset9000.csv'):
    df = pd.read_csv(file_path)
    
    # Define skills and their order (must match Streamlit app)
    skills = [
        "Database Fundamentals", "Computer Architecture", "Distributed Computing Systems",
        "Cyber Security", "Networking", "Software Development", "Programming Skills",
        "Project Management", "Computer Forensics Fundamentals", "Technical Communication",
        "AI ML", "Software Engineering", "Business Analysis", "Communication skills",
        "Data Science", "Troubleshooting skills", "Graphics Designing"
    ]
    
    # Updated ordinal categories with 'Excellent'
    skill_levels = ["Not Interested", "Poor", "Beginner", 
                   "Average", "Intermediate", "Excellent", "Professional"]
    
    return df, skills, skill_levels

# 2. Preprocessing
def preprocess_data(df, skills, skill_levels):
    # Separate features and target
    X = df[skills]
    y = df['Role']
    
    # Create and fit encoders
    feature_encoder = OrdinalEncoder(
        categories=[skill_levels]*len(skills),
        handle_unknown='use_encoded_value',
        unknown_value=-1
    )
    label_encoder = LabelEncoder()
    
    # Transform data
    X_encoded = feature_encoder.fit_transform(X)
    y_encoded = label_encoder.fit_transform(y)
    
    return X_encoded, y_encoded, feature_encoder, label_encoder

# 3. Training
def train_model(X, y):
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Initialize and train model
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_split=5,
        class_weight='balanced',
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    print(f"Model Accuracy: {accuracy_score(y_test, y_pred):.2f}")
    print("Class distribution:", dict(pd.Series(y).value_counts()))
    
    return model

# 4. Save Artifacts
def save_artifacts(model, feature_encoder, label_encoder):
    joblib.dump(model, 'career_model.pkl')
    joblib.dump(feature_encoder, 'feature_encoder.pkl')
    joblib.dump(label_encoder, 'label_encoder.pkl')
    print("Artifacts saved successfully")

# Main execution
if __name__ == '__main__':
    print("=== Starting training process ===")
    
    # Load data
    print("Loading data...")
    df, skills, skill_levels = load_data()
    print(f"Loaded {len(df)} records")
    print(f"Unique roles: {df['Role'].unique()}")
    
    # Preprocess
    print("Preprocessing data...")
    X, y, feature_encoder, label_encoder = preprocess_data(df, skills, skill_levels)
    
    # Train model
    print("Training model...")
    model = train_model(X, y)
    
    # Save artifacts
    print("Saving artifacts...")
    save_artifacts(model, feature_encoder, label_encoder)
    print("=== Training completed successfully ===")

client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

try:
    data = client.table('courses').select("*").execute()
    st.write("Connection successful! Found courses:")
    st.write(data.data)
except Exception as e:
    st.error(f"Connection failed: {str(e)}")