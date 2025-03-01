from typing import List

class TextUtils:
    def chunk_text(self, text: str, chunk_size: int, overlap: int):
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size - overlap)]