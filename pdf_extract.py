import fitz
from transformers import pipeline
import re
import pandas as pd


def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def extract_transaction_lines(text):
    # Match lines that include: MM/DD, description, and an amount (positive or negative)
    pattern = re.compile(r'\b\d{2}/\d{2}\b\s+.+?\s+-?\d+\.\d{2}')
    return pattern.findall(text)


def extract_structured_data(lines, model_name="google/flan-t5-small"):
    extractor = pipeline("text2text-generation", model=model_name)
    results = []

    for line in lines:
        prompt = f"Extract the date, description, and amount from this bank transaction: {line}"
        output = extractor(prompt, max_length=64)[0]['generated_text']
        results.append({
            "raw": line,
            "extracted": output
        })

    return results

def parse_structured_line(text):
    # Match format like: "MM/DD Description Amount"
    match = re.match(r"(\d{2}/\d{2})\s+(.+?)\s+(-?\d+\.\d{2})", text.strip())
    if match:
        date, description, amount = match.groups()
        return {
            "Date": date,
            "Description": description.strip(),
            "Amount": float(amount)
        }
    return None

def extract_transactions_from_pdf(file_path):
    # Step 1: Extract text from PDF
    pdf_text = extract_text_from_pdf(file_path)

    # Step 2: Parse out candidate transaction lines
    lines = extract_transaction_lines(pdf_text)

    # Step 3: Run transformer to structure each line
    structured = extract_structured_data(lines)

    # Step 4: Parse results
    clean_rows = []
    for entry in structured:
        parsed = parse_structured_line(entry["extracted"])
        if parsed:
            clean_rows.append(parsed)

    # Convert to DataFrame
    df = pd.DataFrame(clean_rows)
    return df

if __name__ == "__main__":
    df = extract_transactions_from_pdf("statement.pdf")
    print(f"Found {len(df)} transactions:")
    print(df.head())
    # Optional: Save to CSV
    df.to_csv("categorized_transactions.csv", index=False)
