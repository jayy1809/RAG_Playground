import streamlit as st
import requests

input_file = st.file_uploader("Upload Input Data", type="json")
ground_truth_file = st.file_uploader("Upload Ground Truth", type="json")

if input_file and ground_truth_file:
    input_data = input_file.read().decode("utf-8")
    ground_truth = ground_truth_file.read().decode("utf-8")

    response = requests.post(
        "http://localhost:8000/upload-files",
        json={"input_data": input_data, "ground_truth": ground_truth}
    )
    st.write(response.json())