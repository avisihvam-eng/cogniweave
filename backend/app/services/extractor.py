import re
import io
from youtube_transcript_api import YouTubeTranscriptApi
from pypdf import PdfReader
from docx import Document as DocxDocument
import httpx


def get_youtube_video_id(url: str) -> str:
    pattern = r"(?:https?://)?(?:www\.)?(?:youtube\.com/(?:[^/\n\s]+/\S+/|(?:v|e(?:mbed)?)/|\S*?[?&]v=)|youtu\.be/)([a-zA-Z0-9_-]{11})"
    match = re.match(pattern, url)
    return match.group(1) if match else None


def fetch_youtube_transcript(video_id: str) -> str:
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([item["text"] for item in transcript_list])
    except Exception as e:
        print(f"Error fetching YouTube transcript: {e}")
        return None


def fetch_youtube_metadata(video_id: str) -> dict:
    try:
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        r = httpx.get(url)
        if r.status_code == 200:
            data = r.json()
            return {
                "title": data.get("title"),
                "speaker": data.get("author_name"),
                "source": "YouTube",
                "url": f"https://www.youtube.com/watch?v={video_id}",
            }
    except Exception as e:
        print(f"Error fetching oembed metadata: {e}")
    return {
        "title": f"YouTube Video {video_id}",
        "speaker": "Unknown",
        "source": "YouTube",
        "url": f"https://www.youtube.com/watch?v={video_id}",
    }


def parse_pdf(file_bytes: bytes) -> str:
    try:
        pdf = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return ""


def parse_docx(file_bytes: bytes) -> str:
    try:
        doc = DocxDocument(io.BytesIO(file_bytes))
        return "\n".join([p.text for p in doc.paragraphs]).strip()
    except Exception as e:
        print(f"Error parsing DOCX: {e}")
        return ""


def parse_txt(file_bytes: bytes) -> str:
    try:
        return file_bytes.decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Error parsing TXT: {e}")
        return ""
