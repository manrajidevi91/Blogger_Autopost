"""Utilities for retrieving YouTube transcripts.

This module provides a helper function to fetch the transcript text for a
YouTube video using :mod:`youtube_transcript_api`. Any network issues or cases
where transcripts are unavailable are surfaced as error strings so callers can
handle them gracefully.
"""

from youtube_transcript_api import YouTubeTranscriptApi, _errors
from requests.exceptions import RequestException

def get_youtube_transcript(video_id):
    """Return the transcript for ``video_id`` or an error message string."""

    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join(entry["text"] for entry in transcript_list)
        return transcript
    except _errors.TranscriptsDisabled:
        return "Transcripts are disabled for this video"
    except _errors.NoTranscriptFound:
        return "No transcript found for this video"
    except (RequestException, _errors.HTTPError) as exc:
        return f"Network error fetching transcript: {exc}"
    except Exception as exc:  # noqa: BLE001
        return f"Error getting YouTube transcript for video ID {video_id}: {exc}"
