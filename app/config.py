import os

try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv():
        return False

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

OUTPUT_DIR = "outputs"
TRACE_DIR = "traces"
LOG_DIR = "logs"
