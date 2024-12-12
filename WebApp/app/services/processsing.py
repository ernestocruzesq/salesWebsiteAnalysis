from .scraping import extract_links, scrape_links_full_text
from .ollama import chat
from .pdf_generator import create_pdf_from_llm_output
import logging


# Function to Process Data in the Background
def process_in_background(company_website, output_filepath, app):
    with app.app_context():
        try:
            # Get links
            scrap_links = extract_links(company_website)

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
            create_pdf_from_llm_output(ollama_document, output_filename=output_filepath)

            # Logging a success message
            logging.info(f"PDF generated successfully: {output_filepath}")

        except Exception as e:
            logging.error("Error while processing data in background: %s", str(e))