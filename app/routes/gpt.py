# app/routes/gpt.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import openai
from app.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str

@router.post("/api/gpt")
async def generate_response(request: PromptRequest):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": request.prompt},
            ]
        )
        return {"response": response.choices[0].message["content"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
