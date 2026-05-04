import os
import json
import asyncio
from google import genai           # <-- Using the newer SDK
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

async def call_agent_json(system_prompt: str, note_text: str) -> dict:
    """
    Calls the Gemini LLM and guarantees a JSON dictionary is returned.
    """
    try:
        # THE EVENT LOOP FIX:
        # By instantiating the Client INSIDE the async function, it inherently 
        # attaches to the fresh asyncio loop that Streamlit just created for this run.
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        # Call the API asynchronously using the locally scoped client
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash", 
            contents=f"Call Note:\n{note_text}",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        
        return json.loads(response.text)
        
    except Exception as e:
        print(f"Error calling Gemini LLM: {e}")
        return {}