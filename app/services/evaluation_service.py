import math
from typing import List, Dict

class EvaluationService:
    
    @staticmethod
    def _discounted_cumulative_gain_at_k(retrieved_docs: List[Dict], ground_truth: List[str], k: int) -> float:
        """
        Computes the Discounted Cumulative Gain (DCG) @ K.
        """
        try:
            if not isinstance(retrieved_docs, list) or not isinstance(ground_truth, list) or not isinstance(k, int):
                raise TypeError("Invalid input types. Expected (List[Dict], List[str], int).")
            
            if k <= 0:
                raise ValueError("Parameter 'k' should be a positive integer.")
            
            retrieved_texts = [doc["chunk"] for doc in retrieved_docs[:k]]
            relevance_scores = [1 if doc in ground_truth else 0 for doc in retrieved_texts]
            
            if not relevance_scores:
                return 0.0

            dcg_at_k = relevance_scores[0] if relevance_scores else 0
            for i in range(1, len(relevance_scores)):
                dcg_at_k += relevance_scores[i] / math.log2(i + 1)

            return dcg_at_k

        except Exception as e:
            print(f"Error in discounted_cumulative_gain_at_k: {e}")
            return 0.0


    @staticmethod
    def _ideal_discounted_cumulative_gain_at_k(ground_truth: List[str], k: int) -> float:
        """
        Computes the Ideal Discounted Cumulative Gain (IDCG) @ K.
        """
        try:
            if not isinstance(ground_truth, list) or not isinstance(k, int):
                raise TypeError("Invalid input types. Expected (List[str], int).")
            
            if k <= 0:
                raise ValueError("Parameter 'k' should be a positive integer.")
            
            ideal_relevance_scores = [1] * min(len(ground_truth), k)
            
            if not ideal_relevance_scores:
                return 0.0
            
            idcg_at_k = ideal_relevance_scores[0] if ideal_relevance_scores else 0
            for i in range(1, len(ideal_relevance_scores)):
                idcg_at_k += ideal_relevance_scores[i] / math.log2(i + 1)

            return idcg_at_k
    
        except Exception as e:
            print(f"Error in ideal_discounted_cumulative_gain_at_k: {e}")
            return 0.0
    
    @staticmethod
    def normalized_discounted_cumulative_gain_at_k(retrieved_docs: List[Dict], ground_truth: List[str], k: int) -> float:
        """
        Computes the Normalized Discounted Cumulative Gain (NDCG) @ K.
        """
        try:
            if not isinstance(retrieved_docs, list) or not isinstance(ground_truth, list) or not isinstance(k, int):
                raise TypeError("Invalid input types. Expected (List[Dict], List[str], int).")
            
            if k <= 0:
                raise ValueError("Parameter 'k' should be a positive integer.")
            
            ndcg_at_k = {}
            for i in range(k):
                dcg_at_i = EvaluationService._discounted_cumulative_gain_at_k(retrieved_docs, ground_truth, i+1)
                idcg_at_i = EvaluationService._ideal_discounted_cumulative_gain_at_k(ground_truth, i+1)
                ndcg_at_i = dcg_at_i / idcg_at_i if idcg_at_i > 0 else 0.0
                
                ndcg_at_k[f'NDCG@{i+1}'] = ndcg_at_i
            
            return ndcg_at_k
        
        except Exception as e:
            print(f"Error in normalized_discounted_cumulative_gain_at_k: {e}")
            return {}
    
    @staticmethod
    def bpref(retrieved_docs: List[Dict], ground_truth: List[str]) -> float:
        """
        Computes BPREF (Binary Preference).
        """
        try:
            if not isinstance(retrieved_docs, list) or not isinstance(ground_truth, list):
                raise TypeError("Invalid input types. Expected (List[Dict], List[str]).")

            relevant_docs = set(ground_truth)
            irrelevant_count = 0
            total_relevant = len(relevant_docs)
            bpref_score = 0.0

            if total_relevant == 0:
                return 0.0 
            
            for doc in retrieved_docs:
                if doc["chunk"] in relevant_docs:
                    bpref_score += (1 - (irrelevant_count / total_relevant))
                else:
                    irrelevant_count += 1

            return bpref_score / total_relevant
    
        except Exception as e:
            print(f"Error in bpref: {e}")
            return 0.0
    
