from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import time
from app.config.settings import Settings

class LLMUtils:
    def __init__(self):
        self.settings = Settings()
        
    def generate_questions(self, chunk: str):
        llm = ChatGroq(model="mixtral-8x7b-32768", api_key=self.settings.GROQ_API_KEY)
        # llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=self.settings.GEMINI_API_KEY)
        prompt = ChatPromptTemplate.from_template(
            """First, analyze the content of the provided text chunk. Based on your analysis,
            determine if the chunk contains sufficient diversity to generate 3 distinct questions.
            If it does, create 3 questions; otherwise, generate 2 questions.
            Ensure the questions incorporate technical terms, paraphrases, and some out-of-vocabulary words.
            Return only the questions, separated by newlines.\n\nText: {chunk}"""
        )
        chain = prompt | llm
        response = chain.invoke({"chunk": chunk})
        time.sleep(0.9)
        return [q.strip() for q in response.content.split('\n') if q.strip()]