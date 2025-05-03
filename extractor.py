from openai import OpenAI
from config import OPENAI_API_KEY
import json

client = OpenAI(api_key=OPENAI_API_KEY)

def extract_fields_from_transcript(transcript):
    system_prompt = """
You are an expert mortgage assistant.
Your job is to extract standardized 1003 mortgage application form fields from transcripts.

For each field, return:
- field_name (string)
- field_value (string)
- confidence_score (float from 0 to 1)
- short_explanation (max 20 words explaining how you found it)

⚠️ Return ONLY a valid JSON array like this:

[
  {
    "field_name": "Borrower Name",
    "field_value": "Michael Harris",
    "confidence_score": 0.95,
    "short_explanation": "Introduced himself clearly by name."
  },
  {
    "field_name": "Loan Amount",
    "field_value": "$400,000",
    "confidence_score": 0.90,
    "short_explanation": "Said 'I'd like to borrow around $400,000'."
  }
]
"""
    user_prompt = f"""
Transcript:
\"\"\"{transcript}\"\"\"

Extract the fields as per instructions above. Do not return anything else.
"""

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )

    raw_content = response.choices[0].message.content.strip()

    try:
        parsed = json.loads(raw_content)
        if isinstance(parsed, list):
            return parsed
        else:
            print("❌ Expected a list. Got:", type(parsed))
            return []
    except json.JSONDecodeError as e:
        print("❌ JSON Decode Error:", e)
        print("🔍 Raw GPT response:")
        print(raw_content)
        return []
