from langchain_core.prompts import ChatPromptTemplate

class RAGPrompts:
    @property
    def single_chunk_questions_prompt(self):
        return ChatPromptTemplate.from_template(
            # """First, analyze the content of the provided text chunk. Based on your analysis,
            # determine if the chunk contains sufficient diversity to generate 3 distinct questions.
            # If it does, create 3 questions; otherwise, generate 2 questions.
            # Ensure the questions incorporate technical terms, paraphrases, and some out-of-vocabulary words.
            # Return only the questions, separated by newlines.\n\nText: {chunk}"""

            # """First, Analyze the provided text chunk and assess its content diversity.
            # Based on your analysis, If it offers enough variety, generate 3 distinct questions; if not, produce 2.
            # Ensure the questions incorporate technical terms, paraphrases, and some out-of-vocabulary words.
            # while avoiding numbered prefixes (e.g., '1. '). Return only the questions, separated by newlines.
            # \n\nText: {chunk}"""
        
            """First, Analyze the provided text chunk and assess its content diversity.
            Based on your analysis, If it offers enough variety, generate 3 distinct questions; if not, produce 2.
            Ensure the questions incorporate technical terms, paraphrases, and some out-of-vocabulary words.
            but under no circumstances include numbered prefixes (e.g., '1. ') or any prefix whatsoever—keep it strictly prefix-free.
            Return only the questions, separated by newlines.\n\nText: {chunk}. Return only the questions, separated by newlines.
            \n\nText: {chunk}""" 
        )
    
    @property
    def multi_chunk_question_prompt(self):
        return ChatPromptTemplate.from_template(
            # """I'm going to provide you with several text chunks with chunk ids. Generate ONE question that requires synthesizing 
            # information from multiple chunks to answer completely. The question should be complex enough 
            # that it cannot be answered by any single chunk alone.
            
            # Text chunks:
            # {combined_chunks}
            
            # Return only the question without any additional text or numbering."""

            multi_chunk_question_prompt = ChatPromptTemplate.from_template(
            """You're provided with multiple text chunks, each with an '_id' and 'text'. 
                Generate ONE complex question that requires synthesizing information from at least two chunks to answer fully, 
                ensuring it cannot be answered by any single chunk alone. 
                Identify the '_id's of the chunks most relevant to answering the question. 
                Return a JSON object in this exact format:\n
                {
                    "question": "<your synthesized question>",
                    "relevant_ids": ["<id1>", "<id2>", ...]
                }\n
                Do not include additional text outside the JSON.\n\nText chunks: {combined_chunks}"""
            )
        )