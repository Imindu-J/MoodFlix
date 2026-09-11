from google import genai
from google.genai import types

from app.schemas.preferences import ExtractedPreferences

SYSTEM_PROMPT = """
You extract movie preferences from one user message.

Rules:
- Extract only information explicitly stated or clearly implied.
- Never invent preferences.
- Put moods, themes, tone, plot interests, and subjective qualities
  into semantic_query.
- Convert runtime expressions into minutes.
- Convert clearly named languages to lowercase ISO 639-1 codes.
- Use conventional movie genre names.
- Use intent="similar" only when the user names a reference movie.
- Put that movie title in reference_movie_title.
- If there is not enough information for a useful search, return
  status="needs_clarification" and ask one concise question.
- Requests such as "another one" require conversation context.
  Since no context is available, request clarification.
- Do not add filters the user did not request.
- Keep the result limit between 3 and 5.
"""


class PreferenceExtractionError(RuntimeError):
    pass


class PreferenceExtractor:
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
    ) -> None:
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def extract(self, message: str) -> ExtractedPreferences:
        cleaned_message = message.strip()

        if not cleaned_message:
            raise ValueError("Message cannot be empty")

        response = self.client.models.generate_content(
            model=self.model,
            contents=cleaned_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=ExtractedPreferences,
                temperature=0,
            ),
        )

        if not response.text:
            raise PreferenceExtractionError(
                "Gemini did not return preference data"
            )

        return ExtractedPreferences.model_validate_json(
            response.text
        )
