import os
import asyncio
from openai import AsyncOpenAI, AssistantEventHandler
from threading import Thread
from openai import OpenAI
import logging

logging.basicConfig(level=logging.INFO)
# Initialize the OpenAI client
#api_key = os.getenv(OPENAI_API_KEY)
client = AsyncOpenAI(api_key="")

transcript_buffer = ""

def append_to_transcript(transcript):
    global transcript_buffer
    if transcript:
        transcript_buffer += transcript + " "

def reset_transcript():
    global transcript_buffer
    transcript_buffer = ""

def set_role(new_role):
    global role
    role = new_role

def get_transcript_buffer():
    global transcript_buffer
    return transcript_buffer

async def send_transcript_content():
    global transcript_buffer
    if transcript_buffer.strip():
        try:
            content = f"Interview transcript, answer the question briefly: {transcript_buffer}"

            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": content}],
                stream=True
            )

            full_response = ""
            async for chunk in response:
                chunk_message = chunk.choices[0].delta.content
                if chunk_message:
                    full_response += chunk_message
                    yield chunk_message  # Yield each chunk instead of printing
            reset_transcript()
        except Exception as e:
            yield f"Error with OpenAI API: {e}"
    else:
        yield "Transcript buffer is empty."
