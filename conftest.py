# Root conftest: set test DB before any test module (and thus main/database) is loaded
import os

# File-based so all connections share the same DB (avoids :memory: isolation issues)
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
