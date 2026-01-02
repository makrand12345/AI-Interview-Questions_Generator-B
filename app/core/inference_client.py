import os
import asyncio
import httpx
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InferenceClient:
    def __init__(self):
        self.api_key = os.getenv("HF_API_KEY")
        # Standard OpenAI-compatible router endpoint
        self.model_url = os.getenv(
            "HF_MODEL_URL", 
            "https://router.huggingface.co/v1/chat/completions"
        )
        self.model_id = "Qwen/Qwen2.5-Coder-32B-Instruct"
        self.timeout = httpx.Timeout(90.0, connect=10.0)

    async def generate_text(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # NEW FORMAT: OpenAI-compatible 'messages' payload
        payload = {
            "model": self.model_id,
            "messages": [
                {"role": "system", "content": "You are an expert technical interviewer."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4,
            "max_tokens": 1000
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    self.model_url, 
                    json=payload, 
                    headers=headers
                )
                
                if response.status_code == 404:
                    return "Error: Model path not found. Check HF_MODEL_URL in .env."

                response.raise_for_status()
                result = response.json()

                # Extract text from OpenAI-style response
                return result["choices"][0]["message"]["content"].strip()

            except Exception as e:
                logger.error(f"Inference Error: {str(e)}")
                return f"Error: {str(e)}"

inference_client = InferenceClient()