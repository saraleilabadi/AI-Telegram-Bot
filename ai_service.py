import asyncio

from google import genai
from google.genai import errors

from config import API_KEY, MODEL_NAME


client = genai.Client(api_key=API_KEY)


def _generate_sync(user_message, operation, language):
    """Blocking call to the Gemini API."""

    print(">>> _generate_sync CALLED")

    if operation == "rewrite":
        instruction = (
            "generate an intelligent, clear, natural, and well-rewritten "
            "response while preserving the original meaning."
        )

    elif operation == "summarize":
        instruction = "generate a concise summary of the message."

    elif operation == "translate":
        instruction = f"translate the message into {language}."

    else:
        raise ValueError(f"Invalid operation: {operation}")

    try:
        print("MODEL:", MODEL_NAME)

        result = client.models.generate_content(
            model=MODEL_NAME,
            contents=f"""For the following message:
            {instruction}
            Message: {user_message}""",
        )

    except errors.APIError as e:
        print(f"API error code: {e.code}")
        raise

    return result.text


async def ai_response(user_message, operation, language):
    return await asyncio.to_thread(
        _generate_sync,
        user_message,
        operation,
        language
    )