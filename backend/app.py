from flask import Flask, request, jsonify
from flask_cors import CORS
from converter import convert_sql, validate_postgres_sql

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/convert', methods=['POST', 'OPTIONS'])
def convert():
    if request.method == "OPTIONS":
        return jsonify({"status": "OK"}), 200
    data = request.json
    oracle_sql = data.get('oracle_sql', '')
    
    # Convert Oracle SQL to PostgreSQL
    postgres_sql = convert_sql(oracle_sql)
    
    # Validate the converted SQL against Supabase
    is_valid, validation_result = validate_postgres_sql(postgres_sql)
    
    return jsonify({
        'postgres_sql': postgres_sql,
        'is_valid': is_valid,
        'validation_result': validation_result
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=3000)