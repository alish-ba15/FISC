import streamlit as st
import sqlite3
import pandas as pd
import datetime

# Function to initialize the database (without dropping existing data)
def init_db():
    conn = sqlite3.connect("tumor_detector.db")
    c = conn.cursor()
    
    # Create Patients Table (without dropping it)
    c.execute('''CREATE TABLE IF NOT EXISTS patients (
                 id INTEGER PRIMARY KEY, 
                 name TEXT, 
                 age INTEGER, 
                 gender TEXT, 
                 contact_no TEXT, 
                 lab_no TEXT, 
                 cancer_type TEXT, 
                 report TEXT, 
                 report_date TEXT, 
                 doctor TEXT)''')
    
    conn.commit()
    conn.close()

# Function to save patient report
def save_report(name, age, gender, contact_no, lab_no, cancer_type, report, doctor):
    conn = sqlite3.connect("tumor_detector.db")
    c = conn.cursor()
    report_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''INSERT INTO patients 
                 (name, age, gender, contact_no, lab_no, cancer_type, report, report_date, doctor) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                 (name, age, gender, contact_no, lab_no, cancer_type, report, report_date, doctor))
    conn.commit()
    conn.close()

# Function to get patient history
def get_patient_history():
    conn = sqlite3.connect("tumor_detector.db")
    df = pd.read_sql("SELECT * FROM patients", conn)
    conn.close()
    return df

# Initialize Database (Without Resetting Data)
init_db()

# App layout
st.set_page_config(page_title="Tumor Disease Detector", layout="wide")

# Centered Title
st.markdown("<h1 style='text-align: center;'>Tumor Disease Detector</h1>", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Page", ["Login", "Brain Cancer", "Breast Cancer", "Kidney Cancer", "Patient History"])

# Doctor Login Page (Centered)
if page == "Login":
    st.markdown("<br><br>", unsafe_allow_html=True)  # Add spacing
    col1, col2, col3 = st.columns([1, 2, 1])  # Centering the form

    with col2:
        st.subheader("Doctor Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username and password:
                st.success("Login Successful!")
            else:
                st.error("Please enter both username and password.")

# Cancer Detection Page
def cancer_interface(cancer_type):
    st.header(f"{cancer_type} Detection")

    name = st.text_input("Patient Name")
    age = st.number_input("Age", min_value=1, max_value=120, step=1)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    contact_no = st.text_input("Contact Number")
    lab_no = st.text_input("Lab Number")
    uploaded_file = st.file_uploader("Upload MRI/X-ray Image", type=["png", "jpg", "jpeg"])
    report_findings = st.text_area("Findings/Observations")
    doctor = st.text_input("Doctor's Name")  # Added field for doctor name

    if st.button("Analyze & Save Report"):
        if uploaded_file and name and contact_no and lab_no and report_findings and doctor:
            result = "Tumor detected"  # Placeholder AI analysis
            st.success(result)

            # Save report in the database
            save_report(name, age, gender, contact_no, lab_no, cancer_type, report_findings, doctor)
            
            st.success("Report Saved Successfully! Now check Patient History.")
        else:
            st.error("Please provide all required details.")

if page in ["Brain Cancer", "Breast Cancer", "Kidney Cancer"]:
    cancer_interface(page)

# Patient History Page (Hidden Table, Only Download Button)
if page == "Patient History":
    st.header("Download Patient Reports")

    df = get_patient_history()

    if not df.empty:
        # Convert DataFrame to CSV
        csv = df.to_csv(index=False)
        
        # Show only the download button (Hide Data Table)
        st.download_button("Download Patient History", csv, "patient_history.csv", "text/csv")
    else:
        st.warning("No patient records found.")
