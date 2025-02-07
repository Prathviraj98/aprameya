import streamlit as st
import pandas as pd
import uuid
from fpdf import FPDF
from datetime import datetime
import re
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

st.set_page_config(
    page_title="Bilgen",
    page_icon="logo.png"
)

# Function to generate a unique alphanumeric ID
def generate_unique_id():
    return str(uuid.uuid4()).replace("-", "").upper()[:10]

# Function to create a PDF bill
def create_pdf(bill_data):
    pdf = FPDF()
    pdf.add_page()
    
    # Set font
    pdf.set_font("Arial", size=12)
    
    # Add unique ID
    pdf.cell(200, 10, txt=f"Unique ID: {bill_data['Unique ID']}", ln=True, align='L')
    
    # Add company name
    pdf.cell(200, 10, txt=f"Company Name: {bill_data['Company Name']}", ln=True, align='L')
    
    # Add date
    pdf.cell(200, 10, txt=f"Date: {bill_data['Date']}", ln=True, align='L')
    
    # Add serial number
    pdf.cell(200, 10, txt=f"Serial Number: {bill_data['serial_number']}", ln=True, align='L')
    
    # Add products/services
    pdf.cell(200, 10, txt="Products/Services:", ln=True, align='L')
    for product in bill_data['products']:
        pdf.cell(200, 10, txt=f"{product['name']} - {product['price']:.2f}", ln=True, align='L')
    
    # Add Amount
    pdf.cell(200, 10, txt=f"Total: {bill_data['Total']:.2f}", ln=True, align='L')
    
    # Save the PDF
    pdf_file_name = f"bill_{bill_data['Unique ID']}.pdf"
    pdf.output(pdf_file_name)
    
    return pdf_file_name

# Function to validate PAN number
def validate_pan(pan):
    pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]$'
    return re.match(pan_pattern, pan) is not None

# Streamlit app
def main():
    st.title("Billing Application")
    
    # Input fields
    company_name = st.text_input("Enter Company Name:")
    pan_number = st.text_input("Enter PAN Number (Format: ABCDE1234F):")
    
    # Initialize session state for products
    if 'products' not in st.session_state:
        st.session_state.products = []
    
    # Product input fields
    product_name = st.text_input("Enter Product/Service Name:")
    price = st.number_input("Enter Price:", min_value=0.0, format="%.2f")
    
    if st.button("Add Product"):
        if product_name and price >= 0:
            st.session_state.products.append({'name': product_name, 'price': price})
            st.success(f"Added {product_name} - {price:.2f}")
        else:
            st.error("Please fill in both product name and price.")
    
    # Display added products
    if st.session_state.products:
        st.write("### Added Products:")
        for idx, product in enumerate(st.session_state.products):
            st.write(f"{idx + 1}. {product['name']} - {product['price']:.2f}")
    
    if st.button("Generate Bill"):
        if validate_pan(pan_number) and st.session_state.products and company_name:
            # Generate unique ID and serial number
            unique_id = generate_unique_id()
            date = datetime.now().strftime("%Y-%m-%d")
            serial_number = f"SN{int(datetime.now().timestamp())}"  # Simple serial number based on timestamp
            
            # Calculate Amount
            Amount = sum(product['price'] for product in st.session_state.products)
            
            # Prepare bill data
            bill_data = {
                'Unique ID': unique_id,  # Changed from 'unique_id' to 'Unique ID'
                'Date': date,
                'serial_number': serial_number,
                'products': st.session_state.products,
                'Total': Amount,
                'pan_number': pan_number,  # Save PAN number
                'Company Name': company_name  # Save company name
            }
            
            # Create PDF
            pdf_file_name = create_pdf(bill_data)
            st.success("Bill generated successfully!")
            
            # Read the PDF file to provide a download option
            if os.path.exists(pdf_file_name):
                with open(pdf_file_name, "rb") as pdf_file:
                    st.download_button(
                        label="Download Bill",
                        data=pdf_file,
                        file_name=pdf_file_name,
                        mime="application/pdf"
                    )
            else:
                st.error("Error: PDF file not found.")
            
            # Save record to CSV with utf-8 encoding
            df = pd.DataFrame([{
                'Unique ID': unique_id,  # Changed from 'unique_id' to 'Unique ID'
                'Date': date,
                'serial_number': serial_number,
                'Amount': Amount,
                'pan_number': pan_number,  # Include PAN number in CSV
                'Company Name': company_name  # Include company name in CSV
            }])
            try:
                df.to_csv('billing_records.csv', mode='a', header=not pd.io.common.file_exists('billing_records.csv'), index=False, encoding='utf-8')
                st.success("Record saved to billing_records.csv")
            except Exception as e:
                st.error(f"Error saving to CSV: {e}")
        else:
            st.error("Please fill in all fields correctly. Ensure PAN number is in the correct format (ABCDE1234F), company name is provided, and at least one product is added.")

if __name__ == "__main__":
    main()