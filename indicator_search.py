"""
Indicator search using TF-IDF and cosine similarity
"""
import time
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import sent_tokenize


class IndicatorSearch:
    """Search for relevant indicators using TF-IDF similarity"""
    
    def __init__(self, indicator_df: pd.DataFrame):
        """
        Initialize indicator search
        
        Args:
            indicator_df: DataFrame containing indicator information
        """
        self.df = indicator_df.copy()
        self._prepare_indicators()
        
    def _prepare_indicators(self):
        """Prepare combined indicator text for searching"""
        self.df['indicator_text'] = (
            "name: " + self.df['name'] +
            " description: " + self.df['description'] +
            " source: " + self.df['source'] +
            " topic: " + self.df['topic']
        ).fillna('')
    
    def _compute_similarity(self, vectorizer, tfidf_matrix, query_part: str):
        """
        Compute cosine similarity between query and indicators
        
        Args:
            vectorizer: Fitted TF-IDF vectorizer
            tfidf_matrix: TF-IDF matrix of indicators
            query_part: Query text to compare
            
        Returns:
            Array of similarity scores
        """
        query_vec = vectorizer.transform([query_part])
        cosine_similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
        return cosine_similarities
    
    def search(self, query: str, top_n: int = 5) -> str:
        """
        Search for top N most relevant indicators
        
        Args:
            query: Search query
            top_n: Number of top results to return
            
        Returns:
            Formatted string of indicator IDs and names
        """
        indicators = self.df['indicator_text'].tolist()
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(indicators)
        
        # Tokenize query into sentences
        query_parts = sent_tokenize(query)
        
        all_results = []
        
        for part in query_parts:
            similarities = self._compute_similarity(vectorizer, tfidf_matrix, part)
            
            temp_df = self.df.copy()
            temp_df['similarity'] = similarities
            top_results = temp_df.sort_values(by='similarity', ascending=False).head(top_n)
            all_results.append(top_results)
        
        # Combine and deduplicate results
        combined_results = pd.concat(all_results).drop_duplicates(subset='id').reset_index(drop=True)
        combined_results = combined_results.sort_values(by='similarity', ascending=False)
        final_results = combined_results.head(top_n)
        
        # Format output
        output = [
            f"id: {row['id']}, indicator_name: {row['name']}\n"
            for _, row in final_results.iterrows()
        ]
        
        return "; ".join(output)