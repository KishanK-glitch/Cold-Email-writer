from masumi import run
from agent import process_job
import os
from dotenv import load_dotenv

load_dotenv()
# This strictly follows the Masumi SDK schema format
INPUT_SCHEMA = {
    "input_data": [
        {
            "id": "url", 
            "type": "string", 
            "name": "Target Company URL",
            "description": "The website of the company you want to pitch."
        },
        {
            "id": "user_offering", 
            "type": "string", 
            "name": "Your Offering",
            "description": "A brief description of the product or service you are selling."
        }
    ]
}

if __name__ == "__main__":
    run(
        start_job_handler=process_job,
        input_schema_handler=INPUT_SCHEMA
    )