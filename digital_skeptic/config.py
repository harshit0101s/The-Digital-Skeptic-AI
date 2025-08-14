from dataclasses import dataclass
import os

@dataclass
class Config:
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    max_input_chars: int = int(os.getenv("MAX_INPUT_CHARS", "60000"))
#AIzaSyDU6X28CsyuYhl53N5HrIywW0jgmtspZUc