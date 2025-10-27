"""
Utility functions for SSL, NLTK downloads, and database operations
"""
import nltk
import ssl
import sqlite3
import pandas as pd


def setup_nltk():
    """Configure SSL and download required NLTK data"""
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    
    # Download required NLTK data
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)


def load_indicator_data(db_path: str, table_name: str = 'Indicator') -> pd.DataFrame:
    """
    Load indicator data from SQLite database
    
    Args:
        db_path: Path to SQLite database
        table_name: Name of the table to query
        
    Returns:
        DataFrame containing indicator data
    """
    conn = sqlite3.connect(db_path)
    try:
        query = f"SELECT * FROM {table_name};"
        df = pd.read_sql(query, conn)
        return df
    finally:
        conn.close()