import re
from datetime import datetime


def clean_text(text):
    """Remove unnecessary spaces and normalize text."""

    if not text:
        return ""

    text = str(text)
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def create_title(text, max_length=60):
    """Generate a short title from user input."""

    if not text:
        return "Untitled"

    cleaned = clean_text(text)
    first_line = cleaned.split("\n")[0]

    if len(first_line) > max_length:
        return first_line[:max_length].rstrip() + "..."

    return first_line or "Untitled"


def validate_input(text, field_name="Input"):
    """Validate required text input."""

    if not text or not str(text).strip():
        return False, f"Please enter {field_name.lower()}."

    return True, ""


def format_timestamp(timestamp):
    """Format an ISO timestamp for display."""

    if not timestamp:
        return "Unknown"

    try:
        date = datetime.fromisoformat(timestamp)
        return date.strftime("%d %b %Y, %I:%M %p")

    except (ValueError, TypeError):
        return str(timestamp)


def truncate_text(text, max_length=300):
    """Shorten long text for previews."""

    if not text:
        return ""

    text = str(text).strip()

    if len(text) <= max_length:
        return text

    return text[:max_length].rstrip() + "..."


def count_words(text):
    """Count words in a text."""

    if not text:
        return 0

    return len(str(text).split())


def get_reading_time(text):
    """Estimate reading time in minutes."""

    words = count_words(text)

    if words == 0:
        return 0

    return max(1, round(words / 200))


def safe_filename(filename):
    """Convert a filename into a safe format."""

    filename = str(filename).strip()
    filename = re.sub(r"[^\w.\-]", "_", filename)

    return filename[:100] or "document"