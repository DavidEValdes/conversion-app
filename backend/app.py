from flask import Flask, request, jsonify
from flask_cors import CORS
from converter import convert_sql
from dotenv import load_dotenv
import os

load_dotenv()  # This loads the variables from .env

app = Flask(__name__)
CORS(app)

@app.route('/convert', methods=['POST'])
def convert():
    data = request.json
    oracle_sql = data.get('oracle_sql', '')
    postgres_sql = convert_sql(oracle_sql)
    return jsonify({'postgres_sql': postgres_sql})

if __name__ == '__main__':
    app.run(debug=True)