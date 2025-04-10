import streamlit as st
from supabase import create_client

def main():
    st.title("Connection Test")
    
    try:
        client = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )
        st.success("Connected to Supabase!")
        
        # Test table access
        courses = client.table('courses').select("*").execute()
        st.write(f"Found {len(courses.data)} courses")
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.error("Verify secrets.toml and database connection")

if __name__ == "__main__":
    main()