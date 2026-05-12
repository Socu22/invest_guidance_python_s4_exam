from typing import Dict, Any, Optional
import os
import requests
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY: Optional[str] = os.getenv("MISTRAL_API_KEY")

MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"


def get_investment_advice(
    ticker: str,
    stock_data: Dict[str, Any],
    analysis: Dict[str, Any]
) -> str:
    """
    Get investment advice from Mistral AI (no SDK).
    """
    try:
        if not MISTRAL_API_KEY:
            return "Error: MISTRAL_API_KEY not configured."

        prompt = f"""
Analyze stock {ticker} with the following stock data:
{stock_data}

Technical analysis:
{analysis}

Provide:
1. Investment recommendation (Buy/Hold/Sell)
2. Key reasons
3. Risks to consider
"""

        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "mistral-small-latest",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        response = requests.post(
            MISTRAL_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            return f"Mistral API error {response.status_code}: {response.text}"

        data = response.json()

        return data["choices"][0]["message"]["content"]

    except requests.exceptions.RequestException as e:
        return f"HTTP error calling Mistral: {e}"
    except Exception as e:
        return f"Error generating advice: {e}"