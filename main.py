"""
Main entry point for the World Bank SQL Agent application
"""
import os
from config import Config
from utils import setup_nltk, load_indicator_data
from few_shot_selector import FewShotSelector
from indicator_search import IndicatorSearch
from agent import WorldBankAgent


def main(user_query: str):
    """
    Main function to process user queries
    
    Args:
        user_query: Natural language query from user
    """
    # Validate configuration
    Config.validate()
    
    # Setup NLTK
    setup_nltk()
    
    # Load indicator data
    print("Loading indicator data...")
    indicator_df = load_indicator_data(Config.DATABASE_PATH)
    
    # Initialize components
    print("Initializing components...")
    few_shot_selector = FewShotSelector()
    indicator_search = IndicatorSearch(indicator_df)
    agent = WorldBankAgent()
    
    # Select relevant few-shot examples
    print("Selecting few-shot examples...")
    selected_examples = few_shot_selector.select_examples(user_query)
    formatted_examples = FewShotSelector.format_examples(selected_examples)
    
    # Search for relevant indicators
    print("Searching for relevant indicators...")
    indicator_ids = indicator_search.search(user_query, top_n=Config.TOP_N_INDICATORS)
    
    # Augment query with indicator IDs if found
    augmented_query = user_query
    if indicator_ids:
        augmented_query += (
            f" . **You should use relevant indicator_id's from these based on their description** "
            f"{{ indicator_id = {indicator_ids} }}"
        )
    
    # Create agent with few-shot examples
    print("Creating SQL agent...")
    agent.create_agent(formatted_examples)
    
    # Execute query
    print("Executing query...")
    response = agent.query_with_tokens(augmented_query)
    
    # Generate summary
    print("Generating summary...")
    summary = agent.generate_summary(user_query, response)
    
    # Print results
    print("\n" + "="*80)
    print(f"User Query: {user_query}")
    print("="*80)
    print(f"\nResponse Summary:\n{summary}")
    print("="*80)
    
    return summary


if __name__ == "__main__":
    # Example query
    query = (
        "Are citizens in developed countries more aware of their rights under "
        "financial consumer protection laws compared to those in developing nations?"
    )
    
    main(query)