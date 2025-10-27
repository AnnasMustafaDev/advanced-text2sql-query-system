"""
Few-shot example selector using semantic similarity
"""
import json
from typing import List, Dict
from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings
from config import Config


class FewShotSelector:
    """Manages few-shot example selection based on semantic similarity"""
    
    def __init__(self, json_path: str = None, api_key: str = None):
        """
        Initialize the few-shot selector
        
        Args:
            json_path: Path to JSON file containing examples
            api_key: OpenAI API key
        """
        self.json_path = json_path or Config.FEW_SHOTS_JSON_PATH
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.examples = self._load_examples()
        
    def _load_examples(self) -> List[Dict]:
        """Load examples from JSON file"""
        with open(self.json_path, 'r') as f:
            json_obj = json.load(f)
            return json_obj['FewShots']
    
    def select_examples(self, query: str, k: int = 5) -> List[Dict]:
        """
        Select the most relevant few-shot examples for a query
        
        Args:
            query: User query to match against
            k: Number of examples to return
            
        Returns:
            List of selected example dictionaries
        """
        example_selector = SemanticSimilarityExampleSelector.from_examples(
            self.examples,
            OpenAIEmbeddings(api_key=self.api_key),
            FAISS,
            k=k,
            input_keys=["input"]
        )
        
        return example_selector.select_examples({"input": query})
    
    @staticmethod
    def format_examples(examples: List[Dict]) -> str:
        """
        Format selected examples into a string for the prompt
        
        Args:
            examples: List of example dictionaries
            
        Returns:
            Formatted string of examples
        """
        formatted = ""
        for shot in examples:
            formatted += f"input: {shot['input']}\n"
            formatted += f"query: {shot['query']}\n\n"
        return formatted