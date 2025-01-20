# Project Title: Sales Report Generator using LLM

## Description
This repository demonstrates the use of a Large Language Model (LLM) to generate a concise sales report by analyzing data from any home webpage. It showcases the integration of natural language processing for data extraction and report generation.

---

## Features
- Automatically parses sales data from a home webpage.
- Generates a structured and concise sales report.

---

## Installation
Follow these steps to set up the project locally:

1. **Clone the repository**  
   ```bash
   git clone https://github.com/ernestocruzesq/salesWebsiteAnalysis.git
   cd salesWebsiteAnalysis
   ```

2. **Create and activate a virtual environment**
It is recommended that a virtual environment be used to manage dependencies. Run the following commands:

   On macOS/Linux:
   ```bash
   python3 -m venv salesWebsiteAnalysis
   source salesWebsiteAnalysis/bin/activate
   ```

   On Windows:
   ```bash
   python -m venv salesWebsiteAnalysis
   salesWebsiteAnalysis\Scripts\activate
   ```

3. **Install dependencies**
Install the required libraries from the requirements.txt file by running:
   ```bash
   pip install -r requirements.txt
   ```
---

## Usage
To generate the PDF, start the web app running:
```bash
python run.py
```

Then, it will locally run in http://127.0.0.1:5000.

---
## WebApp Structure

```bash
app/
│  
├── documents/             # Generated PDFs are saved here
├── misecellaneous/        # Font data
├── services/        
│   ├── ollama.py          # The LLMs script and prompt
│   ├── pdf_generator.py   # The functions to generate the PDFs
│   ├── processing.py      # Background processing functions
│   └── scraping.py        # Scraping functions
├── templates/              
│   └── index.html         # Main web page design. 
├── auth.py                # Authorization functions
└── routes.py              
```
---
License

This project is licensed under the MIT License.

---
For questions or feedback, feel free to reach out:

      LinkedIn: https://www.linkedin.com/in/ernesto-cruz-694132160/
