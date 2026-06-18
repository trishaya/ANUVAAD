from dotenv import load_dotenv
import os
import google.generativeai as genai


load_dotenv()


class MeetingSummarizer:

    def __init__(self):

        genai.configure(

            api_key=os.getenv(
                "GEMINI_API_KEY"
            )
        )

        self.model = genai.GenerativeModel(

            "models/gemini-2.5-flash"
        )

    def summarize_meeting(

        self,

        transcript
    ):

        prompt = f"""

        You are an AI meeting assistant.

        Analyze the following meeting transcript.

        Generate:

        1. A concise summary
        2. Minutes of Meeting (MoM)

        Include:
        - Key discussion points
        - Decisions made
        - Tasks assigned
        - Deadlines if mentioned

        Transcript:
        {transcript}

        """

        response = self.model.generate_content(
            prompt
        )

        return response.text