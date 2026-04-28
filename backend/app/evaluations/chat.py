from app.tracing import get_langfuse


def evaluate_chat_message(message_id: str, notebook_id: str):
    """Trigger quality evaluation for a chat response asynchronously."""
    langfuse = get_langfuse()
    langfuse.evaluate(
        name="chat_response_quality",
        input={"message_id": message_id},
        metadata={"notebook_id": notebook_id}
    )