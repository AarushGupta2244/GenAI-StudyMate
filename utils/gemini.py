from google import genai
from google.genai import types

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    DEFAULT_TEMPERATURE,
    MAX_OUTPUT_TOKENS
)


class GeminiService:

    def __init__(self):

        if not GEMINI_API_KEY:
            raise ValueError(
                "Gemini API key missing. Please configure your .env file."
            )

        self.client = genai.Client(
            api_key=GEMINI_API_KEY,
            http_options=types.HttpOptions(
                timeout=60000
            )
        )

        self.model = GEMINI_MODEL

    def generate_response(self, prompt, system_instruction=None):

        try:
            config = types.GenerateContentConfig(
                temperature=DEFAULT_TEMPERATURE,
                max_output_tokens=MAX_OUTPUT_TOKENS,
                system_instruction=system_instruction
            )

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )

            if not response.text:
                raise ValueError("AI returned an empty response.")

            return response.text.strip()

        except Exception as error:
            raise RuntimeError(
                f"Gemini AI Error: {str(error)}"
            ) from error

    def generate_stream(self, prompt, system_instruction=None):

        try:
            config = types.GenerateContentConfig(
                temperature=DEFAULT_TEMPERATURE,
                max_output_tokens=MAX_OUTPUT_TOKENS,
                system_instruction=system_instruction
            )

            response_stream = self.client.models.generate_content_stream(
                model=self.model,
                contents=prompt,
                config=config
            )

            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text

        except Exception as error:
            raise RuntimeError(
                f"Gemini Streaming Error: {str(error)}"
            ) from error


def get_gemini_service():
    return GeminiService()