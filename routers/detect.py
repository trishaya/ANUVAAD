from fastapi import APIRouter
from pydantic import BaseModel
from langdetect import detect

router = APIRouter()

class DetectRequest(BaseModel):
    text: str

@router.post("/detect")
def detect_language(request: DetectRequest):

    language = detect(request.text)

    return {
        "detected_language": language
    }