import logging
import os
import sys

# --- Configure logging to print to the console ---
# This ensures that even the earliest messages are captured by the container's log driver.
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

logging.info("Starting app.py script...")

try:
    import sqlite3
    logging.info("Successfully imported sqlite3.")
    import bentoml
    logging.info("Successfully imported bentoml.")
    from openai import OpenAI
    logging.info("Successfully imported OpenAI.")
    from pydantic import BaseModel
    logging.info("Successfully imported BaseModel.")
except ImportError as e:
    logging.error(f"Failed to import a critical library: {e}")
    # Exit if we can't even import our core libraries
    sys.exit(1)


# --- Pydantic Model for Input Validation ---
class Question(BaseModel):
    question: str
logging.info("Pydantic 'Question' model defined.")


# --- Build a reliable, absolute path to the database file ---
try:
    _APP_DIR = os.path.dirname(os.path.realpath(__file__))
    DB_FILE = os.path.join(_APP_DIR, "erp_database.db")
    logging.info(f"Database path constructed: {DB_FILE}")
    if not os.path.exists(DB_FILE):
        logging.warning("Database file does NOT exist at the constructed path!")
    else:
        logging.info("Database file confirmed to exist at the constructed path.")
except Exception as e:
    logging.error(f"Error constructing database path: {e}")


# --- Initialize OpenAI Client ---
try:
    client = OpenAI()
    logging.info("OpenAI client initialized successfully.")
    if os.environ.get("OPENAI_API_KEY") is None:
        logging.warning("OPENAI_API_KEY environment variable not found!")
    else:
        logging.info("OPENAI_API_KEY environment variable is present.")
except Exception as e:
    logging.error(f"Failed to initialize OpenAI client: {e}")


def get_db_schema() -> str:
    """Returns the schema of the database as a string."""
    try:
        logging.info(f"Executing get_db_schema() on {DB_FILE}...")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        logging.info(f"Found tables: {tables}")
        # Return a simple string for this test; we don't need the full schema logic.
        return "mock_schema_read_successfully"
    except Exception as e:
        logging.error(f"Error executing get_db_schema: {e}")
        return "error_reading_schema"


# --- BentoML Service ---
@bentoml.service
class PowerPlantRAGService:
    logging.info("PowerPlantRAGService class is being defined.")

    try:
        db_schema = get_db_schema()
        logging.info(f"db_schema initialized at class level with value: '{db_schema}'")
    except Exception as e:
        logging.error(f"Failed to initialize db_schema at class level: {e}")
        db_schema = "initialization_failed"


    @bentoml.api
    def ask(self, data: Question) -> str:
        logging.info(f"API endpoint /ask received a request. Responding with simple confirmation.")
        # The full RAG logic is temporarily removed to focus on startup issues.
        return f"Request processed. Schema loaded as: '{self.db_schema}'"

logging.info("app.py script definition finished. BentoML will now take over.")