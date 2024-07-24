import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
from converter import convert_and_validate, load_test_queries

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3001"}})

@app.route('/convert', methods=['POST', 'OPTIONS'])
def convert():
    if request.method == "OPTIONS":
        return jsonify({"status": "OK"}), 200
    try:
        app.logger.info("Received conversion request")
        data = request.json
        app.logger.debug(f"Request data: {data}")
        oracle_sql_list = data.get('oracle_sql_list', [])
        
        results = []
        for oracle_sql in oracle_sql_list:
            method_results = {}
            for method in ['rule_based', 'gpt3', 'hybrid']:
                try:
                    app.logger.info(f"Converting using method: {method}")
                    postgres_sql, is_valid, validation_result = convert_and_validate(oracle_sql, method)
                    method_results[method] = {
                        'postgres_sql': postgres_sql,
                        'is_valid': is_valid,
                        'validation_result': validation_result
                    }
                except Exception as method_error:
                    app.logger.error(f"Error in method {method}: {str(method_error)}")
                    app.logger.error(traceback.format_exc())
                    method_results[method] = {
                        'error': str(method_error)
                    }
            results.append({
                'oracle_sql': oracle_sql,
                'method_results': method_results
            })
        
        app.logger.info("Conversion completed successfully")
        return jsonify(results)
    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

@app.route('/test-queries', methods=['GET'])
def get_test_queries():
    try:
        queries = load_test_queries()
        return jsonify(queries)
    except Exception as e:
        app.logger.error(f"Error loading test queries: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3000)