# data_loader.py
import streamlit as st
import gdown
import json
import pickle

# Google Drive file IDs
JOINED_DATA_FILE_ID = "1ZgEJcIPdZstOwF0UVc0GJd4SBwmFDVBt"
JOB_VECTORS_FILE_ID = "14ZsyQgkxjkKRIQtBNi8H7eX9yJaPbo5H"

# Function to download file from Google Drive
@st.cache_data
def download_from_drive(file_id, output_path):
    try:
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, output_path, quiet=False)
        return output_path
    except Exception as e:
        st.error(f"Error downloading file from Google Drive: {e}")
        return None

# Function to load data from JSON file
@st.cache_data
def load_data():
    try:
        # Download the JSON file from Google Drive
        json_path = "joined_data_standar.json"
        downloaded_path = download_from_drive(JOINED_DATA_FILE_ID, json_path)
        if downloaded_path:
            with open(downloaded_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            return data
        else:
            return []
    except Exception as e:
        st.error(f"Error loading JSON file: {e}")
        return []

# Function to load pre-calculated vectors
@st.cache_data
def load_job_vectors():
    try:
        # Download the pickle file from Google Drive
        pkl_path = "job_vectors.pkl"
        downloaded_path = download_from_drive(JOB_VECTORS_FILE_ID, pkl_path)
        if downloaded_path:
            with open(downloaded_path, "rb") as f:
                job_vectors = pickle.load(f)
            return job_vectors
        else:
            return {}
    except Exception as e:
        st.error(f"Error loading job_vectors.pkl: {e}")
        return {}