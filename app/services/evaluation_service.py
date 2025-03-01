import math
from typing import List, Dict

class EvaluationService:
    
    @staticmethod
    def _discounted_cumulative_gain_at_k(retrieved_docs: List[Dict], ground_truth: List[int], k: int) -> float:
        """
        Computes the Discounted Cumulative Gain (DCG) @ K.
        """
        try:
            if not isinstance(retrieved_docs, list) or not isinstance(ground_truth, list) or not isinstance(k, int):
                raise TypeError("Invalid input types. Expected (List[Dict], List[str], int).")
            
            if k <= 0:
                raise ValueError("Parameter 'k' should be a positive integer.")
            
            retrieved_texts = [doc["id"] for doc in retrieved_docs[:k]]
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
    def _ideal_discounted_cumulative_gain_at_k(ground_truth: List[int], k: int) -> float:
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
    def normalized_discounted_cumulative_gain_at_k(retrieved_docs: List[Dict], ground_truth: List[Dict], k: int) -> float:
        """
        Computes the Normalized Discounted Cumulative Gain (NDCG) @ K.
        """
        try:
            if not isinstance(retrieved_docs, list) or not isinstance(ground_truth, list) or not isinstance(k, int):
                raise TypeError("Invalid input types. Expected (List[Dict], List[str], int).")
            
            if k <= 0:
                raise ValueError("Parameter 'k' should be a positive integer.")
            
            ground_truth_texts_ids = [doc["id"] for doc in ground_truth]
            ndcg_at_k = {}
            for i in range(k):
                dcg_at_i = EvaluationService._discounted_cumulative_gain_at_k(retrieved_docs, ground_truth_texts_ids, i+1)
                idcg_at_i = EvaluationService._ideal_discounted_cumulative_gain_at_k(ground_truth_texts_ids, i+1)
                ndcg_at_i = dcg_at_i / idcg_at_i if idcg_at_i > 0 else 0.0
                
                ndcg_at_k[f'NDCG@{i+1}'] = ndcg_at_i
            
            return ndcg_at_k
        
        except Exception as e:
            print(f"Error in normalized_discounted_cumulative_gain_at_k: {e}")
            return {}
    
    @staticmethod
    def bpref(retrieved_docs: List[Dict], ground_truth: List[Dict]) -> float:
        """
        Computes BPREF (Binary Preference).
        """
        try:
            if not isinstance(retrieved_docs, list) or not isinstance(ground_truth, list):
                raise TypeError("Invalid input types. Expected (List[Dict], List[str]).")

            ground_truth_ids = [doc["id"] for doc in ground_truth]
            relevant_docs = set(ground_truth_ids)
            irrelevant_count = 0
            total_relevant = len(relevant_docs)
            bpref_score = 0.0

            if total_relevant == 0:
                return 0.0 
            
            for doc in retrieved_docs:
                if doc["id"] in relevant_docs:
                    bpref_score += (1 - (irrelevant_count / total_relevant))
                else:
                    irrelevant_count += 1

            return bpref_score / total_relevant
    
        except Exception as e:
            print(f"Error in bpref: {e}")
            return 0.0
        
    @staticmethod
    def precision_at_k(retrieved_docs: List[Dict], ground_truth: List[Dict], max_k: int = None) -> Dict[str, float]:
        """
        Computes Precision@K for all k values from 1 to max_k.
        
        Args:
            retrieved_docs: List of retrieved documents, each with an "id" field
            ground_truth: List of ground truth documents, each with an "id" field
            max_k: Maximum k value to compute. If None, uses length of retrieved_docs
            
        Returns:
            Dictionary mapping 'Precision@k' to precision scores for k from 1 to max_k
        """
        try:
            if not isinstance(retrieved_docs, list) or not isinstance(ground_truth, list):
                raise TypeError("Invalid input types. Expected (List[Dict], List[Dict]).")
            
            if max_k is None:
                max_k = len(retrieved_docs)
            elif max_k <= 0:
                raise ValueError("Parameter 'max_k' should be a positive integer.")
                
            ground_truth_ids = set(doc["id"] for doc in ground_truth)
            retrieved_ids = [doc["id"] for doc in retrieved_docs]
            precision_results = {}
            
            for k in range(1, max_k + 1):
                retrieved_at_k = retrieved_ids[:k]
                matches = sum(1 for doc_id in retrieved_at_k if doc_id in ground_truth_ids)
                precision_results[f"Precision@{k}"] = round(matches / float(k), 2) if k > 0 else 0.0
                
            return precision_results
            
        except Exception as e:
            print(f"Error in precision_at_k: {e}")
            return {}
    
    @staticmethod
    def recall_at_k(retrieved_docs: List[Dict], ground_truth: List[Dict], max_k: int = None) -> Dict[str, float]:
        """
        Computes Recall@K for all k values from 1 to max_k.
        
        Args:
            retrieved_docs: List of retrieved documents, each with an "id" field
            ground_truth: List of ground truth documents, each with an "id" field
            max_k: Maximum k value to compute. If None, uses length of retrieved_docs
            
        Returns:
            Dictionary mapping 'Recall@k' to recall scores for k from 1 to max_k
        """
        try:
            if not isinstance(retrieved_docs, list) or not isinstance(ground_truth, list):
                raise TypeError("Invalid input types. Expected (List[Dict], List[Dict]).")
            
            if max_k is None:
                max_k = len(retrieved_docs)
            elif max_k <= 0:
                raise ValueError("Parameter 'max_k' should be a positive integer.")
                
            ground_truth_ids = set(doc["id"] for doc in ground_truth)
            retrieved_ids = [doc["id"] for doc in retrieved_docs]
            recall_results = {}
            
            if len(ground_truth_ids) == 0:
                return {f"Recall@{k}": 0.0 for k in range(1, max_k + 1)}
            
            for k in range(1, max_k + 1):
                retrieved_at_k = set(retrieved_ids[:k])
                matches = len(ground_truth_ids.intersection(retrieved_at_k))
                recall_results[f"Recall@{k}"] = round(matches / float(len(ground_truth_ids)), 2)
                
            return recall_results
            
        except Exception as e:
            print(f"Error in recall_at_k: {e}")
            return {}
    
    @staticmethod
    def f1_score_at_k(retrieved_docs: List[Dict], ground_truth: List[Dict], max_k: int = None) -> Dict[str, float]:
        """
        Computes F1-Score@K for all k values from 1 to max_k.
        
        Args:
            retrieved_docs: List of retrieved documents, each with an "id" field
            ground_truth: List of ground truth documents, each with an "id" field
            max_k: Maximum k value to compute. If None, uses length of retrieved_docs
            
        Returns:
            Dictionary mapping 'F1-Score@k' to F1 scores for k from 1 to max_k
        """
        try:
            if not isinstance(retrieved_docs, list) or not isinstance(ground_truth, list):
                raise TypeError("Invalid input types. Expected (List[Dict], List[Dict]).")
            
            if max_k is None:
                max_k = len(retrieved_docs)
            elif max_k <= 0:
                raise ValueError("Parameter 'max_k' should be a positive integer.")
                
            ground_truth_ids = set(doc["id"] for doc in ground_truth)
            retrieved_ids = [doc["id"] for doc in retrieved_docs]
            f1_score_results = {}
            
            for k in range(1, max_k + 1):
                retrieved_at_k = retrieved_ids[:k]
                
                # Calculate precision
                matches = sum(1 for doc_id in retrieved_at_k if doc_id in ground_truth_ids)
                precision = matches / float(k) if k > 0 else 0.0
                
                # Calculate recall
                recall = matches / float(len(ground_truth_ids)) if ground_truth_ids else 0.0
                
                # Calculate F1 score
                f1 = 0.0
                if precision + recall > 0:
                    f1 = 2 * (precision * recall) / (precision + recall)
                
                f1_score_results[f"F1-Score@{k}"] = round(f1, 2)
                
            return f1_score_results
            
        except Exception as e:
            print(f"Error in f1_score_at_k: {e}")
            return {}
    
    @staticmethod
    def hit_rate_at_k(retrieved_docs: List[Dict], ground_truth: List[Dict], max_k: int = None) -> Dict[str, int]:
        """
        Computes Hit Rate@K for all k values from 1 to max_k.
        (Binary outcome: 1 if at least one relevant document is in top-K, 0 otherwise)
        
        Args:
            retrieved_docs: List of retrieved documents, each with an "id" field
            ground_truth: List of ground truth documents, each with an "id" field
            max_k: Maximum k value to compute. If None, uses length of retrieved_docs
            
        Returns:
            Dictionary mapping 'Hit_Rate@k' to binary hit values for k from 1 to max_k
        """
        try:
            if not isinstance(retrieved_docs, list) or not isinstance(ground_truth, list):
                raise TypeError("Invalid input types. Expected (List[Dict], List[Dict]).")
            
            if max_k is None:
                max_k = len(retrieved_docs)
            elif max_k <= 0:
                raise ValueError("Parameter 'max_k' should be a positive integer.")
                
            ground_truth_ids = set(doc["id"] for doc in ground_truth)
            retrieved_ids = [doc["id"] for doc in retrieved_docs]
            hit_rate_results = {}
            
            for k in range(1, max_k + 1):
                retrieved_at_k = set(retrieved_ids[:k])
                hit = 1 if len(ground_truth_ids.intersection(retrieved_at_k)) > 0 else 0
                hit_rate_results[f"Hit_Rate@{k}"] = hit
                
            return hit_rate_results
            
        except Exception as e:
            print(f"Error in hit_rate_at_k: {e}")
            return {}
    
    @staticmethod
    def reciprocal_rank(retrieved_docs: List[Dict], ground_truth: List[Dict]) -> float:
        """
        Computes Reciprocal Rank.
        
        Args:
            retrieved_docs: List of retrieved documents, each with an "id" field
            ground_truth: List of ground truth documents, each with an "id" field
            
        Returns:
            Dictionary containing:
            - 'rr': Reciprocal Rank score
            - 'individual_ranks': Dictionary mapping relevant document IDs to their ranks
        """
        try:
            if not isinstance(retrieved_docs, list) or not isinstance(ground_truth, list):
                raise TypeError("Invalid input types. Expected (List[Dict], List[Dict]).")
                
            ground_truth_ids = [doc["id"] for doc in ground_truth]
            retrieved_ids = [doc["id"] for doc in retrieved_docs]
            
            ranks = {}
            
            for relevant_id in ground_truth_ids:
                rank = next((i + 1 for i, doc_id in enumerate(retrieved_ids) if doc_id == relevant_id), 0)
                if rank > 0:
                    ranks[relevant_id] = rank
            
            # Calculate reciprocal rank
            # RR = 1/rank of first relevant document
            rr = 0.0
            for doc_id in retrieved_ids:
                if doc_id in ground_truth_ids:
                    rank_position = retrieved_ids.index(doc_id) + 1
                    rr = 1.0 / rank_position
                    break
            
            return rr
            
        except Exception as e:
            print(f"Error in reciprocal_rank: {e}")
            return {"rr": 0.0, "individual_ranks": {}}