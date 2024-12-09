from flask import Flask, send_file, render_template, request, redirect, url_for, jsonify
from bs4 import BeautifulSoup
from flask_cors import CORS
from functools import wraps
from fpdf import FPDF
import threading
import requests
import logging
import ollama
import uuid
import os

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    # Render the homepage with the form to input the website URL
    return render_template('index.html')

# Define the username and password for Basic Authentication
USERNAME = "username"
PASSWORD = "password"

# Ollama configuration
model = 'gemma2:2b'
messages = []

# Roles for chat history
USER = 'user'
ASSISTANT = 'assistant'

# Counter for document naming
counter = 0

@app.route('/submit', methods=['POST'])
def submit():
    # Get the company website URL from the form submission
    company_website = request.form['companyWebsite']

    print(f"Processing company website locally for links: {company_website}")

    # Perform local scraping to extract links
    try:
        # Scrape the links from the website
        extracted_links = extract_links(company_website)

        # Optionally, save the links or process them further
        scrape_links_full_text(company_website, extracted_links)

    except Exception as e:

        print(f"ERROR: {e}")

    # Redirect back to home page
    return redirect(url_for('index'))

def extract_links(url):
    """
    Extracts all hyperlinks (anchor tags) from the given URL.

    Args:
    - url (str): The URL of the website to scrape.

    Returns:
    - list: A list of unique links found on the website.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an error for bad responses

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all anchor tags and extract href attributes
    links = set()
    for anchor in soup.find_all('a', href=True):
        href = anchor['href']
        # Resolve relative links to absolute URLs
        full_url = requests.compat.urljoin(url, href)
        links.add(full_url)

    return list(links)


# Authentication Functions
def check_auth(username, password):
    return username == USERNAME and password == PASSWORD


def authenticate():
    return jsonify({"message": "Authentication required"}), 401


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


# Ollama Chat Helper Functions
def add_history(content, role):
    messages.append({'role': role, 'content': content})


def chat(message):
    add_history(message, USER)
    response = ollama.chat(model=model, messages=messages, stream=True)
    complete_message = ''
    for line in response:
        complete_message += line['message']['content']
    add_history(complete_message, ASSISTANT)
    return complete_message

# Function to scrape links using BeautifulSoup
def scrape_links_full_text(links):
    """
    Takes a list of links and scrapes the complete text content using BeautifulSoup.

    Args:
    - links (list): A list of URLs to scrape.

    Returns:
    - dict: A dictionary containing the URL and scraped text content.
    """
    scraped_data = {}

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for link in links:
        try:
            # Request the content of the URL
            response = requests.get(link, headers=headers)
            response.raise_for_status()  # Raise an HTTPError for bad responses

            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract the full text content of the page
            full_text = soup.get_text(separator='\n', strip=True)

            # Store scraped information in dictionary
            scraped_data[link] = {
                "full_text": full_text
            }

        except requests.exceptions.RequestException as e:
            # Handle request exceptions (e.g., network issues, page not found)
            scraped_data[link] = {
                "error": f"Failed to retrieve page: {str(e)}"
            }

    return scraped_data

@app.route('/check_status/<filename>', methods=['GET'])
@requires_auth
def check_status(filename):
    # Check if the file exists on the server
    pdf_path = filename
    if os.path.exists(pdf_path):
        return jsonify({"status": "ready"}), 200
    else:
        return jsonify({"status": "processing"}), 202


# Function to create PDF from LLM output
# Function to create PDF from LLM output
def create_pdf_from_llm_output(llm_output, output_filename='sales_prospect_report.pdf'):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_title("Sales Prospect Research Report")

    # Add your custom font
    # Make sure you have a TTF font in your directory, e.g., 'DejaVuSans.ttf'
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)

    # Add title page
    pdf.add_page()
    pdf.set_font("DejaVu", '', 16)
    pdf.cell(0, 10, "Sales Prospect Research Report", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("DejaVu", '', 12)
    pdf.cell(0, 10, "Generated Report for Sales Team", ln=True, align='C')
    pdf.ln(20)

    pdf.set_font("DejaVu", '', 12)

    # Process the LLM output to structure it within the PDF
    lines = llm_output.split('\n')
    for line in lines:
        line = line.strip()
        if line == "":
            pdf.ln(5)
        else:
            if line.lower().startswith(("introduction", "products/services", "success stories", "value proposition")):
                pdf.set_font("DejaVu", '', 14)
                pdf.cell(0, 10, line, ln=True)
                pdf.set_font("DejaVu", '', 12)
                pdf.ln(5)
            else:
                pdf.multi_cell(0, 10, line)

    pdf.output(output_filename)

# Function to Process Data in the Background
def process_in_background(scrap_links, output_filename):
    with app.app_context():
        try:
            # Construct the sales suggestion prompt for Ollama
            prompt_sales = (
                f"Identify which of the following links would be most useful for creating a sales document. "
                f"Specifically, prioritize links that contain information about the company's background (such as 'About Us' or the LinkedIn page if available), "
                f"product offerings, customer success stories, or any specific value propositions. "
                f"Provide 5 links that have these characteristics, separate them using a comma and write nothing else: {scrap_links}"
            )

            # Get response from Ollama
            ollama_response_sales = chat(prompt_sales)

            # Split suggestions into list of links
            suggested_links = ollama_response_sales.split(',')

            # Scrape each suggested link using BeautifulSoup
            scraped_results = scrape_links_full_text(suggested_links)

            prompt_document = f"""
            Using the following information extracted from various sections of the company's website, create a concise, informative article intended for a sales team. The article should help the sales team understand the company's background, its core offerings, key strengths, and any relevant success stories.

            **Objective**: Automate prospect research by providing a well-crafted summary that highlights the most important points about the prospect company for a sales pitch. Include details such as:
            - The company's mission and vision.
            - Products or services offered, focusing on what distinguishes them from competitors.
            - Success stories, case studies, or notable clients.
            - Key value propositions that would be relevant in a sales conversation.

            **Instructions for Filtering and Reasoning**:
            1. Carefully filter out redundant information and focus on content that would be persuasive in a sales pitch.
            2. Highlight the unique aspects of the company’s products/services that align with customer needs.
            3. Summarize only the relevant aspects that give insights into the company’s values, goals, and customer relationships.
            4. Make it like a report for a sales team, not a propaganda to convince someone, but an objective report of what the company offers.
            5. All the information include must be available in the extracted content, do not include parts to insert more info, as this is the final version.
            6. Do not talk about our, but their mission, their customers, etc.

            Here is the extracted content:

            {scraped_results}

            ---

            **Desired Structure**:
            1. **Introduction**: Provide a summary of the company, including its mission, vision, and overall objectives.
            2. **Products/Services**: Outline the company's core offerings, emphasizing any products/services that differentiate it from others.
            3. **Value Proposition**: Summarize key value propositions that are important for the sales team to understand for pitching.

            Use this to produce a concise, informative article about this prospect for the sales team.
            """

            # Get response from Ollama
            ollama_document = chat(prompt_document)

            # Create a PDF report from the LLM output
            create_pdf_from_llm_output(ollama_document, output_filename=output_filename)

            # Logging a success message
            logging.info(f"PDF generated successfully: {output_filename}")

        except Exception as e:
            logging.error("Error while processing data in background: %s", str(e))


@app.route('/download/<filename>', methods=['GET'])
@requires_auth
def download(filename):
    try:
        pdf_path = filename
        if not os.path.exists(pdf_path):
            return jsonify({"error": "PDF not found"}), 404

        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        logging.error("Error while sending PDF for download: %s", str(e))
        return jsonify({"error": "Failed to download PDF"}), 400


# Flask Endpoint for Receiving Initial Request
@app.route('/process', methods=['POST'])
@requires_auth
def process():
    # Log headers and data to understand what is being received
    logging.debug("Headers: %s", request.headers)
    logging.debug("Data received: %s", request.data)

    # Check if Content-Type starts with application/json
    if not request.content_type or not request.content_type.startswith('application/json'):
        return jsonify({"error": "Invalid content type. Expected application/json"}), 400

    # Attempt to parse JSON data
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        # Extract 'scrapLinks' from JSON data
        scrap_links = data.get('scrapLinks', None)

        if not scrap_links:
            return jsonify({"error": "Missing 'scrapLinks' key in JSON data"}), 400

        # Create a unique filename for the PDF
        unique_id = str(uuid.uuid4())  # Use UUID to create unique identifier for PDF
        output_filename = f"sales_prospect_report_{unique_id}.pdf"

        # Start background thread to process data with Flask app context
        background_thread = threading.Thread(target=process_in_background, args=(scrap_links, output_filename))
        background_thread.start()

        # Respond to the client with the unique identifier for polling
        return jsonify({"status": "Processing started", "filename": output_filename}), 200

    except Exception as e:
        logging.error("Error while processing request: %s", str(e))
        return jsonify({"error": "Failed to parse JSON data"}), 400



if __name__ == '__main__':
    app.run(debug=True, port=5000)
