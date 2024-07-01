import React, { useState } from 'react';
import axios from 'axios';

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
      <h1>Oracle to PostgreSQL Converter</h1>
      <textarea
        value={oracleSQL}
        onChange={(e) => setOracleSQL(e.target.value)}
        placeholder="Enter Oracle SQL here"
      />
      <button onClick={handleConvert}>Convert</button>
      <textarea
        value={postgresSQL}
        readOnly
        placeholder="Converted PostgreSQL will appear here"
      />
    </div>
  );
}

export default App;