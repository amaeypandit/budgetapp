import streamlit as st
import pandas as pd
import tempfile
from pdf_extract import extract_transactions_from_pdf

st.set_page_config(page_title="Bank Statement Extractor", layout="centered")
st.title("Bank Statement PDF to CSV Extractor")
st.write("Upload your bank statement PDF. The app will extract transactions and let you view and download them as a CSV.")

uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

# Use session state to persist the DataFrame
if 'df' not in st.session_state:
    st.session_state.df = None
    st.session_state.last_file = None

if uploaded_file is not None:
    # Only re-process if a new file is uploaded
    if (st.session_state.last_file is None) or (uploaded_file.name != st.session_state.last_file):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name
        with st.spinner("Extracting transactions. This may take a minute..."):
            try:
                df = extract_transactions_from_pdf(tmp_path)
                st.session_state.df = df
                st.session_state.last_file = uploaded_file.name
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.session_state.df = None
                st.session_state.last_file = None

if st.session_state.df is not None:
    df = st.session_state.df
    if df.empty:
        st.warning("No transactions found in the PDF.")
    else:
        st.success(f"Extracted {len(df)} transactions.")
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="categorized_transactions.csv",
            mime="text/csv"
        )
else:
    st.info("Please upload a PDF file to begin.") 