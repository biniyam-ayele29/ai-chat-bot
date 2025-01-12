from langchain_community.vectorstores import SQLiteVSS
from langchain_openai import OpenAIEmbeddings
import os
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DBConnection:
    def __init__(self):
        self.db_path = os.getenv("DB_PATH", "src/database/vector_store.db")
        self.table = os.getenv("TABLE", "state_union")
        self.connection: Optional[SQLiteVSS.Connection] = None
        self.vector_store: Optional[SQLiteVSS] = None
        self.embeddings: Optional[OpenAIEmbeddings] = None

    def get_db_path(self) -> str:
        """Get database path - no need for async as it's a simple property access"""
        return self.db_path
    
    def get_table(self) -> str:
        """Get table name - no need for async as it's a simple property access"""
        return self.table
    
    def initialize_connection(self) -> None:
        """Initialize the database connection"""
        try:
            if not self.connection:
                self.connection = SQLiteVSS.create_connection(db_file=self.get_db_path())
                logger.info(f"Database connection initialized at {self.get_db_path()}")
        except Exception as e:
            logger.error(f"Error initializing database connection: {e}")
            raise
    
    async def get_connection(self):
        """Get or create database connection"""
        if not self.connection:
            await self.initialize_connection()
        return self.connection

    async def initialize_embeddings(self) -> None:
        """Initialize the embeddings"""
        try:
            if not self.embeddings:
                self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
                logger.info("Embeddings initialized")
        except Exception as e:
            logger.error(f"Error initializing embeddings: {e}")
            raise

    async def get_embeddings(self):
        """Get or create embeddings"""
        if not self.embeddings:
            await self.initialize_embeddings()
        return self.embeddings

    async def initialize_vector_store(self) -> None:
        """Initialize the vector store"""
        try:
            if not self.vector_store:
                # Ensure we have connection and embeddings
                conn = await self.get_connection()
                embed = await self.get_embeddings()
                
                self.vector_store = SQLiteVSS(
                    embedding=embed,
                    table=self.get_table(),
                    connection=conn
                )
                logger.info(f"Vector store initialized with table {self.get_table()}")
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise

    async def get_vector_store(self):
        """Get or create vector store"""
        if not self.vector_store:
            await self.initialize_vector_store()
        return self.vector_store

    async def close(self) -> None:
        """Close all connections"""
        try:
            if self.connection:
                # Assuming SQLiteVSS connection has a close method 
                await self.connection.close()
                self.connection = None
                logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")
            raise