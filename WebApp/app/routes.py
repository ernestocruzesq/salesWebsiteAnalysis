from flask import Blueprint, render_template, request, jsonify, redirect, url_for, send_file, current_app
from .auth import requires_auth
from .services.processsing import process_in_background
import threading
import uuid
import os
import logging


main = Blueprint('main', __name__)

PDF_DIRECTORY = 'app/documents'

@main.route('/')
def index():
    # Render the homepage with the form to input the website URL
    return render_template('index.html')


@main.route('/submit', methods=['POST'])
def submit():

    company_website = request.form.get('companyWebsite')  # Retrieve form data
    if not company_website:
        return jsonify({"error": "No company website provided"}), 400

    # Redirect back to home page
    return redirect(url_for('index'))

@main.route('/check_status/<filename>', methods=['GET'])
@requires_auth
def check_status(filename):
    # Check if the file exists on the server
    pdf_path = os.path.join(PDF_DIRECTORY, filename)

    if os.path.exists(pdf_path):
        return jsonify({"status": "ready"}), 200
    else:
        return jsonify({"status": "processing"}), 202


@main.route('/download/<filename>', methods=['GET'])
@requires_auth
def download(filename):
    try:
        pdf_path = os.path.join(os.getcwd(), PDF_DIRECTORY, filename)

        if not os.path.exists(pdf_path):
            return jsonify({"error": "PDF not found"}), 404

        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        logging.error("Error while sending PDF for download: %s", str(e))
        return jsonify({"error": "Failed to download PDF"}), 400


# Flask Endpoint for Receiving Initial Request
@main.route('/process', methods=['GET', 'POST'])
@requires_auth
def process():

    # Check if Content-Type starts with application/json
    if not request.content_type or not request.content_type.startswith('application/json'):
        return jsonify({"error": "Invalid content type. Expected application/json"}), 400

    # Attempt to parse JSON data
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        # Extract 'companyWebsite' from JSON data
        company_website = data.get('companyWebsite', None)

        if not company_website:
            return jsonify({"error": "Missing 'companyWebsite' key in JSON data"}), 400

        # Create a unique filename for the PDF
        unique_id = str(uuid.uuid4())  # Use UUID to create unique identifier for PDF

        output_filename = f'sales_prospect_report_{unique_id}.pdf'

        output_filepath = os.path.join(os.path.dirname(__file__), 'documents', output_filename)

        # Start background thread to process data with Flask app context
        background_thread = threading.Thread(target=process_in_background, args=(company_website, output_filepath, current_app._get_current_object()))
        background_thread.start()

        # Respond to the client with the unique identifier for polling
        return jsonify({"status": "Processing started", "filename": output_filename}), 200

    except Exception as e:
        logging.error("Error while processing request: %s", str(e))
        return jsonify({"error": "Failed to parse JSON data"}), 400
