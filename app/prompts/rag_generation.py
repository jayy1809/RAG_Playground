GENERATE_QUESTIONS_PROMPT = """First, Analyze the provided text chunk and assess its content diversity.
    Based on your analysis, If it offers enough variety, generate 3 distinct questions; if not, produce 2.
    Ensure the questions incorporate technical terms, paraphrases, and some out-of-vocabulary words.
    but under no circumstances include numbered prefixes (e.g., '1. ') or any prefix whatsoever—keep it strictly prefix-free.
    Return only the questions, separated by newlines."""

GENERATE_MULTI_CHUNK_QUESTION_PROMPT = """You're provided with multiple text chunks, each with an '_id' and 'text'. 
    Generate ONE complex question that requires synthesizing information from at least two chunks to answer fully, 
    ensuring it cannot be answered by any single chunk alone. 
    Identify the '_id's of the chunks most relevant to answering the question. 
    Return a JSON object in this exact format:\n
    {
        "question": "your synthesized question",
        "relevant_ids": ["id1", "id2", ...]
    }\n
    Do not include additional text outside the JSON.\n\n"""
