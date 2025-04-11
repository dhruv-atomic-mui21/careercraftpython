from flask import Flask, request, jsonify
import requests
from io import BytesIO
import PyPDF2

app = Flask(__name__)

EXTERNAL_API_URL = "https://magicloops.dev/api/loop/fe2ef75f-80fa-4d1c-82a6-ca4ebf4089a6/run"

@app.route("/get-text", methods=["GET"])
def fetch_pdf_and_send_to_api():
    # Get PDF URL from query param
    pdf_url = request.args.get("pdf_url")
    if not pdf_url:
        return jsonify({"error": "Missing 'pdf_url' query parameter."}), 400

    try:
        # Step 1: Download PDF
        response = requests.get(pdf_url)
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
            return jsonify({"error": "No text could be extracted from the PDF."}), 400

        # Step 3: Send extracted text to Magic Loops API
        api_response = requests.post(EXTERNAL_API_URL, json={"input": text_content})
        api_response.raise_for_status()

        # Step 4: Return Magic Loops response
        return jsonify(api_response.json())

    except requests.RequestException as e:
        print("Error:", e)
        return jsonify({"error": "Something went wrong while fetching or sending data."}), 500


@app.route("/analyze-text", methods=["POST"])
def analyze_text():
    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' in request body."}), 400

    try:
        # Send text to external API
        api_response = requests.post(EXTERNAL_API_URL, json={"input": data["text"]})
        api_response.raise_for_status()

        return jsonify(api_response.json())
    except requests.RequestException as e:
        print("Error:", e)
        return jsonify({"error": "Failed to send data to external API."}), 500


if __name__ == "__main__":
    app.run(debug=False)
