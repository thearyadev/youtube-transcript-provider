import requests
import re
from typing import Awaitable, Callable, Any


NOTEGPT_URL = (
    "https://notegpt.io/api/v1/get-transcript-v2?video_id={video_id}&platform=youtube"
)


def get_youtube_video_id(url: str) -> str | None:
    if len(url) == 0:
        return None
    match = re.search(r"(?:v=|be/|watch\?v=)([^&?]+)", url)
    if match:
        return match.group(1)
    else:
        return None


def get_best_transcript(transcripts_dict: dict) -> list[dict[str, Any]]:
    if "en" in transcripts_dict:
        return transcripts_dict["en"]["auto"]
    if "en_auto" in transcripts_dict:
        return transcripts_dict["en_auto"]["auto"]
    return []


def request_transcript(video_id: str) -> requests.Response:
    return requests.get(NOTEGPT_URL.format(video_id=video_id))


class Tools:
    def __init__(self):
        self.citation = True

    async def get_youtube_transcript(
        self,
        url: str,
        __event_emitter__: Callable[[dict[str, dict[str, Any] | str]], Awaitable[None]],
    ) -> str:
        """
        Provides the title and full transcript of a YouTube video in English.
        Only use if the user supplied a valid YouTube URL.
        Examples of valid YouTube URLs: https://youtu.be/dQw4w9WgXcQ, https://www.youtube.com/watch?v=dQw4w9WgXcQ

        :param url: The URL of the youtube video that you want the transcript for.
        :return: The title and full transcript of the YouTube video in English, or an error message.
        """
        await __event_emitter__(
            {
                "type": "status",
                "data": {
                    "description": f"Getting transcript for {url}",
                    "done": False,
                },
            }
        )

        video_id = get_youtube_video_id(url)
        if (
            video_id is None or video_id == "dQw4w9WgXcQ"
        ):  # llms will provide the one in the description.
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"{url} is not a valid youtube link",
                        "done": True,
                    },
                }
            )
            return "The tool failed with an error. No transcript has been provided."
        response = request_transcript(video_id)

        if response.status_code != 200:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": "Couldn't load transcript",
                        "done": True,
                    },
                }
            )
            return f"The tool failed with an error. No transcript has been provided\n\nStatus Code: {response.status_code}\nContent: {response.text}"

        try:
            json_content = response.json()
        except:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": "Couldn't load transcript. Response body was not valid JSON",
                        "done": True,
                    },
                }
            )
            return "The tool failed with an error. No transcript has been provided."

        if json_content["code"] != 100000:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": "Couldn't load transcript",
                        "done": True,
                    },
                }
            )
            return f"The tool failed with an error. No transcript has been provided\n\nStatus Code: {response.status_code}\nContent: {response.text}"

        title = json_content["data"]["videoInfo"]["name"]
        transcript = get_best_transcript(json_content["data"]["transcripts"])
        if len(transcript) == 0:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": "No english transcript is present.",
                        "done": True,
                    },
                }
            )
            return "The tool failed with an error. No transcript has been provided."
        text_only_transcript = " ".join([caption["text"] for caption in transcript])

        await __event_emitter__(
            {
                "type": "status",
                "data": {
                    "description": f"Successfully retrieved transcript for {url}",
                    "done": True,
                },
            }
        )
        return f"Title: {title}\n\nTranscript:\n{text_only_transcript}"
