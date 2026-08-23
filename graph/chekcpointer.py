from pathlib import Path
import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver


BASE_DIR = Path(__file__).resolve().parent.parent
MEMORY_DIR = BASE_DIR / "memory"

MEMORY_DIR.mkdir(parents=True, exist_ok=True)


CHECKPOINT_DB = MEMORY_DIR / "langgraph_checkpoints.db"


def create_checkpointer():

    conn = sqlite3.connect(CHECKPOINT_DB, check_same_thread=False)

    return SqliteSaver(conn)