# utils/gemini_helper.py
import os
import logging

import google.generativeai as genai
from config import Config
import json

logger = logging.getLogger(__name__)

def extract_sql_query(response_text):
    try:
        # Find the start and end of the SQL block
        sql_block_start = response_text.find("```sql") + 6  # Start after "```sql"
        sql_block_end = response_text.find("```", sql_block_start)

        if sql_block_start == -1 or sql_block_end == -1:
            raise ValueError("SQL block not found in the response")

        # Extract and clean the SQL query
        sql_query = response_text[sql_block_start:sql_block_end].strip()

        # Ensure the SQL query is valid (remove unwanted characters)
        if sql_query.startswith("l"):
            sql_query = sql_query[1:].strip()  # Remove the leading 'l' if present

        return sql_query
    except Exception as e:
        raise ValueError(f"Error extracting SQL query: {str(e)}")


def mermaid_content(content):
    start = content.find('```mermaid')
    end = content.find('```', start + 1)
    while start != -1 and end != -1:
        mermaid_code = content[start:end + 3]
        mermaid_code = mermaid_code.replace('```mermaid', '<pre class="mermaid">').replace('```', '</pre>')
        content = content[:start] + mermaid_code + content[end + 3:]
        start = content.find('```mermaid', end + 1)
        end = content.find('```', start + 1)
    return content


class GeminiHelper:
    def __init__(self):
        config = Config()
        genai.configure(api_key=config.API_KEY)
        self.safety_settings = [
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "HIGH"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "HIGH"}
        ]
        self.generation_config = {
            "max_output_tokens": 8192
        }
        self.model = genai.GenerativeModel("gemini-1.5-flash-002")

    def generate_content(self, prompt, response_schema=None):
        try:
            logger.debug(f"Generating content with schema: {response_schema}")
            if response_schema:
                generation_config = genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    **self.generation_config
                )
                logger.debug(f"Using generation config: {generation_config}")
                response = self.model.generate_content(
                    prompt,
                    safety_settings=self.safety_settings,
                    generation_config=generation_config
                )
                logger.debug(f"Raw response from Gemini: {response.text}")
                return json.loads(response.text)
            else:
                response = self.model.generate_content(
                    prompt, 
                    safety_settings=self.safety_settings
                )
                return response.text
        except Exception as e:
            logger.error(f"Error in generate_content: {str(e)}", exc_info=True)
            raise

