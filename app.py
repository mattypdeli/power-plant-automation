import os
import sqlite3
import bentoml
from openai import OpenAI
from pydantic import BaseModel

# --- Pydantic Model for Input Validation ---
class Question(BaseModel):
    question: str

# --- Configuration ---
DB_FILE = "erp_database.db"
client = OpenAI()

# --- Database Helper Function ---
def get_db_schema():
    """Returns the schema of the database as a string."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    schema_str = ""
    for table_name in tables:
        table_name = table_name[0]
        schema_str += f"Table '{table_name}':\n"
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        for column in columns:
            schema_str += f"  - {column[1]} ({column[2]})\n"
        schema_str += "\n"
    conn.close()
    return schema_str

# --- BentoML Service ---
@bentoml.service
class PowerPlantRAGService:
    db_schema = get_db_schema()

    @bentoml.api
    def ask(self, data: Question) -> str:
        """
        Accepts a JSON object with a "question" field and returns a SQL query.
        """
        # 1. Augmentation: Create a prompt for the LLM
        prompt = f"""
        Given the following database schema:
        ---
        {self.db_schema}
        ---
        Please write a SQL query to answer the following question: "{data.question}"

        Only return the SQL query.
        """

        # 2. Generation: Call the LLM to translate the question to SQL
        try:
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that translates natural language questions into SQL queries."},
                    {"role": "user", "content": prompt}
                ]
            )

            generated_sql = completion.choices[0].message.content
            if "```sql" in generated_sql:
                generated_sql = generated_sql.split("```sql\n")[1].split("```")[0]

            return generated_sql.strip()

        except Exception as e:
            return f"An error occurred: {str(e)}"