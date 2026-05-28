"""
LangGraph agent for the multimodal chatbot.

Builds a StateGraph with an agent node (LLM with tool-calling)
and a tools node. The agent can use the image analysis tool to
answer questions about user-provided images stored in Redis.
"""

import logging
from typing import Optional

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import MessagesState
from langgraph.prebuilt import ToolNode

from app.config import Settings
from app.models.session import ChatMessageRecord
from app.tools.image_analysis import analyze_image

logger = logging.getLogger(__name__)

# All tools available to the agent
AGENT_TOOLS = [analyze_image]

# System prompt that defines the agent's behaviour
SYSTEM_PROMPT = """You are a helpful multimodal assistant for a mobile application.
You can analyze images that users send you and answer questions about them.

When the current user message contains [image_id:...] and [session_id:...] markers:
- That image is the active image for this turn.
- The markers may come from a newly uploaded image or be automatically carried over from an earlier message in the same session.
- If the user's request depends on what is visible in the image, call the analyze_image tool with the provided session_id and image_id.
- If the request is clearly unrelated to the image, answer normally without the tool.

When a user sends text without any image markers:
- Answer the question directly based on your knowledge and the text conversation history.

Always be concise but thorough. Respond in the same language the user writes in."""


def build_agent_graph(settings: Settings) -> StateGraph:
    """
    Construct the LangGraph StateGraph for the chatbot agent.

    Args:
        settings: Application settings (contains model name and API key).

    Returns:
        A compiled LangGraph graph ready for invocation.
    """
    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0.3,
    )
    llm_with_tools = llm.bind_tools(AGENT_TOOLS)

    async def agent_node(state: MessagesState) -> dict:
        """Call the LLM with the current messages and bound tools."""
        response = await llm_with_tools.ainvoke(state["messages"])
        return {"messages": [response]}

    def should_continue(state: MessagesState) -> str:
        """Decide whether the agent should call a tool or finish."""
        last_message = state["messages"][-1]
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            return "tools"
        return END

    # Build the graph
    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(AGENT_TOOLS))

    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    return graph.compile()


def _build_langchain_messages(
    history: list[ChatMessageRecord],
    user_message: str,
    session_id: str,
    image_id: Optional[str] = None,
    image_url: Optional[str] = None,
) -> list[BaseMessage]:
    """
    Convert session history + new user message into LangChain message objects.

    Images are NOT embedded into the context. Instead, the user message is
    annotated with the image_id and session_id so the agent can pass them
    to the analyze_image tool.

    Args:
        history: Previous messages from the session.
        user_message: Current user text.
        session_id: The current session UUID (for tool reference).
        image_id: Optional image identifier stored in Redis.
        image_url: Optional public image URL.

    Returns:
        List of LangChain BaseMessage objects ready for the agent.
    """
    messages: list[BaseMessage] = [SystemMessage(content=SYSTEM_PROMPT)]

    # Reconstruct history (include image annotations for past messages)
    for record in history:
        if record.role == "user":
            text = record.content
            if record.image_id:
                text += (
                    f"\n\n[image_id:{record.image_id}] [session_id:{session_id}]"
                )
            messages.append(HumanMessage(content=text))
        elif record.role == "assistant":
            messages.append(AIMessage(content=record.content))

    # Build current user message — annotate with image reference if present
    if image_id:
        annotated = (
            f"{user_message}\n\n"
            f"[image_id:{image_id}] [session_id:{session_id}]"
        )
        messages.append(HumanMessage(content=annotated))
    elif image_url:
        annotated = (
            f"{user_message}\n\n"
            f"[image_url:{image_url}] [session_id:{session_id}]"
        )
        messages.append(HumanMessage(content=annotated))
    else:
        messages.append(HumanMessage(content=user_message))

    return messages


async def invoke_agent(
    settings: Settings,
    history: list[ChatMessageRecord],
    user_message: str,
    session_id: str,
    image_id: Optional[str] = None,
    image_url: Optional[str] = None,
) -> str:
    """
    Run the LangGraph agent with session history and a new user message.

    Args:
        settings: Application settings.
        history: Previous messages from the session.
        user_message: The user's current text message.
        session_id: The current session UUID.
        image_id: Optional image identifier stored in Redis.
        image_url: Optional image URL.

    Returns:
        The agent's text response.
    """
    graph = build_agent_graph(settings)
    messages = _build_langchain_messages(
        history, user_message, session_id, image_id, image_url,
    )

    logger.info(
        "Invoking agent with %d history messages + 1 new message",
        len(history),
    )

    result = await graph.ainvoke({"messages": messages})

    # Extract the last AI message from the result
    response_messages = result["messages"]
    for msg in reversed(response_messages):
        if isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
            logger.info("Agent responded with %d chars", len(msg.content))
            return msg.content

    # Fallback — shouldn't happen but safe guard
    logger.warning("No AI response found in agent result")
    return "I'm sorry, I couldn't generate a response. Please try again."
