"""
In-memory session store.
Each session_id maps to a list of LangChain message objects.
"""
from threading import Lock
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

_lock = Lock()
_store: dict[str, list] = {}


def get_history(session_id: str) -> list:
    """Return the full message history for this session (excluding system prompt)."""
    with _lock:
        return list(_store.get(session_id, []))


def add_human_message(session_id: str, content: str) -> None:
    with _lock:
        _store.setdefault(session_id, []).append(HumanMessage(content=content))


def add_ai_message(session_id: str, message) -> None:
    """message can be a string or an AIMessage object."""
    with _lock:
        if isinstance(message, str):
            _store.setdefault(session_id, []).append(AIMessage(content=message))
        else:
            _store.setdefault(session_id, []).append(message)


def add_tool_message(session_id: str, content: str, tool_call_id: str) -> None:
    with _lock:
        _store.setdefault(session_id, []).append(
            ToolMessage(content=content, tool_call_id=tool_call_id)
        )


def clear_session(session_id: str) -> None:
    with _lock:
        _store.pop(session_id, None)


def session_exists(session_id: str) -> bool:
    with _lock:
        return session_id in _store
