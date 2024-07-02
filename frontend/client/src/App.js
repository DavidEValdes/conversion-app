import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [oracleSQL, setOracleSQL] = useState('');
  const [postgresSQL, setPostgresSQL] = useState('');
  const [isValid, setIsValid] = useState(null);
  const [validationResult, setValidationResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('http://localhost:3000/health')
      .then(response => response.json())
      .then(data => console.log('Server status:', data.status))
      .catch(error => console.error('Error checking server status:', error));
  }, []);

  const handleConvert = async () => {
    try {
      setError(null);
      const response = await fetch('http://localhost:3000/convert', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ oracle_sql: oracleSQL }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setPostgresSQL(data.postgres_sql);
      setIsValid(data.is_valid);
      setValidationResult(data.validation_result);
    } catch (error) {
      console.error('Conversion error:', error);
      setError(error.message);
    }
  };

  return (
    <div className="App">
      <h1>Oracle to PostgreSQL Converter</h1>
      <div className="converter">
        <div className="panel">
          <h2>Oracle SQL</h2>
          <textarea
            value={oracleSQL}
            onChange={(e) => setOracleSQL(e.target.value)}
            placeholder="Enter Oracle SQL here"
          />
        </div>
        <button onClick={handleConvert}>Convert &gt;</button>
        <div className="panel">
          <h2>PostgreSQL</h2>
          <textarea
            value={postgresSQL}
            readOnly
            placeholder="Converted PostgreSQL will appear here"
          />
          {isValid !== null && (
            <div className={`validation ${isValid ? 'valid' : 'invalid'}`}>
              {isValid ? 'Valid SQL' : 'Invalid SQL'}
            </div>
          )}
          {validationResult && (
            <div className="validation-result">
              <h3>Validation Result:</h3>
              <pre>{JSON.stringify(validationResult, null, 2)}</pre>
            </div>
          )}
        </div>
      </div>
      {error && <div className="error">Error: {error}</div>}
    </div>
  );
}

export default App;