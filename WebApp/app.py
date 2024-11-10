from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    # Render the homepage with the form to input the website URL
    return render_template('index.html')

import requests
def trigger_zapier(company_website):
    webhook_url = 'https://hooks.zapier.com/hooks/catch/20661712/258qefn/'
    data = {"company_website": company_website}
    response = requests.post(webhook_url, json=data)
    return response.status_code

@app.route('/submit', methods=['POST'])
def submit():
    # Get the company website URL from the form submission
    company_website = request.form['companyWebsite']

    # Trigger Zapier webhook
    response_code = trigger_zapier(company_website)
    if response_code == 200:
        print("Zap triggered successfully.")
    else:
        print(f"Failed to trigger Zap: {response_code}")

    # Redirect back to home page or render a success page
    return redirect(url_for('index'))

@app.route('/process', methods=['POST'])
def process():
    # Debugging: Print headers and request data
    logging.debug("Headers: %s", request.headers)
    logging.debug("Data received: %s", request.data)

    # Content-Type validation
    if request.content_type != 'application/json':
        return jsonify({"error": "Invalid content type. Expected application/json"}), 400

    # Retrieve JSON data
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400

    scrap_links = data.get('scrapLinks', 'Unknown')
    response_message = f"Processed data for scraped link: {scrap_links}"

    return jsonify({"message": response_message})

    # # Retrieve data sent from Zapier
    # data = request.json
    # print("Request from IP:", request.remote_addr)
    # scrap_links = data.get('scrapLinks')
    #
    # # Process the data (this could be any kind of logic or data analysis)
    # response_message = f"Scrapped links: {scrap_links}"
    #
    # print(response_message)
    #
    # # Return the processed result back as JSON
    # return jsonify({"message": response_message})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
