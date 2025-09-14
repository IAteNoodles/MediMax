import streamlit as st
import requests
import json

# Define the base URL of the agentic server
BASE_URL = "http://10.26.5.99:8000"

st.title("Agentic Server Test Interface")

st.header("Patient Assessment")

# Input fields for the patient data
patient_text = st.text_area("Patient Text", "The patient is a 52-year-old male, height 175 cm, weight 95 kg. He presents for a routine check-up. He has a history of hypertension and his father had a heart attack at age 60. His systolic blood pressure is 145 (ap_hi: 145) and his diastolic blood pressure is 92 (ap_lo: 92). Recent lab work shows his cholesterol is above normal (cholesterol: 2) and his glucose is well above normal (gluc: 3). The patient reports that he smokes cigarettes daily (smoke: 1) and consumes alcohol a few times a week (alco: 1). He describes his lifestyle as mostly sedentary with little to no physical activity (active: 0).")
query = st.text_input("Query", "Cardiovascular risk assessment")
additional_notes = st.text_area("Additional Notes", "Patient has a family history of heart disease.")

col1, col2 = st.columns(2)

with col1:
    if st.button("Assess Patient"):
        if patient_text and query:
            # Prepare the data for the POST request
            assessment_data = {
                "patient_text": patient_text,
                "query": query,
                "additional_notes": additional_notes
            }
            
            st.write("Sending request to:", f"{BASE_URL}/assess")
            st.json(assessment_data)

            try:
                # Send the request to the agentic server
                headers = {"Content-Type": "application/json"}
                response = requests.post(f"{BASE_URL}/assess", data=json.dumps(assessment_data), headers=headers)
                response.raise_for_status()  # Raise an exception for bad status codes
                
                st.header("Server Response")
                st.json(response.json())

            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please fill in the 'Patient Text' and 'Query' fields.")

with col2:
    if st.button("Assess with Mock Data"):
        st.write("Sending request to:", f"{BASE_URL}/assess_mock?patient_index=0")
        try:
            # Send the request to the agentic server
            response = requests.post(f"{BASE_URL}/assess_mock?patient_index=0")
            response.raise_for_status()  # Raise an exception for bad status codes
            
            st.header("Server Response")
            st.json(response.json())

        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {e}")

st.header("Server Health Check")
if st.button("Check Health"):
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        st.header("Health Check Response")
        st.json(response.json())
    except requests.exceptions.RequestException as e:
        st.error(f"Health check failed: {e}")

st.header("Available Models")
if st.button("Get Models"):
    try:
        response = requests.get(f"{BASE_URL}/models")
        response.raise_for_status()
        st.header("Models Response")
        st.json(response.json())
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to get models: {e}")
