import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def list_groq_models():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("No Groq Key")
        return
    client = Groq(api_key=api_key)
    print("Listing Groq models...")
    for m in client.models.list().data:
        print(m.id)

if __name__ == "__main__":
    list_groq_models()
