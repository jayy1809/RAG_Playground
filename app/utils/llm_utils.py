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
        
    async def generate_multi_chunk_question(self, chunks: List[Dict]):
        llm = ChatGroq(model="mixtral-8x7b-32768", api_key=self.settings.GROQ_API_KEY)
        # combined_chunks = json.dumps(chunks)
        combined_chunks = json.dumps(chunks, ensure_ascii=False)
        # combined_chunks = chunks
        # print(combined_chunks[1])
        print(type(combined_chunks))
        # print(chunks[0])
        prompt = self.prompts.multi_chunk_question_prompt
        # print(prompt)
        chain = prompt | llm
        # print(chain)
        response = chain.invoke({"combined_chunks": combined_chunks})
        # response = chain.invoke({"combined_chunks": chunks[0]})
        # print(response)
        await asyncio.sleep(self.settings.LLM_REQUEST_DELAY)
        try:
            result = json.loads(response.content.strip())
            if "question" not in result or "relevant_ids" not in result:
                raise ValueError("LLM response missing required fields")
            return result
        except json.JSONDecodeError:
            # Fallback handling if the LLM doesn't return valid JSON
            return {
                "question": response.content.strip(),
                "relevant_ids": [chunk["_id"] for chunk in chunks[:2]]  # Default to first two chunks
            }
            result = json.loads(response.content.strip())

            return {"question": result["question"], "relevant_ids": result["relevant_ids"]}
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid multi-chunk response from LLM: {response.content} - Error: {str(e)}")
        # return response.content.strip()


    # async def generate_multi_chunk_question(self, chunks: List[Dict]):
    #     try:
    #         llm = ChatGroq(model="mixtral-8x7b-32768", api_key=self.settings.GROQ_API_KEY)

    #         print(f"Input to generate_multi_chunk_question: {type(chunks)}")
            
    #         # Handle the case where chunks might already be a string
    #         if isinstance(chunks, str):
    #             print("Chunks is already a string")
    #             combined_chunks = chunks
    #         else:
    #             try:
    #                 # Convert chunks list to JSON string
    #                 combined_chunks = json.dumps(chunks, ensure_ascii=False)
    #                 print(f"Serialized chunks to JSON string: {combined_chunks[:100]}...")
    #             except Exception as e:
    #                 print(f"Error serializing chunks: {str(e)}")
    #                 # Fallback to a simpler representation
    #                 combined_chunks = str(chunks)
            
    #         prompt = self.prompts.multi_chunk_question_prompt
    #         chain = prompt | llm
            
    #         # Invoke the model
    #         print("Invoking LLM...")
    #         response = chain.invoke({"combined_chunks": combined_chunks})
    #         print(f"LLM response received: {response.content[:100]}...")
    #         await asyncio.sleep(self.settings.LLM_REQUEST_DELAY)
            
    #         # CHANGE: More robust parsing
    #         try:
    #             # Try to find and extract JSON from the response
    #             content = response.content.strip()
    #             # Find JSON object markers if they exist
    #             json_start = content.find('{')
    #             json_end = content.rfind('}') + 1
                
    #             if json_start >= 0 and json_end > json_start:
    #                 # Extract just the JSON part
    #                 json_str = content[json_start:json_end]
    #                 result = json.loads(json_str)
                    
    #                 # Validate the result
    #                 if "question" not in result or "relevant_ids" not in result:
    #                     print("Missing fields in parsed JSON")
    #                     raise ValueError("Required fields missing")
                        
    #                 return result
    #             else:
    #                 # No JSON markers found
    #                 print("No JSON format found in response")
    #                 raise ValueError("No JSON in response")
                    
    #         except (json.JSONDecodeError, ValueError) as e:
    #             print(f"Error parsing response: {str(e)}")
    #             # Parse manually as a fallback
    #             content = response.content.strip()
                
    #             # Try to extract a question
    #             question_marker = content.lower().find("question")
    #             if question_marker >= 0:
    #                 question_end = content.find("\n", question_marker)
    #                 if question_end == -1:
    #                     question_end = len(content)
    #                 question = content[question_marker:question_end].replace("question:", "").strip()
    #             else:
    #                 # Just use the whole content
    #                 question = content
                    
    #             # Default ids to all chunks
    #             return {
    #                 "question": question,
    #                 "relevant_ids": [chunk.get("_id", "unknown") for chunk in chunks[:2]]
    #             }
                
    #     except Exception as e:
    #         print(f"Error in generate_multi_chunk_question: {str(e)}")
    #         # Return a fallback result with a default question
    #         return {
    #             "question": "What key information can be derived from these related texts?",
    #             "relevant_ids": [chunk.get("_id", "unknown") for chunk in chunks[:2] if isinstance(chunk, dict)]
    #         }