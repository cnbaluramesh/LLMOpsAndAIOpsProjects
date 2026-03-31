import os
from dotenv import load_dotenv

load_dotenv()

class Settings():

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    MODEL_NAME = os.getenv("GROQ_MODEL_NAME")
    
    TEMPERATURE = os.getenv("TEMPERATURE", 0.9)

    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))


settings = Settings()  