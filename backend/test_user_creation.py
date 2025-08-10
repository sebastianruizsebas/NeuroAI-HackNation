from profai_engine import ProfAIEngine
import os
import json
import sys
import logging

# Set up logging
logging.basicConfig(
    filename='test_user_creation.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_user_creation():
    try:
        logging.info(f"Current directory: {os.getcwd()}")
        
        # Check if data directory exists
        data_dir = os.path.join(os.getcwd(), 'data')
        logging.info(f"Checking data directory: {data_dir}")
        logging.info(f"Data directory exists: {os.path.exists(data_dir)}")
        
        # Check if we can create the directory
        try:
            os.makedirs(data_dir, exist_ok=True)
            logging.info("Successfully created/verified data directory")
        except Exception as e:
            logging.error(f"Error creating data directory: {e}")
            
        # Try to create a test file in the data directory
        test_file = os.path.join(data_dir, 'test.json')
        try:
            with open(test_file, 'w') as f:
                json.dump({"test": "data"}, f)
            logging.info(f"Successfully created test file: {test_file}")
        except Exception as e:
            logging.error(f"Error creating test file: {e}")
            
        logging.info("Initializing ProfAIEngine...")
        
        engine = ProfAIEngine()
        logging.info("ProfAIEngine initialized")
        
        test_name = "TestUser"
        logging.info(f"Creating user: {test_name}")
        
        user_id = engine.create_user(test_name)
        logging.info(f"Successfully created user: {user_id}")
        
        # Try to read the user back
        user_data = engine.get_user(user_id)
        logging.info(f"Retrieved user data: {user_data}")
        
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        import traceback
        logging.error("Traceback:", exc_info=True)

if __name__ == "__main__":
    test_user_creation()
