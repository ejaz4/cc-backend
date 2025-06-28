import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDBConnection:
    def __init__(self, connection_string=None, database_name=None):
        """
        Initialize MongoDB connection
        
        Args:
            connection_string (str): MongoDB connection string
            database_name (str): Name of the database to use
        """
        self.connection_string = connection_string or Config.MONGODB_URI
        self.database_name = database_name or Config.MONGODB_DATABASE
        self.client = None
        self.db = None
        
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(self.connection_string)
            # Test the connection
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            logger.info(f"Successfully connected to MongoDB database: {self.database_name}")
            return True
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def get_database(self):
        """Get the database instance"""
        if not self.db:
            self.connect()
        return self.db
    
    def get_collection(self, collection_name):
        """Get a specific collection from the database"""
        db = self.get_database()
        return db[collection_name]

# Global connection instance
mongodb_connection = MongoDBConnection()

def get_db():
    """Get database instance"""
    return mongodb_connection.get_database()

def get_collection(collection_name):
    """Get collection instance"""
    return mongodb_connection.get_collection(collection_name)

def connect_db():
    """Connect to database"""
    return mongodb_connection.connect()

def disconnect_db():
    """Disconnect from database"""
    mongodb_connection.disconnect() 