import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__),'.env'))
# assert 'OPENAI_API_KEY' in os.environ