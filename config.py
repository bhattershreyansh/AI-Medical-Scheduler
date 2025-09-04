import os
from dotenv import load_dotenv

load_dotenv()

# New Groq config
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL")  # Fast Groq model

# File Paths
PATIENTS_CSV = "data/patients.csv"
DOCTORS_EXCEL = "data/doctors_schedule.xlsx"
APPOINTMENTS_EXCEL = "data/appointments.xlsx"
INTAKE_FORM_PATH = "data/forms/New-Patient-Intake-Form.pdf"

# Email Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Application Settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"