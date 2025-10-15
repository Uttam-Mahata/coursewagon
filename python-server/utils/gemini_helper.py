# utils/gemini_helper.py
import os
import logging
import json
from google import genai
from google.genai import types
from config import Config
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
    """Convert mermaid code blocks to HTML pre tags"""
    start = content.find('```mermaid')
    end = content.find('```', start + 1)
    while start != -1 and end != -1:
        mermaid_code = content[start:end + 3]
        mermaid_code = mermaid_code.replace('```mermaid', '<pre class="mermaid">').replace('```', '</pre>')
        content = content[:start] + mermaid_code + content[end + 3:]
        start = content.find('```mermaid', end + 1)
        end = content.find('```', start + 1)
    return content


def chart_content(content):
    """Convert chart-json code blocks to HTML divs with data attributes"""
    import re
    import html
    
    # Pattern to match ```chart-json ... ```
    pattern = r'```chart-json\s*\n(.*?)```'
    
    def replace_chart(match):
        chart_json = match.group(1).strip()
        # Generate unique ID for each chart
        import time
        chart_id = f"chart-{int(time.time() * 1000)}-{hash(chart_json) % 10000}"
        # Escape the JSON for HTML attribute
        escaped_json = html.escape(chart_json)
        return f'<div class="chart-container" data-chart-id="{chart_id}" data-chart-config="{escaped_json}"></div>'
    
    # Replace all chart-json blocks
    content = re.sub(pattern, replace_chart, content, flags=re.DOTALL)
    return content


# remove the first occurence of  ```markdown  and last occurence of ```
def extract_markdown(content):
    start = content.find('```markdown')
    end = content.rfind('```')
    if start != -1 and end != -1:
        content = content[start + 12:end].strip()
    return content





class GeminiHelper:
    def __init__(self, api_key=None):
        # Always use API key from environment variables
        self.api_key = os.environ.get('API_KEY')
        
        if not self.api_key:
            logger.warning("No API_KEY found in environment variables. Gemini functionality will not work.")
        
        # Initialize the client only when needed, with API key
        self._client = None
        self.safety_settings = [
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold="BLOCK_NONE"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH",
                threshold="BLOCK_NONE"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="HIGH"
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="HIGH"
            )
        ]
        self.generation_config = {
            "max_output_tokens": 8192
        }
        self.model_name = "gemini-2.5-flash-lite"  # Default model

    @property
    def client(self):
        # Only initialize the client when needed, not in constructor
        if self._client is None:
            if not self.api_key:
                raise ValueError("No API key available for Gemini. Set API_KEY in environment variables.")
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def generate_content(self, prompt, response_schema=None):
        try:
            logger.debug(f"Generating content with schema: {response_schema}")
            if not self.api_key:
                raise ValueError("No API key available for Gemini. Set API_KEY in environment variables.")
                
            if response_schema:
                config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema,
                    max_output_tokens=self.generation_config["max_output_tokens"],
                    # safety_settings=self.safety_settings
                )
                logger.debug(f"Using generation config: {config}")
                
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )
                logger.debug(f"Raw response from Gemini: {response.text}")
                return json.loads(response.text)
            else:
                response = self.client.models.generate_content(
                    model=self.model_name, 
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        # safety_settings=self.safety_settings
                    )
                )
                return response.text
        except Exception as e:
            logger.error(f"Error in generate_content: {str(e)}", exc_info=True)
            raise
        finally:
            # Remove reference to client to help with garbage collection
            # of objects containing the API key
            self._client = None

