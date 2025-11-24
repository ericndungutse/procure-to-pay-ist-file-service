import json
from openai import OpenAI
import re
from typing import Any

from config import get_openai_api_key


def _get_attr(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


# Initialize OpenAI client with API key from environment variable
client = OpenAI(api_key=get_openai_api_key())



class OpenAIService:
    @staticmethod
    def generate_purchase_order_dict(purchase_request, proforma_text):

        prompt = f"""
You are an assistant that extracts structured Purchase Order data from a purchase request and a proforma invoice.
Given the following Purchase Request information:
- ID: {_get_attr(purchase_request, 'id')}
- Title: {_get_attr(purchase_request, 'title')}
- Description: {_get_attr(purchase_request, 'description')}
- Amount: {_get_attr(purchase_request, 'amount')}

And the following Proforma Invoice Text:
{proforma_text}

Return a JSON object with the following fields:
- title
- description
- amount
- vendor_name
- vendor_address
- items (list of items with name, quantity, unit_price)
- total

Ensure the JSON is properly formatted and parsable.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # safer if GPT-4 access is not available
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        content = response.choices[0].message.content.strip()

        # Remove Markdown code fences if present
        content = re.sub(r"^```json\s*|\s*```$", "", content, flags=re.MULTILINE).strip()

        try:
            po_dict = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse OpenAI response as JSON:\n{content}") from e

        return po_dict
