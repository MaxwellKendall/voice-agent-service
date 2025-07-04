from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

VECTOR_STORE_NAME = "ACME Shop Product Knowledge Base"
FILE_PATH = "../docs/test.pdf"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def upload_file(file_path: str, vector_store_id: str):
    file_name = os.path.basename(file_path)
    try:
        file_response = client.files.create(file=open(file_path, 'rb'), purpose="assistants")
        attach_response = client.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=file_response.id
        )
        return {"file": file_name, "status": "success"}
    except Exception as e:
        print(f"Error with {file_name}: {str(e)}")
        return {"file": file_name, "status": "failed", "error": str(e)}

def create_vector_store(store_name: str) -> dict:
    try:
        vector_store = client.vector_stores.create(name=store_name)
        details = {
            "id": vector_store.id,
            "name": vector_store.name,
            "created_at": vector_store.created_at,
            "file_count": vector_store.file_counts.completed
        }
        print("Vector store created:", details)
        return details
    except Exception as e:
        print(f"Error creating vector store: {e}")
        return {}
    
vector_store_id = create_vector_store(VECTOR_STORE_NAME)
upload_file(FILE_PATH, vector_store_id["id"])