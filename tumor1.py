import streamlit as st
import sqlite3
import pandas as pd
import datetime
import hashlib

# Function to hash passwords for security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to initialize the database
def init_db():
    conn = sqlite3.connect("tumor_detector.db")
    c = conn.cursor()

    # Create Patients Table
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

    # Create Doctors Table
    c.execute('''CREATE TABLE IF NOT EXISTS doctors (
                 id INTEGER PRIMARY KEY, 
                 username TEXT UNIQUE, 
                 password TEXT)''')
    
    conn.commit()
    conn.close()

# Function to register a new doctor
def register_doctor(username, password):
    conn = sqlite3.connect("tumor_detector.db")
    c = conn.cursor()

    try:
        hashed_password = hash_password(password)
        c.execute("INSERT INTO doctors (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

# Function to authenticate a doctor
def authenticate_doctor(username, password):
    conn = sqlite3.connect("tumor_detector.db")
    c = conn.cursor()
    hashed_password = hash_password(password)
    
    c.execute("SELECT * FROM doctors WHERE username = ? AND password = ?", (username, hashed_password))
    user = c.fetchone()
    conn.close()
    
    return user is not None

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

# Initialize Database
init_db()

# Set up session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# App layout
st.set_page_config(page_title="Tumor Disease Detector", layout="wide")

# Centered Title
st.markdown("<h1 style='text-align: center;'>Tumor Disease Detector</h1>", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("Navigation")

# If not logged in, show Login & Register options
if not st.session_state.authenticated:
    page = st.sidebar.radio("Select Page", ["Login", "Register"])
else:
    page = st.sidebar.radio("Select Page", ["Brain Cancer", "Breast Cancer", "Kidney Cancer", "Patient History", "Logout"])

# Doctor Registration Page
if page == "Register":
    st.subheader("Doctor Registration")
    new_username = st.text_input("Create Username")
    new_password = st.text_input("Create Password", type="password")

    if st.button("Register"):
        if new_username and new_password:
            success = register_doctor(new_username, new_password)
            if success:
                st.success("Registration successful! You can now log in.")
            else:
                st.error("Username already exists. Choose another username.")
        else:
            st.error("Please fill in all fields.")

# Doctor Login Page
if page == "Login":
    st.subheader("Doctor Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate_doctor(username, password):
            st.session_state.authenticated = True
            st.session_state.username = username
            st.success("Login Successful! Now you can access all functions.")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password!")

# Logout Function
if page == "Logout":
    st.session_state.authenticated = False
    st.session_state.pop("username", None)
    st.success("Logged out successfully!")
    st.experimental_rerun()

# Cancer Detection Page (Restricted to Logged-In Users)
def cancer_interface(cancer_type):
    if not st.session_state.authenticated:
        st.warning("⚠️ Please login to access this page!")
        return
    
    st.header(f"{cancer_type} Detection")

    name = st.text_input("Patient Name")
    age = st.number_input("Age", min_value=1, max_value=120, step=1)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    contact_no = st.text_input("Contact Number")
    lab_no = st.text_input("Lab Number")
    uploaded_file = st.file_uploader("Upload MRI/X-ray Image", type=["png", "jpg", "jpeg"])
    report_findings = st.text_area("Findings/Observations")
    doctor = st.session_state.username  # Auto-fill doctor's name from logged-in user

    if st.button("Analyze & Save Report"):
        if uploaded_file and name and contact_no and lab_no and report_findings:
            result = "Tumor detected"  # Placeholder AI analysis
            st.success(result)

            # Save report in the database
            save_report(name, age, gender, contact_no, lab_no, cancer_type, report_findings, doctor)
            
            st.success("Report Saved Successfully! Now check Patient History.")
        else:
            st.error("Please provide all required details.")

if page in ["Brain Cancer", "Breast Cancer", "Kidney Cancer"]:
    cancer_interface(page)

# Patient History Page (Restricted Access)
if page == "Patient History":
    if not st.session_state.authenticated:
        st.warning("⚠️ Please login to view patient history!")
    else:
        st.header("Download Patient Reports")
        df = get_patient_history()

        if not df.empty:
            # Convert DataFrame to CSV
            csv = df.to_csv(index=False)
            
            # Show only the download button (Hide Data Table)
            st.download_button("Download Patient History", csv, "patient_history.csv", "text/csv")
        else:
            st.warning("No patient records found.")
