import os
import sys
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault("DB_USER", "db_user")
os.environ.setdefault("DB_PASS", "db_pass")
os.environ.setdefault("DB_HOST", "db_host")
os.environ.setdefault("DB_PORT", "5432")
os.environ.setdefault("DB_NAME", "db_name")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.main import app
import json
import yaml


def generate_openapi_spec(path: str = "./docs/", name: str = "openapi", ext: str = "yaml"):
    """
    Generate an OpenAPI specification file.
    """
    os.makedirs(path, exist_ok=True)

    openapi_spec = app.openapi()
    with open(f"{path}{name}.{ext}", "w") as f:
        if ext == "json":
            json.dump(openapi_spec, f)
        elif ext == "yaml":
            yaml.dump(openapi_spec, f)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")


if __name__ == "__main__":
    generate_openapi_spec(ext="yaml")
    generate_openapi_spec(ext="json")
