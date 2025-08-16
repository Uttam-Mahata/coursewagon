from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ['API_KEY'])




response = client.models.generate_content(
    model='models/gemini-2.0-flash',
    contents=types.Content(
        parts=[
            types.Part(
                file_data=types.FileData(file_uri='https://youtu.be/KaYENI2LyWU?si=37_iCmQbdAw_IYCq')
            ),
            types.Part(text='List Down All the Input fileds used in google form in this video')
        ]
    )
)


print(response.text)