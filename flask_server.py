from flask import Flask
import requests
from io import BytesIO
import PyPDF2

app = Flask(__name__)

EXTERNAL_API_URL = "https://magicloops.dev/api/loop/fe2ef75f-80fa-4d1c-82a6-ca4ebf4089a6/run"
PDF_URL = "https://res.cloudinary.com/dwhovyplx/raw/upload/v1744400084/resumes/pygtiezg3ndz1hiwc74r"

@app.route("/")
def fetch_and_send_to_api():
    try:
        # Step 1: Download PDF
        response = requests.get(PDF_URL)
        response.raise_for_status()

        # Step 2: Extract text from PDF
        pdf_file = BytesIO(response.content)
        reader = PyPDF2.PdfReader(pdf_file)

        text_content = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_content += page_text + "\n"

        if not text_content.strip():
            return "No text could be extracted from the PDF."

        # Step 3: Send extracted text to Magic Loops API
        api_response = requests.post(EXTERNAL_API_URL, json={"input": text_content})
        api_response.raise_for_status()

        # Step 4: Return Magic Loops response
        result = api_response.json()
        return f"<h2>Magic Loops API Output:</h2><pre>{result}</pre>"

    except requests.RequestException as e:
        print("Error:", e)
        return "An error occurred. Check the terminal for details.", 500

if __name__ == "__main__":
    app.run(debug=True)
