"""LangGraph tool for image analysis using the OpenAI vision model.

This tool is bound to the LangGraph agent and allows it to analyze
images stored in Redis by session_id + image_id, using the shared
SessionManager instance.
"""

import logging

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from app.config import get_settings
from app.services.session_manager import get_session_manager

logger = logging.getLogger(__name__)


@tool
async def analyze_image(session_id: str, image_id: str, question: str) -> str:
    """
    Analyze an image stored in the session and answer a question about it.

    Use this tool when the user provides an image (indicated by [image_id:...] and
    [session_id:...] markers in their message). Pass the session_id and image_id
    exactly as they appear in the markers.

    Args:
        session_id: The UUID of the chat session that owns the image.
        image_id: The UUID of the image to analyze.
        question: The question to answer about the image.

    Returns:
        A detailed text answer about the image based on the question.
    """
    settings = get_settings()
    sm = get_session_manager()

    image_b64 = await sm.get_image(session_id, image_id)

    if not image_b64:
        logger.warning("Image %s not found in session %s", image_id, session_id)
        return f"Error: Image {image_id} not found. It may have been deleted with the session."

    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        max_tokens=1024,
    )

    message = HumanMessage(
        content=[
            {"type": "text", "text": question},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_b64}",
                    "detail": "auto",
                },
            },
        ]
    )

    response = await llm.ainvoke([message])
    logger.info("Image analysis completed for image %s, question: %s", image_id, question[:80])
    return response.content
