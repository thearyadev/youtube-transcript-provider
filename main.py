"""
title: Youtube Transcript Provider (Langchain Community)
author: thearyadev 
author_url: https://github.com/thearyadev/youtube-transcript-provider
funding_url: https://github.com/open-webui
version: 0.0.2
"""

from typing import Awaitable, Callable, Any
from langchain_community.document_loaders import YoutubeLoader
import traceback


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
        try:
            if "dQw4w9WgXcQ" in url:
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

            data = YoutubeLoader.from_youtube_url(
                # video info seems to be broken
                youtube_url=url,
                add_video_info=False,
                language=["en", "en_auto"],
            ).load()

            if not data:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"Failed to retrieve transcript for {url}. No results",
                            "done": True,
                        },
                    }
                )
                return "The tool failed with an error. No transcript has been provided."

            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Successfully retrieved transcript for {url}",
                        "done": True,
                    },
                }
            )
            return f"Title: {data[0].metadata.get('title')}\nTranscript:\n{data[0].page_content}"
        except:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Failed to retrieve transcript for {url}.",
                        "done": True,
                    },
                }
            )
            return f"The tool failed with an error. No transcript has been provided.\nError Traceback: \n{traceback.format_exc()}"

