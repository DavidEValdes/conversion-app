import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [oracleSQL, setOracleSQL] = useState('');
  const [postgresSQL, setPostgresSQL] = useState('');

  const handleConvert = async () => {
    try {
      const response = await axios.post('http://localhost:5000/convert', { oracle_sql: oracleSQL });
      setPostgresSQL(response.data.postgres_sql);
    } catch (error) {
      console.error('Conversion error:', error);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>SQL Converter Tool</h1>
        <p>Effortlessly convert Oracle SQL to PostgreSQL</p>
      </header>
      <div className="converter-container">
        <textarea
          className="input-area"
          value={oracleSQL}
          onChange={(e) => setOracleSQL(e.target.value)}
          placeholder="Enter Oracle SQL here"
        />
        <button className="convert-button" onClick={handleConvert}>Convert</button>
        <textarea
          className="output-area"
          value={postgresSQL}
          readOnly
          placeholder="Converted PostgreSQL will appear here"
        />
      </div>
    </div>
  );
}

export default App;
