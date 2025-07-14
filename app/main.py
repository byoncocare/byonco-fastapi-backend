# app/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Enable CORS (you can restrict origins later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define input schema
class PromptRequest(BaseModel):
    prompt: str

# Root test route
@app.get("/")
def read_root():
    return {"message": "ByOnco GPT API is running 🚀"}

# Main GPT response route
@app.post("/api/gpt")
def generate_response(prompt_request: PromptRequest):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # You can change to gpt-3.5-turbo if needed
            messages=[{"role": "user", "content": prompt_request.prompt}],
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
