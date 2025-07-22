import sys
import base64
import requests
import os
import json
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=dotenv_path, override=True)

# Load OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Missing OPENAI_API_KEY env var")
    sys.exit(1)

# Get image path from command-line argument
image_path = sys.argv[1]

# Read and encode image
with open(image_path, "rb") as img_file:
    base64_image = base64.b64encode(img_file.read()).decode("utf-8")

# Prepare request
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

data = {
    "model": "gpt-4o",
    "stream": True,
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": """
This is a screenshot of a stock report, equity research document, or financial summary. Please analyze the image and return a clear and structured breakdown with the following sections:

---

📊 Key Financial Highlights**
   - Pull out any financial metrics visible (e.g., revenue, net income, earnings per share, margins).
   - Mention YoY or QoQ changes if visible.
   - Identify if the company beat/missed expectations.

📈 Company Performance Summary**
   - Describe whether the company is doing well, poorly, or mixed — and why.
   - Include commentary on trends like growth, profit, costs, etc.

🎯 Stock Rating & Outlook**
   - If visible, extract analyst rating (e.g., Buy, Hold, Sell), target price, or sentiment.
   - Note any risks, opportunities, or sector-wide headwinds/tailwinds.

✅ Actionable Insight for a Financial Analyst**
   - Suggest one or two quick takeaways for a financial services professional (e.g., flag for further review, compare to competitors, log into CRM, update client briefing, etc.).

💬 Simple Explanation (Plain English)**
   - Translate the core message of the report into easy-to-understand terms, as if explaining to someone with no finance background.
   - Avoid jargon. Use analogies if helpful (e.g., "The company made more money than expected this quarter, mostly due to strong sales and keeping costs low.").

---

Keep your response concise, bulleted where possible, but without too many spaces between lines because right now there are
and aimed at helping a busy employee quickly understand and act on this report. Assume this is part of an internal productivity assistant for employees at **StoneX**, a financial services firm.
"""},

                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"
                    }
                }
            ]
        }
    ],
    "max_tokens": 1000
}

# Stream the response from OpenAI
try:
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=data,
        stream=True
    )

    for line in response.iter_lines():
        if line:
            line = line.decode("utf-8").strip().replace("data: ", "")
            if line == "[DONE]":
                break
            try:
                delta = json.loads(line)["choices"][0]["delta"]
                if "content" in delta:
                    print(delta["content"], end="", flush=True)
            except Exception:
                continue

except Exception as e:
    print("❌ Streaming failed:", e, file=sys.stderr)
