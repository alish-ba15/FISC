import streamlit as st
import sqlite3
import pandas as pd

# Database setup
def init_db():
    conn = sqlite3.connect("tumor_detector.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS doctors (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS patients (id INTEGER PRIMARY KEY, name TEXT, age INTEGER, cancer_type TEXT, report TEXT, doctor TEXT)''')
    conn.commit()
    conn.close()

# Function to authenticate doctor
def authenticate(username, password):
    conn = sqlite3.connect("tumor_detector.db")
    c = conn.cursor()
    c.execute("SELECT * FROM doctors WHERE username=? AND password=?", (username, password))
    result = c.fetchone()
    conn.close()
    return result

# Function to save patient history
def save_report(name, age, cancer_type, report, doctor):
    conn = sqlite3.connect("tumor_detector.db")
    c = conn.cursor()
    c.execute("INSERT INTO patients (name, age, cancer_type, report, doctor) VALUES (?, ?, ?, ?, ?)", (name, age, cancer_type, report, doctor))
    conn.commit()
    conn.close()

# Function to get patient history
def get_patient_history():
    conn = sqlite3.connect("tumor_detector.db")
    df = pd.read_sql("SELECT * FROM patients", conn)
    conn.close()
    return df

# Initialize Database
init_db()

# App layout
st.set_page_config(page_title="Tumor Disease Detector", layout="wide")
st.title("Tumor Disease Detector")

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Page", ["Login", "Brain Cancer", "Breast Cancer", "Kidney Cancer", "Patient History"])

# Login Page
if page == "Login":
    st.sidebar.header("Doctor Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        if authenticate(username, password):
            st.session_state["doctor"] = username
            st.sidebar.success("Login successful!")
        else:
            st.sidebar.error("Invalid credentials")

# Cancer Detection Pages
def cancer_interface(cancer_type):
    st.header(f"{cancer_type} Detection")
    name = st.text_input("Patient Name")
    age = st.number_input("Age", min_value=1, max_value=120, step=1)
    uploaded_file = st.file_uploader("Upload MRI/X-ray Image", type=["png", "jpg", "jpeg"])
    if st.button("Analyze"):
        if uploaded_file and name:
            result = "Tumor detected"  # Placeholder AI analysis
            st.success(result)
            save_report(name, age, cancer_type, result, st.session_state.get("doctor", "Unknown"))
        else:
            st.error("Please provide all details.")

if page in ["Brain Cancer", "Breast Cancer", "Kidney Cancer"]:
    cancer_interface(page)

# Patient History
if page == "Patient History":
    st.header("Patient Reports")
    df = get_patient_history()
    st.dataframe(df)
