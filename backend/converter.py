import os
import json
import subprocess
import tempfile
from openai import OpenAI
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def convert_sql_rule_based(oracle_sql):
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.sql') as temp_input:
        temp_input.write(oracle_sql)
        temp_input_path = temp_input.name

    temp_output_path = tempfile.mktemp(suffix='.sql')

    try:
        result = subprocess.run([
            'ora2pg',
            '-c', 'ora2pg_config.conf',
            '-i', temp_input_path,
            '-o', temp_output_path,
            '--print_header', '0',
            '--type', 'QUERY',
            '--no_header',
            '--comment_header', '0'
        ], check=True, capture_output=True, text=True)

        if os.path.exists(temp_output_path):
            with open(temp_output_path, 'r') as temp_output:
                postgres_sql = temp_output.read()
        else:
            postgres_sql = result.stdout

        return postgres_sql
    except subprocess.CalledProcessError as e:
        return f"Conversion error: {e.stderr}"
    finally:
        os.unlink(temp_input_path)
        if os.path.exists(temp_output_path):
            os.unlink(temp_output_path)

def convert_sql_gpt3(oracle_sql):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that converts Oracle SQL to PostgreSQL."},
                {"role": "user", "content": f"Convert this Oracle SQL to PostgreSQL and output only the converted SQL code no code blocks:\n\n{oracle_sql}"}
            ],
            max_tokens=150,
            n=1,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"GPT-3 conversion error: {str(e)}"

def convert_sql_hybrid(oracle_sql):
    rule_based = convert_sql_rule_based(oracle_sql)
    gpt3_refined = convert_sql_gpt3(f"Refine this PostgreSQL conversion and output only the converted SQL code no code blocks:\n{rule_based}")
    return gpt3_refined

def validate_postgres_sql(postgres_sql):
    try:
        result = supabase.rpc('validate_sql', {'sql_query': postgres_sql}).execute()
        
        if result.data and isinstance(result.data, dict):
            if 'message' in result.data and result.data['message'] == 'SQL is valid':
                return True, 'SQL is valid'
            elif 'error' in result.data:
                return False, result.data['error']
        
        return False, "Unexpected response from validation function"
    except Exception as e:
        return False, str(e)

def convert_and_validate(oracle_sql, method='rule_based'):
    if method == 'rule_based':
        postgres_sql = convert_sql_rule_based(oracle_sql)
    elif method == 'gpt3':
        postgres_sql = convert_sql_gpt3(oracle_sql)
    elif method == 'hybrid':
        postgres_sql = convert_sql_hybrid(oracle_sql)
    else:
        return None, False, "Invalid method"

    is_valid, validation_result = validate_postgres_sql(postgres_sql)
    return postgres_sql, is_valid, validation_result

def load_test_queries():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    json_path = os.path.join(project_root, 'data', 'oracle_test_queries.json')

    with open(json_path, 'r') as f:
        return json.load(f)

# You can add a main block for testing if needed
if __name__ == "__main__":
    # Test your functions here
    pass