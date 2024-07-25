import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [conversionResults, setConversionResults] = useState([]);
  const [error, setError] = useState(null);
  const [testQueries, setTestQueries] = useState([]);
  const [selectedQueries, setSelectedQueries] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

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
      setIsLoading(true);
      const queriesToConvert = selectedQueries
        .map(id => testQueries.find(q => q.id === parseInt(id))?.oracle_sql)
        .filter(sql => sql);

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
    } catch (error) {
      console.error('Conversion error:', error);
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuerySelect = (e) => {
    const selectedOptions = Array.from(e.target.selectedOptions, option => option.value);
    setSelectedQueries(selectedOptions);
  };

  const calculateValidationRatio = (method) => {
    if (conversionResults.length === 0) return 0;
    const validCount = conversionResults.filter(result => result.method_results[method].validation_result.includes('SQL is valid')).length;
    return ((validCount / conversionResults.length) * 100).toFixed(2);
  };

  const cleanValidationResult = (result) => {
    if (typeof result === 'string') {
      return result.replace(/^\{?'?message'?:\s*'?/, '').replace(/'?\}?$/, '');
    }
    return result;
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
          <button className="convert-button" onClick={handleConvert} disabled={selectedQueries.length === 0 || isLoading}>
            {isLoading ? 'Converting...' : 'Convert Selected Queries'}
          </button>
        </div>
        <div className="results-area">
          <h2>Conversion Results</h2>
          {conversionResults.length > 0 && (
            <div className="validation-ratios">
              <h3>Validation Ratios:</h3>
              <p>Rule-based: {calculateValidationRatio('rule_based')}%</p>
              <p>GPT-3: {calculateValidationRatio('gpt3')}%</p>
              <p>Hybrid: {calculateValidationRatio('hybrid')}%</p>
            </div>
          )}
          {conversionResults.map((result, index) => {
            const selectedQuery = testQueries.find(q => q.id === parseInt(selectedQueries[index]));
            return (
              <div key={index} className="conversion-result">
                <h3>Query {selectedQueries[index]}</h3>
                <p className="query-description">{selectedQuery?.description || 'No description available'}</p>
                <div className="oracle-sql">
                  <h4>Oracle SQL:</h4>
                  <pre>{result.oracle_sql}</pre>
                </div>
                {Object.entries(result.method_results).map(([method, methodResult]) => (
                  <div key={method} className="method-result">
                    <h4>{method.charAt(0).toUpperCase() + method.slice(1)} Method:</h4>
                    <div className="sql-comparison">
                      <div className="before">
                        <h5>Before:</h5>
                        <pre>{result.oracle_sql}</pre>
                      </div>
                      <div className="after">
                        <h5>After:</h5>
                        <pre>{methodResult.postgres_sql}</pre>
                      </div>
                    </div>
                    <div className={`validation ${methodResult.validation_result.includes('SQL is valid') ? 'valid' : 'invalid'}`}>
                      {methodResult.validation_result.includes('SQL is valid') ? 'Valid SQL' : 'Invalid SQL'}
                    </div>
                    <div className="validation-result">
                      <strong>Validation Result:</strong> {cleanValidationResult(methodResult.validation_result)}
                    </div>
                  </div>
                ))}
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