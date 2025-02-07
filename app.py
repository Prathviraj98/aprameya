import pdfplumber
import pytesseract
import cv2
import streamlit as st
import os
import pandas as pd
import easyocr
import re
from datetime import datetime
import locale
import tempfile
import hashlib  # Import hashlib for generating hash codes

c1 = 0
c2 = 0

# Set locale for currency formatting to Indian
try:
    locale.setlocale(locale.LC_ALL, 'en_IN.UTF-8')  # Set to Indian locale
except locale.Error:
    st.warning("Locale 'en_IN.UTF-8' not supported on this system.")

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_from_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, config='--psm 6')
    return text

def parse_financial_data(text):
    data = []
    unique_records = set()  # Set to track unique records
    
    # Extract Unique ID
    unique_id_match = re.search(r'Unique ID:\s*(\w+)', text)
    unique_id = unique_id_match.group(1).strip() if unique_id_match else None

    # Extract Company Name
    company_name_match = re.search(r'Company Name:\s*(.*?)\s*Date:', text, re.DOTALL)
    company_name = company_name_match.group(1).strip() if company_name_match else None

    # Extract date
    date_match = re.search(r'Date:\s*(\d{4}-\d{2}-\d{2})', text)
    date = pd.to_datetime(date_match.group(1)) if date_match else None

    # Extract total amount
    total_amount_match = re.search(r'Total:\s*([\d,]+(?:\.\d+)?)', text)
    total_amount = float(total_amount_match.group(1).replace(',', '')) if total_amount_match else None

    if unique_id and company_name and date and total_amount is not None:
        formatted_amount = locale.currency(total_amount, grouping=True, symbol=True)
        record = (unique_id, company_name, formatted_amount, date)

        # Check if the record is unique
        if record not in unique_records:
            unique_records.add(record)  # Add to the set
            data.append({'Unique ID': unique_id, 'Company Name': company_name, 'Amount': formatted_amount, 'Date': date})
        else:
            st.warning(f"Duplicate record found for Unique ID: {unique_id}, Company Name: {company_name}, Date: {date}. Skipping.")
    else:
        st.warning("Could not extract all required fields from the text.")

    return data

def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

def calculate_file_hash(file_path):
    """Calculate SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read the file in chunks
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

st.set_page_config(
    page_title="Audity",
    page_icon="logo.png"
)

# Initialize EasyOCR Reader
reader = easyocr.Reader(['en'])

st.title("Audity")
st.subheader("A Financial Statement Auditor")

# Load billing records to fetch unique IDs
billing_recordsm = pd.read_csv('/home/darling/Documents/bilgen/billing_records.csv')
billing_recordsm.columns = billing_recordsm.columns.str.strip()

# Ensure the date column is in datetime format and sort by date and Company Name
if 'Date' in billing_recordsm.columns:
    billing_recordsm['Date'] = pd.to_datetime(billing_recordsm['Date'], errors='coerce')
    billing_recordsm = billing_recordsm.sort_values(by=['Date', 'Company Name'])

billing_records_file = st.file_uploader("Upload Billing Records (CSV)", type=["csv"])
billing_records = pd.DataFrame()

if billing_records_file is not None:
    billing_records = pd.read_csv(billing_records_file)
    billing_records.columns = billing_records.columns.str.strip()

    if 'Date' in billing_records.columns:
        billing_records['Date'] = pd.to_datetime(billing_records['Date'], errors='coerce')
        billing_records = billing_records.sort_values(by=['Date', 'Company Name'])

# Upload multiple PDF or image files
uploaded_files = st.file_uploader("Upload PDF or Image files", type=["pdf", "jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    all_data = []
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.getbuffer())
            temp_file_path = temp_file.name

        if uploaded_file.name.endswith('.pdf'):
            text = extract_text_from_pdf(temp_file_path)
        else:
            text = extract_text_from_image(temp_file_path)

        all_data.extend(parse_financial_data(text))
        
        # Calculate the hash of the uploaded PDF
        if uploaded_file.name.endswith('.pdf'):
            uploaded_pdf_hash = calculate_file_hash(temp_file_path)
            st.write(f"Uploaded PDF Hash: {uploaded_pdf_hash}")

            # Check against the stored hash in billing records
            if 'PDF Hash' in billing_recordsm.columns:
                # Find the corresponding unique ID in the billing records
                unique_id_match = re.search(r'Unique ID:\s*(\w+)', text)
                if unique_id_match:
                    unique_id = unique_id_match.group(1).strip()
                    stored_hash = billing_recordsm.loc[billing_recordsm['Unique ID'] == unique_id, 'PDF Hash']
                    
                    if not stored_hash.empty:
                        stored_hash_value = stored_hash.values[0]
                        if uploaded_pdf_hash == stored_hash_value:
                            st.success("The uploaded PDF hash matches the stored hash.")
                        else:
                            st.warning("The uploaded PDF hash does NOT match the stored hash.")
                    else:
                        st.warning(f"No matching Unique ID found in billing records for Unique ID: {unique_id}")
        
        os.remove(temp_file_path)

    if st.button("Parse Financial Data"):
        parsed_df = pd.DataFrame(all_data)

        if not parsed_df.empty:
            parsed_df['Date'] = pd.to_datetime(parsed_df['Date'], errors='coerce')
            parsed_df = parsed_df.sort_values(by=['Date', 'Company Name'])

            st.subheader("Parsed Data")
            st.write(parsed_df)

            if 'Unique ID' in parsed_df.columns and 'Unique ID' in billing_recordsm.columns:
                parsed_unique_ids = set(parsed_df['Unique ID'].astype(str))
                billing_unique_ids = set(billing_recordsm['Unique ID'].astype(str))

                matched_ids = parsed_unique_ids.intersection(billing_unique_ids)
                unmatched_ids = parsed_unique_ids - matched_ids

                if unmatched_ids:
                    st.warning(f"Unique IDs not found in billing records: {', '.join(unmatched_ids)}")
                else:
                    st.success("All Unique IDs match with billing records.")
            else:
                c1 = 1

            if 'Company Name' in parsed_df.columns and 'Amount' in parsed_df.columns:
                for index, row in parsed_df.iterrows():
                    company_name = row['Company Name']
                    amount = row['Amount'].replace('₹', '').replace(',', '').strip()

                    # Clean the amount in billing records for comparison
                    billing_records['Cleaned Amount'] = billing_records['Amount'].astype(str).str.replace('₹', '').str.replace(',', '').str.strip()

                    # Initialize a flag to check if a match is found
                    match_found = False

                    # Compare each entry in billing_records with the current row in parsed_df
                    for _, billing_row in billing_records.iterrows():
                        billing_company_name = billing_row['Company Name']
                        billing_amount = float(billing_row['Cleaned Amount'])

                        # Check for a match
                        if billing_company_name == company_name and billing_amount == float(amount):
                            st.success(f"Match found for Company Name: {company_name} with Amount: {amount}")
                            match_found = True
                            break  # Exit the loop if a match is found
                    if not match_found:
                        c2 = 1
                        st.warning(f"No match found for Company Name: {company_name} with Amount: {amount}")

        else:
            st.warning("No valid data was parsed from the uploaded files.")
if ((c1 == 0) and (c2 == 0)):
    if st.button('Generate'):
        file_path = "/home/darling/Documents/audity/vouchers/Balancesheetnit3.csv" 
        report.generate_audit_report_from_file(file_path) 
# The code continues from the previous implementation, ensuring the hash checking functionality is integrated.

# Additional logic to handle the case where no files are uploaded
if not uploaded_files and st.button("Check Hashes"):
    st.warning("Please upload PDF or image files to check hashes.")

# Finalize the Streamlit app
if st.button("Clear Data"):
    all_data.clear()
    st.success("Data cleared successfully.")
