import subprocess
import os
import tempfile

def convert_sql(oracle_sql):
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.sql') as temp_input:
        temp_input.write(oracle_sql)
        temp_input_path = temp_input.name

    temp_output_path = tempfile.mktemp(suffix='.sql')

    try:
        subprocess.run([
            'ora2pg',
            '-c', 'ora2pg_config.conf',
            '-i', temp_input_path,
            '-o', temp_output_path,
            '--print_header', '0',
            '--type', 'QUERY'
        ], check=True, capture_output=True, text=True)

        with open(temp_output_path, 'r') as temp_output:
            postgres_sql = temp_output.read()

        return postgres_sql
    except subprocess.CalledProcessError as e:
        return f"Conversion error: {e.stderr}"
    finally:
        os.unlink(temp_input_path)
        if os.path.exists(temp_output_path):
            os.unlink(temp_output_path)