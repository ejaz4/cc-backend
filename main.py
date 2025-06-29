from typing import List, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .services.summarizer import ChatSummarizer
from .services.elevenlabs_service import ElevenLabsService
from .services.mediaupload import MediaUpload
# ----- Models -----
class Conversation(BaseModel):
    messages: List[Dict]

class Summary(BaseModel):
    summary: str

# ----- FastAPI Setup -----
app = FastAPI(
    title="Chat Summarizer API",
    version="1.0.0",
    description="Summarizes a conversation into a concise summary."
)

@app.post("/summarize", response_model=Summary)
async def summarize_conversation(conversation: Conversation):
    try:
        session = ChatSummarizer()
        summary = session.generate_summary(conversation)
        eleven = ElevenLabsService()
        paths= eleven.master(summary)
        MediaUpload.upload(paths)
        return paths

    except Exception as e:
        # you can refine exception handling as needed
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"status": "ok"}
