import os

from google import genai
from dotenv import load_dotenv


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents="Explain HTTP 500 error in one simple sentence."
)


print(response.text)