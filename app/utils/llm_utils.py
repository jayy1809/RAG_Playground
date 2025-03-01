from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
import asyncio
from typing import List, Dict
from app.config.settings import Settings
from app.prompts.rag_generation import RAGPrompts
import json


class LLMUtils:
    def __init__(self):
        self.settings = Settings()
        self.prompts = RAGPrompts()
        
    async def generate_questions(self, chunk: str):
        llm = ChatGroq(model="mixtral-8x7b-32768", api_key=self.settings.GROQ_API_KEY)
        prompt = self.prompts.single_chunk_questions_prompt
        chain = prompt | llm
        response = chain.invoke({"chunk": chunk})
        await asyncio.sleep(self.settings.LLM_REQUEST_DELAY)
        return [q.strip() for q in response.content.split('\n') if q.strip()]
    
    # async def generate_multi_chunk_question(self, chunks: List[Dict]):
    #     llm = ChatGroq(model="mixtral-8x7b-32768", api_key=self.settings.GROQ_API_KEY)
    #     # print(chunks[0])
    #     # combined_chunks = "\n\n".join(chunks)
    #     combined_chunks = json.dumps(chunks)
    #     # print(combined_chunks)
    #     # print(len(chunks))
    #     prompt = self.prompts.multi_chunk_question_prompt
    #     chain = prompt | llm
    #     response = chain.invoke({"combined_chunks": combined_chunks})
    #     print(response)
    #     await asyncio.sleep(self.settings.LLM_REQUEST_DELAY)
    #     return response.content.strip()