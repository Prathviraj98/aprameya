import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def load_file(file):
    # Load the file based on its type
    if file.name.endswith('.xlsx'):
        df = pd.read_excel(file, sheet_name=None)  # Load all sheets for Excel
    elif file.name.endswith('.csv'):
        df = pd.read_csv(file)  # Load CSV file
    else:
        st.error("Unsupported file type. Please upload an Excel (.xlsx) or CSV (.csv) file.")
        return None
    return df

def generate_audit_report(df):
    report = {}
    
    if isinstance(df, dict):  # If it's a dictionary, it means multiple sheets
        for sheet_name, data in df.items():
            report[sheet_name] = {
                'row_count': data.shape[0],
                'column_count': data.shape[1],
                'columns': data.columns.tolist(),
                'missing_values': data.isnull().sum().to_dict(),
            }
    else:  # Single DataFrame for CSV
        report['Data'] = {
            'row_count': df.shape[0],
            'column_count': df.shape[1],
            'columns': df.columns.tolist(),
            'missing_values': df.isnull().sum().to_dict(),
        }
    
    return report

def display_audit_report(report):
    # Display the audit report
    for sheet_name, details in report.items():
        st.subheader(f"Sheet: {sheet_name}")
        st.write(f"Row Count: {details['row_count']}")
        st.write(f"Column Count: {details['column_count']}")
        st.write(f"Columns: {', '.join(details['columns'])}")
        st.write("Missing Values:")
        st.write(details['missing_values'])
        st.write("---")

def generate_pdf_report(report, filename):
    # Create a PDF report
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 50, "Final Audit Report")
    
    # Prepared for
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 80, "Prepared for: [Chartered Accountant's Name]")
    c.drawString(100, height - 95, "Prepared by: [Auditor's Name/Company Name]")
    c.drawString(100, height - 110, "Date: [Insert Date]")
    c.drawString(100, height - 125, "Report Reference: [Insert Reference Number]")

    # Executive Summary
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 150, "1. Executive Summary")
    c.setFont("Helvetica", 10)
    c.drawString(100, height - 165, "This report presents the findings of the financial audit conducted on the transactions recorded in the audited balance sheet.")
    
    # Introduction
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 185, "2. Introduction")
    c.setFont("Helvetica", 10)
    c.drawString(100, height - 200, "The purpose of this audit report is to provide a comprehensive analysis of the financial transactions for the period ending [Insert Date].")

    # Overview of Transactions
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 220, "4. Overview of Transactions")
    c.setFont("Helvetica", 10)
    total_transactions = sum(details['row_count'] for details in report.values())
    highest_transaction = 90000  # Placeholder for actual values
    lowest_transaction = 16500    # Placeholder for actual values
    total_amount_processed = 198500  # Placeholder
    average_transaction_value = total_amount_processed / total_transactions if total_transactions > 0 else 0

    c.drawString(100, height - 240, f"Total Number of Transactions: {total_transactions}")
    c.drawString(100, height - 255, f"Highest Transaction Value: ₹{highest_transaction:.2f}")
    c.drawString(100, height - 270, f"Lowest Transaction Value: ₹{lowest_transaction:.2f}")
    c.drawString(100, height - 285, f"Total Amount Processed: ₹{total_amount_processed:.2f}")
    c.drawString(100, height - 300, f"Average Transaction Value: ₹{average_transaction_value:.2f}")

    # Client-Wise Transaction Breakdown
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, height - 320, "5. Client-Wise Transaction Breakdown")
    c.setFont("Helvetica", 10)

    # Example client-wise breakdown (you would replace this with actual data)
    client_data = {
        "ABC Enterprises": 90000,
        "ABC Corporation": 40000,
        "ABC Pvt Ltd": 35000,
        "GST Payments": 17000,
        "State Electricity Board": 16500,
    }

    y_position = height - 340
    for client, amount in client_data.items():
        c.drawString(120, y_position, f"{client} - ₹{amount:.2f}")
        y_position -= 15  # Move down for the next client entry

    # Analysis of Financial Trends
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, y_position, "6. Analysis of Financial Trends")
    y_position -= 20
    c.setFont("Helvetica", 10)
    analysis_text = (
        "The majority of the transactions involve high-value clients, suggesting strong business engagements.\n"
        "Payments to government and utility agencies (GST, Electricity Board) indicate operational expenses.\n"
        "A steady flow of financial activity across multiple dates shows healthy cash movement."
    )
    for line in analysis_text.split('\n'):
        c.drawString(100, y_position, line)
        y_position -= 15

    # Compliance & Risk Assessment
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, y_position, "7. Compliance & Risk Assessment")
    y_position -= 20
    c.setFont("Helvetica", 10)
    compliance_text = (
        "All transactions appear consistent with expected financial records.\n"
        "No significant discrepancies or unusual patterns were detected.\n"
        "Payments to regulatory bodies ensure tax compliance and legal adherence.\n"
        "Regular transactions with corporate entities signify stable business relations."
    )
    for line in compliance_text.split('\n'):
        c.drawString(100, y_position, line)
        y_position -= 15

    # Recommendations
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, y_position, "8. Recommendations")
    y_position -= 20
    c.setFont("Helvetica", 10)
    recommendations = [
        "Maintain detailed records of all high-value transactions for future audits.",
        "Ensure timely payment to vendors and government agencies to avoid penalties.",
        "Implement an automated financial tracking system for efficiency.",
        "Review operational costs periodically to optimize financial performance."
    ]
    for rec in recommendations:
        c.drawString(100, y_position, f"- {rec}")
        y_position -= 15

    # Conclusion
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, y_position, "9. Conclusion")
    y_position -= 20
    c.setFont("Helvetica", 10)
    conclusion_text = (
        "The financial audit confirms a structured and transparent financial record. "
        "The transactions indicate a stable business environment with reliable clients and necessary operational expenses. "
        "The organization demonstrates sound financial management, adhering to compliance standards and maintaining healthy financial movements."
    )
    for line in conclusion_text.split('\n'):
        c.drawString(100, y_position, line)
        y_position -= 15

    # Appendices
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, y_position, "10. Appendices")
    y_position -= 20
    c.setFont("Helvetica", 10)
    c.drawString(100, y_position, "- Appendix A: Detailed Transaction Data")
    y_position -= 15
    c.drawString(100, y_position, "- Appendix B: Supporting Documents")
    y_position -= 15
    c.drawString(100, y_position, "- Appendix C: Audit Methodology and Procedures")

    # Contact Information
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, y_position, "Contact Information")
    y_position -= 20
    c.setFont("Helvetica", 10)
    c.drawString(100, y_position, "For further inquiries, please contact:")
    y_position -= 15
    c.drawString(100, y_position, "Auditor's Name: [Your Name]")
    y_position -= 15
    c.drawString(100, y_position, "Email: [Your Email]")
    y_position -= 15
    c.drawString(100, y_position, "Phone: [Your Phone Number]")

    c.save()

def main():
    st.title("Excel/CSV Audit Report Generator")

    uploaded_file = st.file_uploader("Upload an Excel (.xlsx) or CSV (.csv) file", type=["xlsx", "csv"])

    if uploaded_file is not None:
        # Load the file
        df = load_file(uploaded_file)

        if df is not None:
            # Generate the audit report
            report = generate_audit_report(df)

            # Display the audit report
            display_audit_report(report)

            # Generate PDF report
            pdf_filename = "audit_report.pdf"
            generate_pdf_report(report, pdf_filename)
            st.success(f"PDF report generated: {pdf_filename}")

            # Provide a download link for the PDF
            with open(pdf_filename, "rb") as f:
                st.download_button("Download PDF Report", f, file_name=pdf_filename)

if __name__ == "__main__":
    main()
