import os

import dotenv

dotenv.load_dotenv()


def get_api_url():
    host = os.environ.get("API_HOST", "localhost")
    port = 8000 if host == "localhost" else 80
    return f"http://{host}:{port}"


def get_postgres_uri():
    url = os.getenv("DATABASE_URL")
    return url
