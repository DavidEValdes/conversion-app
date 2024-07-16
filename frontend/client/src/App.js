import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [conversionResults, setConversionResults] = useState([]);
  const [error, setError] = useState(null);
  const [testQueries, setTestQueries] = useState([]);
  const [selectedQueries, setSelectedQueries] = useState([]);
  const [convertedQueries, setConvertedQueries] = useState([]);

  useEffect(() => {
    fetch('http://localhost:3000/health')
      .then(response => response.json())
      .then(data => console.log('Server status:', data.status))
      .catch(error => console.error('Error checking server status:', error));

    fetch('http://localhost:3000/test-queries')
      .then(response => response.json())
      .then(data => setTestQueries(data.queries))
      .catch(error => console.error('Error loading test queries:', error));
  }, []);

  const handleConvert = async () => {
    try {
      setError(null);
      const queriesToConvert = selectedQueries.map(id => testQueries.find(q => q.id === parseInt(id)).oracle_sql);

      const response = await fetch('http://localhost:3000/convert', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ oracle_sql_list: queriesToConvert }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setConversionResults(data);
      setConvertedQueries(selectedQueries);  // Update the converted queries
    } catch (error) {
      console.error('Conversion error:', error);
      setError(error.message);
    }
  };

  const handleQuerySelect = (e) => {
    const selectedOptions = Array.from(e.target.selectedOptions, option => option.value);
    setSelectedQueries(selectedOptions);
  };

  const calculateValidPercentage = () => {
    if (conversionResults.length === 0) return 0;
    const validCount = conversionResults.filter(result => result.validation_result.includes('SQL is valid')).length;
    return ((validCount / conversionResults.length) * 100).toFixed(2);
  };

  const calculateInvalidPercentage = () => {
    if (conversionResults.length === 0) return 0;
    const invalidCount = conversionResults.filter(result => !result.validation_result.includes('SQL is valid')).length;
    return ((invalidCount / conversionResults.length) * 100).toFixed(2);
  };

  return (
    <div className="App">
      <header>
        <h1>Oracle to PostgreSQL Converter</h1>
      </header>
      <main>
        <div className="query-selector">
          <h2>Select Queries to Convert</h2>
          <select multiple value={selectedQueries} onChange={handleQuerySelect} size={10}>
            {testQueries.map(query => (
              <option key={query.id} value={query.id}>
                {query.id}: {query.description}
              </option>
            ))}
          </select>
          <button className="convert-button" onClick={handleConvert} disabled={selectedQueries.length === 0}>
            Convert Selected Queries
          </button>
          <div className="dashboard">
            <h2>Conversion Dashboard</h2>
            <p>Valid Queries: {calculateValidPercentage()}%</p>
            <p>Invalid Queries: {calculateInvalidPercentage()}%</p>
          </div>
        </div>
        <div className="results-area">
          <h2>Conversion Results</h2>
          {conversionResults.map((result, index) => {
            const query = testQueries.find(q => q.id === parseInt(convertedQueries[index]));
            return (
              <div key={index} className="conversion-result">
                <h3>Query {convertedQueries[index]}</h3>
                {query && <p className="query-description">{query.description}</p>}
                <div className="sql-display">
                  <div className="sql-column">
                    <h4>Oracle SQL:</h4>
                    <pre>{result.oracle_sql}</pre>
                  </div>
                  <div className="sql-column">
                    <h4>PostgreSQL:</h4>
                    <pre>{result.postgres_sql}</pre>
                  </div>
                </div>
                <div className={`validation ${result.validation_result.includes('SQL is valid') ? 'valid' : 'invalid'}`}>
                  {result.validation_result.includes('SQL is valid') ? 'VALID SQL' : 'Invalid SQL'}
                </div>
                <div className="validation-result">
                  <h4>Validation Result:</h4>
                  <pre>{result.validation_result.replace(/^Execution error: {'message': /, '').replace(/'}$/, '').replace(/'/g, '')}</pre>
                </div>
              </div>
            );
          })}
        </div>
      </main>
      {error && <div className="error">Error: {error}</div>}
    </div>
  );
}

export default App;
