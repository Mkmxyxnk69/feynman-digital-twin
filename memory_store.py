import os
import json
from datetime import datetime

MEMORY_PATH = "memories.json"
DEFAULT_USER_ID = "default_user"


def load_memories():
    """Load all memories from disk."""
    if not os.path.exists(MEMORY_PATH):
        return {}
    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_memories(data):
    """Save all memories to disk."""
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def add_memory(question: str, answer_summary: str, user_id: str = DEFAULT_USER_ID):
    """Append one memory item for a user."""
    data = load_memories()
    data.setdefault(user_id, [])
    data[user_id].append(
        {
            "question": question,
            "answer_summary": answer_summary,
            "timestamp": datetime.now().isoformat(),
        }
    )
    save_memories(data)


def get_recent_memories(user_id: str = DEFAULT_USER_ID, k: int = 5):
    """Return last k memories for a user (oldest → newest within that slice)."""
    data = load_memories()
    user_mems = data.get(user_id, [])
    return user_mems[-k:]