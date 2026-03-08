"""
LangGraph tool for image analysis using the OpenAI vision model.

This tool is bound to the LangGraph agent and allows it to analyze
images provided as base64-encoded data.
"""

import logging

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from app.config import get_settings

logger = logging.getLogger(__name__)


@tool
def analyze_image(image_base64: str, question: str) -> str:
    """
    Analyze an image and answer a specific question about it.

    Use this tool when the user provides an image and asks a question about it.
    The image should be provided as a base64-encoded string.

    Args:
        image_base64: Base64-encoded image data (JPEG or PNG).
        question: The question to answer about the image.

    Returns:
        A detailed text answer about the image based on the question.
    """
    settings = get_settings()
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
                    "url": f"data:image/jpeg;base64,{image_base64}",
                    "detail": "auto",
                },
            },
        ]
    )

    response = llm.invoke([message])
    logger.info("Image analysis completed for question: %s", question[:80])
    return response.content
