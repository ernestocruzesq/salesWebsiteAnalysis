import ollama

model = 'gemma2:2b'
messages = []
# Roles
USER = 'user'
ASSISTANT = 'assistant'

def add_history(content, role):
    messages.append({'role': role, 'content': content})

def chat(message):
    add_history(message, USER)
    response = ollama.chat(model=model, messages=messages, stream=True)
    complete_message = ''
    for line in response:
        complete_message += line['message']['content']
        print(line['message']['content'], end='', flush=True)
    add_history(complete_message, ASSISTANT)


prompt = "'https://scale.com/,https://scale.com/leaderboard,https://scale.com/data-engine,https://scale.com/generative-ai-data-engine,https://scale.com/public-sector-data-engine,https://scale.com/automotive,https://scale.com/donovan,https://scale.com/genai-platform,https://scale.com/evaluation/model-developers,https://scale.com/evaluation/model-developers,https://scale.com/evaluation/public-sector,https://scale.com/evaluation/enterprise,https://scale.com/genai-platform,https://scale.com/enterprise/generative-ai-solutions,https://scale.com/evaluation/model-developers,https://scale.com/enterprise/prebuilt-applications,https://scale.com/defense,https://scale.com/federal,https://scale.com/public-sector,https://scale.com/about,https://scale.com/contact-us,https://scale.com/security,https://scale.com/blog,https://scale.com/guides,https://scale.com/events,https://scale.com/careers,https://scale.com/docs,https://scale.com/research,https://scale.com/ai-readiness-report,https://scale.com/blog/how-to-label-1m-data-points-week,https://scale.com/customers,https://scale.com/customers/toyota,https://scale.com/customers/brex,https://scale.com/customers/flexport,https://scale.com/customers/opensea,https://scale.com/customers,https://scale.com/leaderboard,https://scale.com/demo,https://dashboard.scale.com/login,https://scale.com/demo,https://scale.com/data-engine,https://scale.com/leaderboard,https://www.scale.com/research/browser-art,https://scale.com/research/mhj,https://arxiv.org/pdf/2403.03218,https://arxiv.org/html/2405.00332v1,https://arxiv.org/html/2407.13887v1,https://scale.com/demo,https://scale.com/rlhf,https://dashboard.scale.com/signup?product=rapid&redirect_url=%2Frapid,https://dashboard.scale.com/nucleus,https://scale.com/donovan,https://scale.com/genai-platform,https://scale.com/blog/open-ai-scale-partnership-gpt-3-5-fine-tuning,https://www.anthropic.com/news/partnering-with-scale,https://scale.com/blog/meta-llama-3-1-launch-partner,https://scale.com/customers/nvidia,https://scale.com/customers/cohere,https://scale.com/blog/leaderboard,https://scale.com/blog/chatgpt-reinforcement-learning,https://scale.com/blog/ukraine-detection,https://scale.com/blog/chatgpt-vs-claude,https://scale.com/blog/gpt-3-davinci-003-comparison,https://scale.com/customers/toyota,https://scale.com/blog/how-to-label-1m-data-points-week,https://scale.com/demo,https://scale.com/data-engine,https://scale.com/data-engine,https://scale.com/genai-platform,https://scale.com/donovan,https://scale.com/defense,https://scale.com/federal,https://scale.com/public-sector,https://scale.com/about,https://scale.com/careers,https://scale.com/security,https://scale.com/legal/terms,https://scale.com/legal/privacy,https://scale.com/blog,https://scale.com/contact-us,https://scale.com/customers,https://scale.com/events,https://scale.com/open-av-datasets,https://scale.com/docs,https://scale.com/guides,https://exchange.scale.com/,https://scale.com/ai-readiness-report,https://scale.com/research/mhj,https://scale.com/guides/data-labeling-annotation-guide,https://scale.com/guides/model-training-building,https://scale.com/guides/diffusion-models-guide,https://scale.com/guides/ai-for-ecommerce,https://scale.com/guides/computer-vision,https://scale.com/guides/large-language-models,https://x.com/scale_ai,https://www.facebook.com/scaleapi,https://www.linkedin.com/company/scaleai,https://scale.com/legal/terms,https://scale.com/legal/privacy':Identify which of the following links would be most useful for creating a sales document. Specifically, prioritize links that contain information about the company's background (such as 'About Us' and its LinkedIn page if available), product offerings, customer success stories, or any specific value propositions. Provide 5 links that have these characteristics, separate them using a comma and write nothing else."
chat(prompt)
