import json
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .services.summarizer import ChatSummarizer
from .services.elevenlabs_service import ElevenLabsService
from fastapi.middleware.cors import CORSMiddleware
from .services.mediaupload import MediaUpload
# ----- Models -----

class Message(BaseModel):
    sender: str
    message: str
    isGroup: bool
    conversationName: str
    id: str
    timestamp: int


class Speakers(BaseModel):
    speaker: str
    text: str
    mp3Path: Optional[str]

class Extracts(BaseModel):
    extract: str
    mp3Path: Optional[str]

class Summary(BaseModel):
    extract: Extracts
    speakers: List[Speakers]


# ----- FastAPI Setup -----
app = FastAPI(
    title="Chat Summarizer API",
    version="1.0.0",
    description="Summarizes a conversation into a concise summary."
)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "*",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or use ["*"] to allow all origins (not recommended in production)
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
@app.post("/summarize", response_model=Summary)
async def summarize_conversation(conversation: List[Message]):

    session = ChatSummarizer()
    summary = session.generate_summary(conversation)
    #print(f"34 {summary}")
    eleven = ElevenLabsService()
    #print(f"35 {summary}")
    paths= eleven.master(json.loads(summary))
    print(f"PATHS {paths}")
    print(f"{type(paths)}")
    urls = MediaUpload.upload(paths)
    summary = json.loads(summary)

    extract = Extracts(extract=summary[0]["extract"], mp3Path=urls[0])
    del summary[0]

    speakers = []

    for speaker in summary:
        del urls[0]
        speakerName = list(speaker.keys())[0]
        text = speaker[speakerName]
        speakerEntry = Speakers(speaker= speakerName,text=text, mp3Path=urls[0])

        speakers.append(speakerEntry)


    return Summary(extract=extract, speakers=speakers)

    # except Exception as e:
    #     # you can refine exception handling as needed
    #     raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"status": "ok"}
