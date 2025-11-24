import os


def get_api_url():
    host = os.environ.get("API_HOST", "localhost")
    port = 8000 if host == "localhost" else 80
    return f"http://{host}:{port}"


def get_postgres_uri():
    host = os.environ.get("DB_HOST", "localhost")
    port = 54321 if host == "localhost" else 5432
    password = os.environ.get("DB_PASSWORD", "")
    user, db_name = "postgres", "cosmic"
    if password != "":
        url = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    else:
        url = f"postgres://{user}@{host}:{port}/{db_name}"
    return url
