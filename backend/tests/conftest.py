import os
import sys
import tempfile

# Use isolated SQLite DB for tests
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp.name}"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["INIT_ADMIN_USERNAME"] = "admin"
os.environ["INIT_ADMIN_PASSWORD"] = "admin123"
os.environ["INIT_ADMIN_EMAIL"] = "admin@test.local"

# Ensure backend/ is on sys.path so "app" package resolves regardless of cwd.
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)
