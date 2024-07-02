import subprocess
import tempfile
import os
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
            '--no_header',  # Ensures no headers are printed
            '--comment_header', '0'  # Ensures no comments are printed
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
        result = supabase.rpc('execute_sql', {'sql_query': postgres_sql}).execute()
        
        # Check if the result contains an error message
        if result.data and result.data[0].get('result_text', '').startswith('ERROR:'):
            return False, result.data[0]['result_text']
        
        return True, result.data
    except Exception as e:
        return False, str(e)

# You might want to add a main function for testing purposes
if __name__ == "__main__":
    # Test conversion
    oracle_sql = "SELECT * FROM dual"
    postgres_sql = convert_sql(oracle_sql)
    print(f"Converted SQL: {postgres_sql}")

    # Test validation
    is_valid, result = validate_postgres_sql(postgres_sql)
    print(f"Is valid: {is_valid}")
    print(f"Result: {result}")