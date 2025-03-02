import json
from typing import Dict, List

import httpx

from app.config.settings import Settings
from app.prompts import rag_generation


class LLMUtils:
    def __init__(self):
        self.settings = Settings()
        self.rag_generation = rag_generation
        self.model = "mixtral-8x7b-32768"

    async def _make_groq_request(
        self, messages: List[Dict[str, str]], model: str, **params
    ):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.settings.GROQ_API_KEY}",
        }

        data = {"messages": messages, "model": model, **params}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.settings.GROQ_BASE_URL, headers=headers, json=data
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            print(f"GROQ API error: {str(e)}")
            return {"error": str(e)}
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return {"error": str(e)}

    async def generate_questions(self, chunk: str):
        """Generate questions based on a single text chunk."""
        user_msg = f"Text chunk:\n{chunk}"

        response = await self._make_groq_request(
            messages=[
                {
                    "role": "system",
                    "content": self.rag_generation.GENERATE_QUESTIONS_PROMPT,
                },
                {"role": "user", "content": user_msg},
            ],
            model=self.model,
            temperature=0.7,
            max_tokens=512,
        )

        if "error" in response:
            return ["Could not generate questions - API error"]

        content = response["choices"][0]["message"]["content"]
        return [q.strip() for q in content.split("\n") if q.strip()]

    async def generate_multi_chunk_question(self, chunks: List[Dict]):
        """Generate a single complex question synthesizing multiple chunks."""
        formatted_chunks = "\n\n".join(
            f"Chunk ID: {c['_id']}\nContent: {c['text']}" for c in chunks
        )

        user_msg = f"Text chunks:\n{formatted_chunks}"

        response = await self._make_groq_request(
            messages=[
                {
                    "role": "system",
                    "content": self.rag_generation.GENERATE_MULTI_CHUNK_QUESTION_PROMPT,
                },
                {"role": "user", "content": user_msg},
            ],
            model=self.model,
            temperature=0.3,
            max_tokens=1024,
        )

        if "error" in response:
            return {
                "question": "Could not generate question - API error",
                "relevant_ids": (
                    [chunks[0]["_id"], chunks[1]["_id"]]
                    if len(chunks) >= 2
                    else []
                ),
            }

        raw_content = response["choices"][0]["message"]["content"]
        return self._parse_multi_chunk_response(raw_content, chunks)

    def _parse_multi_chunk_response(self, raw_content: str, chunks: List[Dict]):
        """Parse the raw response from multi-chunk question generation into a structured format."""
        try:
            json_str = raw_content.split("{", 1)[-1].rsplit("}", 1)[0]
            json_str = "{" + json_str + "}"
            result = json.loads(json_str)

            if not all(key in result for key in ["question", "relevant_ids"]):
                raise ValueError("Missing required fields")

            return {
                "question": result["question"].strip(),
                "relevant_ids": [str(id) for id in result["relevant_ids"]],
            }
        except (json.JSONDecodeError, ValueError) as e:
            print(f"JSON parse error: {str(e)}")
            return {
                "question": raw_content.strip(),
                "relevant_ids": [c["_id"] for c in chunks[:2]],
            }
