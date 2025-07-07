import os
import sqlite3
import bentoml
from openai import OpenAI
from pydantic import BaseModel

# --- Pydantic Model for Input Validation ---
class Question(BaseModel):
    question: str

# --- Build a reliable, absolute path to the database file ---
# os.path.realpath(__file__) gets the path to this current script (app.py)
# os.path.dirname() gets the directory that app.py is in
# os.path.join() combines the directory path and the filename
_APP_DIR = os.path.dirname(os.path.realpath(__file__))
DB_FILE = os.path.join(_APP_DIR, "erp_database.db")

client = OpenAI()

def get_db_schema() -> str:
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
    # Initialize the schema when the class is defined
    db_schema = get_db_schema()

    @bentoml.api
    def ask(self, data: Question) -> str:
        """
        Accepts a JSON object with a "question" field, executes a SQL query,
        and returns a natural language answer.
        """
        try:
            # --- Step 1: Generate the SQL Query ---
            # vvv --- THE PROMPT HAS BEEN UPDATED --- vvv
            generation_prompt = f"""
            Given the following database schema:
            ---
            {self.db_schema}
            ---
            Please write a SQL query to answer the following question: "{data.question}"
            
            IMPORTANT: When filtering on a text column like 'status', use the LOWER() function to ensure the comparison is case-insensitive. For example, use LOWER(status) = 'pending'.
            
            Only return the SQL query.
            """
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that translates natural language questions into SQL queries."},
                    {"role": "user", "content": generation_prompt}
                ]
            )
            generated_sql = completion.choices[0].message.content
            if "```sql" in generated_sql:
                generated_sql = generated_sql.split("```sql\n")[1].split("```")[0]
            generated_sql = generated_sql.strip()

            # --- Step 2: Execute the SQL Query ---
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(generated_sql)
            results = cursor.fetchall()
            column_names = [description[0] for description in cursor.description]
            conn.close()

            # --- Step 3: Synthesize a Final Answer ---
            synthesis_prompt = f"""
            Given the original question: "{data.question}"
            And the following data retrieved from the database:
            ---
            Columns: {column_names}
            Results: {results}
            ---
            Please provide a clear, concise, natural language answer.
            """
            final_completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes database results into clear, natural language."},
                    {"role": "user", "content": synthesis_prompt}
                ]
            )
            return final_completion.choices[0].message.content.strip()

        except Exception as e:
            return f"An error occurred: {str(e)}"