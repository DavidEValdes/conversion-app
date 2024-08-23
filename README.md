# Oracle 2 Postgres Conversion App

This web app: **Uses "Ora2PG" to convert Oracle to Postgresql code, uses Supabase to validate and return invalid or valid repsonse**

[Intern Project Powerpoint.pdf](https://github.com/user-attachments/files/16731107/Intern.Project.pdf.pdf)



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

## Testing Methodology:

1. Rule-based approach (Ora2pg): 
    * Implement Ora2pg in your pipeline
    * No additional data needed
    * Serves as a baseline for comparison
2. General-Purpose LLM (GPT-3.5-turbo): 
    * Set up an API connection to a service like OpenAI's GPT
    * Craft effective prompts for SQL conversion
    * No additional training data needed
3. Rule-based/General-purpose Hybrid: 
    * Combine Ora2pg output with LLM 
    * May require some experimentation to find the best way to combine the two

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
