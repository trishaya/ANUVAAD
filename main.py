from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from auth import create_access_token

from services.model_router import ModelRouter
from services.indic_lid_detector import IndicLID
from services.analytics_service import AnalyticsService
from services.summarizer import MeetingSummarizer
from services.error_logger import ErrorLogger

import re
import time


app = FastAPI()


app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


router = None
detector = None
analytics = None
summarizer = None
error_logger = None


# =========================================================
# Startup Initialization
# =========================================================

@app.on_event("startup")
def load_model():

    global router
    global detector
    global analytics
    global summarizer
    global error_logger

    print("🚀 Initializing Translation System...")

    router = ModelRouter()

    detector = IndicLID()

    analytics = AnalyticsService()

    summarizer = MeetingSummarizer()

    error_logger = ErrorLogger()

    print("✅ Models Loaded Successfully")


# =========================================================
# English Detection Helper
# =========================================================

def is_plain_english(text):

    if not text:
        return False

    text = text.lower()

    english_words = {

        "the", "is", "are", "you",
        "hello", "good", "morning",
        "please", "thank", "meeting",
        "project", "report", "this",
        "that", "what", "where",
        "how", "when", "why",
        "email", "translation",
        "language", "backend"
    }

    words = re.findall(
        r"\b[a-zA-Z]+\b",
        text
    )

    if not words:
        return False

    matches = sum(

        1 for word in words
        if word in english_words
    )

    return matches >= max(
        1,
        len(words) // 3
    )


# =========================================================
# Login Schema
# =========================================================

class LoginRequest(BaseModel):

    username: str

    password: str


# =========================================================
# Translation Request Schema
# =========================================================

class TranslateRequest(BaseModel):

    text: str

    target_lang: str

    source_lang: str | None = None

    model: str | None = None

    output_script: str | None = None

    numerals_format: str | None = "international"


# =========================================================
# Meeting Request Schema
# =========================================================

class MeetingRequest(BaseModel):

    transcript: str


# =========================================================
# Login Endpoint
# =========================================================

@app.post("/login")
def login(request: LoginRequest):

    if (

        request.username == "admin"

        and

        request.password == "admin"
    ):

        token = create_access_token({

            "sub": request.username
        })

        return {

            "access_token": token
        }

    raise HTTPException(

        status_code=401,

        detail="Invalid credentials"
    )


# =========================================================
# Translation Endpoint
# =========================================================

@app.post("/translate")
async def translate(request: TranslateRequest):

    try:

        start_time = time.time()

        original_text = request.text.strip()

        if not original_text:

            raise HTTPException(

                status_code=400,

                detail="Text cannot be empty"
            )

        # =================================================
        # Source Language Detection
        # =================================================

        if request.source_lang:

            source_lang = (
                request.source_lang
            )

            detected_lang = source_lang

            print(

                "📝 MANUAL SOURCE:",

                source_lang
            )

        else:

            if is_plain_english(
                original_text
            ):

                detected_lang = "en"

                source_lang = "en"

                print(
                    "🇬🇧 DETECTED: English"
                )

            else:

                detected_lang = detector.detect(
                    original_text
                )

                source_lang = detected_lang

                print(

                    "🤖 DETECTED SOURCE:",

                    detected_lang
                )

        # =================================================
        # Safety Fallback
        # =================================================

        if not source_lang:

            source_lang = "en"

        # =================================================
        # Translation Logging
        # =================================================

        print(

            "🌐 TRANSLATION:",

            source_lang,

            "→",

            request.target_lang
        )

        print(

            "🤖 MODEL:",

            request.model
        )

        print(

            "📝 TEXT LENGTH:",

            len(original_text)
        )

        # =================================================
        # Translation Router
        # =================================================

        result = router.translate(

            text=original_text,

            source_lang=source_lang,

            target_lang=request.target_lang,

            model=request.model,

            output_script=
                request.output_script,

            numerals_format=
                request.numerals_format
        )

        # =================================================
        # Response Time
        # =================================================

        response_time = round(

            time.time() - start_time,

            2
        )

        print(

            "⚡ RESPONSE TIME:",

            response_time,

            "seconds"
        )

        # =================================================
        # Analytics Logging
        # =================================================

        analytics.log_translation(

            source_lang=source_lang,

            target_lang=request.target_lang,

            model_used=result["model_used"],

            response_time=response_time,

            text_length=len(original_text),

            success=True
        )

        # =================================================
        # Success Response
        # =================================================

        return {

            "success": True,

            "original_text":
                original_text,

            "translated_text":
                result["translated_text"],

            "source_language":
                detected_lang,

            "target_lang":
                request.target_lang,

            "model_used":
                result["model_used"],

            "output_script":
                request.output_script,

            "numerals_format":
                request.numerals_format,

            "response_time":
                response_time
        }

    except HTTPException:

        raise

    except Exception as error:

        print(

            "❌ TRANSLATION ERROR:",

            str(error)
        )

        error_logger.log_error(

            endpoint="/translate",

            error_message=str(error)
        )

        raise HTTPException(

            status_code=500,

            detail=str(error)
        )


# =========================================================
# Meeting Summarization Endpoint
# =========================================================

@app.post("/summarize-meeting")
async def summarize_meeting(

    request: MeetingRequest
):

    try:

        result = summarizer.summarize_meeting(

            request.transcript
        )

        return {

            "success": True,

            "result": result
        }

    except Exception as error:

        print(

            "❌ SUMMARIZATION ERROR:",

            str(error)
        )

        error_logger.log_error(

            endpoint="/summarize-meeting",

            error_message=str(error)
        )

        raise HTTPException(

            status_code=500,

            detail=str(error)
        )


# =========================================================
# Health Check Endpoint
# =========================================================

@app.get("/")
def root():

    return {

        "status":
            "running",

        "service":
            "ANUVAAD Translation Backend"
    }


# =========================================================
# Analytics Routes
# =========================================================

@app.get("/analytics/stats")
def analytics_stats():

    return analytics.get_stats()


@app.get("/analytics/languages")
def analytics_languages():

    return analytics.get_language_stats()


@app.get("/analytics/models")
def analytics_models():

    return analytics.get_model_stats()


@app.get("/analytics/daily")
def analytics_daily():

    return analytics.get_daily_stats()


@app.get("/analytics/success")
def analytics_success():

    return analytics.get_success_stats()


# =========================================================
# Error Logs Route
# =========================================================

@app.get("/errors")
def get_errors():

    return error_logger.get_errors()