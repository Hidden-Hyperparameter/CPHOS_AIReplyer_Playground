import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__),'.env'))


# os.environ['HTTP_PROXY']="http://127.0.0.1:7890"
# os.environ['HTTPS_PROXY']="http://127.0.0.1:7890"
# os.environ['ALL_PROXY']="socks5://127.0.0.1:7893"



# assert 'OPENAI_API_KEY' in os.environ