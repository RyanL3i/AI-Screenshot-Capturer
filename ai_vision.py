import sys
import base64
import requests
import os
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
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": """
This screenshot was taken by an employee at StoneX Group as part of a company-wide effort to streamline workflows, reduce cognitive overhead, and improve day-to-day productivity across departments. Please analyze the screenshot and determine what the user is working on based on the visible applications, layout, content, and context.

Your response should include the following:

1. **Task Detection**  
   Identify the task the user is likely performing. Be specific if possible (e.g., composing an email, reading a financial report, debugging code, entering client data, etc.). Identify what phase they are in (starting, mid-task, reviewing, copying, etc.).

2. **Context-Aware Insight & Friction Points**  
   Point out any inefficiencies or pain points — such as manual data entry, switching between tools or browser tabs, keeping temporary information in memory, or unclear UI. Mention any signs the user is juggling multiple pieces of information or may forget something.

3. **Memory Support & Tracking Suggestions**  
   Describe how this user could benefit from automated memory aids — like reminders, AI-generated summaries, inline assistants, or context-aware overlays that help them keep track of names, numbers, links, instructions, etc.

4. **Smart AI Productivity Boosters — Based on What You See**  
   Based on the content type in the screenshot, apply the following logic:
   - **If you see an article, PDF, or webpage:** summarize the key points and suggest how the user could automate follow-up (e.g., “add to reading list,” “extract insights,” “track related documents”).
   - **If you see code or a terminal window:** explain what the code does, and suggest improvements or shortcuts (e.g., automation, linting, version control).
   - **If you see email or messaging apps:** suggest how to draft a response, prioritize items, or convert tasks into action steps.
   - **If you see dashboards, charts, or Excel files:** provide a high-level summary of what’s shown and suggest relevant trends, anomalies, or possible alerts.
   - **If it’s a form, database, or internal system:** check if there are fields that look repetitive or could be autofilled or remembered.

5. **StoneX-Aware Suggestions**  
   Tailor your suggestions with the understanding that this is a financial services firm. Be mindful of workflows in trading, operations, compliance, finance, and technology. Suggest automations that could enhance data accuracy, reduce time spent on routine tasks, or improve cross-tool visibility.

Keep your response clear, actionable, and helpful — as if you're assisting the user live, in real time, by reducing mental load and helping them finish their task faster.
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

# Send request to OpenAI
response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)

# Print formatted output
try:
    result = response.json()

    if "choices" in result and result["choices"]:
        raw = result["choices"][0]["message"]["content"]
        pretty = raw.strip()

        # Improve formatting
        pretty = pretty.replace("**", "")  # remove markdown bold
        pretty = pretty.replace(" - ", "\n• ")  # make bullets
        pretty = pretty.replace("\n", "\n\n")  # spacing between points

        print(pretty)
    else:
        print("❌ Unexpected OpenAI response format", file=sys.stderr)

except Exception as e:
    print("❌ Failed to parse OpenAI response:", e, file=sys.stderr)
