"""
SQL Agent for querying the World Bank database
"""
from langchain.chat_models import ChatOpenAI
from langchain.agents import create_sql_agent, AgentType
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.callbacks import get_openai_callback
import openai

from config import Config
from prompts import (
    AGENT_INSTRUCTION_PROMPT, 
    get_sql_agent_prefix, 
    SQL_AGENT_SUFFIX,
    get_summary_prompt
)


class WorldBankAgent:
    """Agent for querying World Bank database using natural language"""
    
    def __init__(self, db_url: str = None, api_key: str = None):
        """
        Initialize the World Bank agent
        
        Args:
            db_url: Database connection URL
            api_key: OpenAI API key
        """
        self.db_url = db_url or Config.SQLALCHEMY_DATABASE_URL
        self.api_key = api_key or Config.OPENAI_API_KEY
        
        # Set OpenAI API key
        openai.api_key = self.api_key
        
        # Initialize database and LLM
        self.db = SQLDatabase.from_uri(self.db_url)
        self.llm = ChatOpenAI(
            model_name=Config.CHAT_MODEL,
            temperature=Config.TEMPERATURE,
            api_key=self.api_key
        )
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        self.agent_executor = None
        
    def create_agent(self, few_shots: str):
        """
        Create SQL agent with few-shot examples
        
        Args:
            few_shots: Formatted few-shot examples
        """
        sql_prefix = get_sql_agent_prefix(few_shots)
        
        self.agent_executor = create_sql_agent(
            llm=self.llm,
            toolkit=self.toolkit,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            prefix=sql_prefix,
            suffix=SQL_AGENT_SUFFIX
        )
    
    def query_with_tokens(self, query: str) -> str:
        """
        Execute query and track token usage
        
        Args:
            query: User query string
            
        Returns:
            Agent response or error message
        """
        if not self.agent_executor:
            raise ValueError("Agent not created. Call create_agent() first.")
        
        full_query = AGENT_INSTRUCTION_PROMPT + "\nUser query: " + query
        
        with get_openai_callback() as cb:
            try:
                result = self.agent_executor.run(full_query)
                print(f"Token usage: {cb}")
                return result
            except Exception as e:
                print(f"Error during query execution: {e}")
                return "I don't have sufficient resource to process your query!"
    
    def generate_summary(self, user_query: str, response: str) -> str:
        """
        Generate a summary of the query response
        
        Args:
            user_query: Original user query
            response: Agent response
            
        Returns:
            Summary text
        """
        summary_prompt = get_summary_prompt(user_query, response)
        
        summary_response = openai.chat.completions.create(
            model=Config.SUMMARY_MODEL,
            messages=[{"role": "user", "content": summary_prompt}]
        )
        
        return summary_response.choices[0].message.content