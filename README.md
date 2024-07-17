# Oracle 2 Postgres Conversion App

This web app: **Uses "Ora2PG" to convert Oracle to Postgresql code, uses Supabase to validate and return invalid or valid repsonse**


![Screen Recording 2024-07-16 at 6 05 15 PM](https://github.com/user-attachments/assets/59ac8497-78ba-44c3-a02c-f5d43a42df81)



## Current Supabase function used for validation

```
DECLARE
  result JSONB;
  ddl_keywords TEXT[] := ARRAY['CREATE', 'ALTER', 'DROP', 'TRUNCATE'];
BEGIN
  IF EXISTS (SELECT 1 FROM unnest(ddl_keywords) keyword WHERE sql_query ILIKE keyword || '%') THEN
    result := jsonb_build_object('message', 'DDL statement - assumed valid');
  ELSE
    BEGIN
      EXECUTE 'PREPARE test_stmt AS ' || sql_query;
      result := jsonb_build_object('message', 'SQL is valid');
      EXECUTE 'DEALLOCATE test_stmt';
    EXCEPTION WHEN OTHERS THEN
      result := jsonb_build_object('error', SQLERRM);
    END;
  END IF;

  RETURN COALESCE(result, jsonb_build_object('error', 'No result generated'));
END;

```

## Next Steps:

1. Rule-based approach (Ora2pg): ✅
    * Implement Ora2pg in your pipeline
    * No additional data needed
    * Serves as a baseline for comparison
2. General-Purpose LLM (API Wrapper):
    * Set up an API connection to a service like OpenAI's GPT
    * Craft effective prompts for SQL conversion
    * No additional training data needed
3. Rule-based/General-purpose Hybrid:
    * Combine Ora2pg output with LLM 
    * May require some experimentation to find the best way to combine the two
4. Knowledge Base Embedding Model:
    * Requires a dataset of Oracle to PostgreSQL conversions
    * Need to implement embedding creation and similarity search
    * Considering using sentence-transformers for embeddings
5. Domain-Specific Fine-Tuned Model:
    * Requires a large dataset of Oracle to PostgreSQL conversions
    * Need access to significant computational resources for training
    * Considering using Hugging Face's Transformers library 



## Execute the converted SQL on an actual PostgreSQL database and compare the results with the original Oracle query
 
Automated test harness with comparison functions for near 100% validation:

Full Database Mirroring:

Create an exact copy of your Oracle database schema in PostgreSQL.
Migrate all data from Oracle to PostgreSQL.
Keep both databases synchronized in real-time or with frequent updates.


Exhaustive Query Testing:

Execute every converted query on both Oracle and PostgreSQL databases.
Compare results bit-by-bit, including data types, precision, and scale.


Transactional Integrity Testing:

Test multi-statement transactions in both databases.
Verify that ACID properties are maintained identically.


Concurrency and Locking Behavior:

Test concurrent operations to ensure locking mechanisms work similarly.
Verify isolation levels behave the same in both databases.


Performance Profiling:

Compare execution plans and query performance.
Ensure indexes are used similarly in both databases.


Stored Procedure and Function Testing:

Convert and test all stored procedures and functions.
Verify that they produce identical results and side effects.


Trigger Behavior Verification:

Test all database triggers to ensure they fire under the same conditions.
Verify that trigger actions produce identical results.


Data Type Handling:

Test all data types, especially those with different representations (e.g., DATE, TIMESTAMP).
Verify that type conversions and comparisons work identically.


Null Handling:

Extensively test NULL value behavior in all contexts.


Error Handling and Exceptions:

Verify that error conditions produce equivalent results.
Test exception handling in procedural code.


Constraint Enforcement:

Test all constraints (PRIMARY KEY, FOREIGN KEY, CHECK, UNIQUE) for identical behavior.


Sequence and Auto-increment Behavior:

Verify that sequence generation and usage is equivalent.


Full Text Search Equivalence:

If used, ensure full-text search capabilities are equivalent.


User-Defined Types and Functions:

Test all user-defined types and functions for equivalent behavior.


Permissions and Security:

Verify that user permissions and roles translate correctly.


Backup and Recovery:

Test backup and recovery processes to ensure data integrity is maintained identically.


Comprehensive Edge Case Testing:

Identify and test all possible edge cases in your specific database usage.


## License

    Copyright [2024] [David Valdes]

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
