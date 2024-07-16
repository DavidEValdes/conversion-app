import subprocess
import tempfile
import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def convert_sql(oracle_sql):
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

def validate_postgres_sql(postgres_sql):
    try:
        # Execute the converted SQL against Supabase
        result = supabase.rpc('validate_sql', {'sql_query': postgres_sql}).execute()

        # Check if the result contains data
        if result.data and isinstance(result.data, list):
            if 'error' in result.data[0]:
                return {'is_valid': False, 'message': result.data[0]['error']}
            else:
                return {'is_valid': True, 'message': 'SQL is valid'}
        elif isinstance(result.data, dict) and 'message' in result.data and result.data['message'] == 'SQL is valid':
            return {'is_valid': True, 'message': 'SQL is valid'}
        else:
            return {'is_valid': False, 'message': 'Unexpected response format'}
    except Exception as e:
        # Handle specific database errors
        return {'is_valid': False, 'message': f"Execution error: {str(e)}"}

def load_test_queries():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    json_path = os.path.join(project_root, 'data', 'oracle_test_queries.json')

    with open(json_path, 'r') as f:
        return json.load(f)

# Test function
if __name__ == "__main__":
    # Test conversion
    oracle_sql = "SELECT * FROM dual"
    postgres_sql = convert_sql(oracle_sql)
    print(f"Converted SQL: {postgres_sql}")

    # Test validation
    validation_result = validate_postgres_sql(postgres_sql)
    print(f"Is valid: {validation_result['is_valid']}")
    print(f"Result: {validation_result['message']}")

    # Test loading queries
    test_queries = load_test_queries()
    print(f"Loaded {len(test_queries['queries'])} test queries")
