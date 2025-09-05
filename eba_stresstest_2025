# Database Import Setup Prompt

Use this prompt to quickly set up PostgreSQL databases with CSV and Excel data import, avoiding common pitfalls.

## Task Description

I need to create a PostgreSQL database and import data from multiple files (CSV and Excel). Please create a complete setup script that:

1. **Creates the database** with proper connection handling
2. **Analyzes actual data types** instead of using generic VARCHARs  
3. **Imports all data files** with proper error handling
4. **Creates performance indexes** for key fields
5. **Verifies the import** with record counts

## Critical Requirements & Lessons Learned

### Data Type Analysis (CRITICAL)
- **NEVER** assume VARCHAR sizes - always analyze actual data first
- Check max string lengths: `df['column'].str.len().max()`
- Use appropriate types: INTEGER, SMALLINT, DECIMAL(precision,scale), DATE, TEXT
- Example: A bank name might be 63 characters, not 50

### Database Connection Strategy (CRITICAL) 
- **Use SQLAlchemy engine for pandas operations** - raw psycopg2 causes SQLite syntax errors
- **Use psycopg2 for schema operations** (CREATE TABLE, CREATE INDEX)
- **Terminate existing connections** before dropping database:
  ```sql
  SELECT pg_terminate_backend(pid) FROM pg_stat_activity 
  WHERE datname = 'target_db' AND pid <> pg_backend_pid()
  ```

### Column Name Handling (CRITICAL)
- **Clean column names consistently**: spaces to underscore, remove special chars
- **NO DOUBLE UNDERSCORES** - use regex to collapse: `.str.replace('__+', '_', regex=True)`
- **Remove apostrophes** - they break PostgreSQL syntax: `.str.replace("'", '')`
- **Test the cleaning pipeline**: Print cleaned column names vs schema columns
- Example cleaning chain:
  ```python
  df.columns = df.columns.str.lower()\
      .str.replace(' ', '_')\
      .str.replace('\n', '_')\
      .str.replace('(', '').str.replace(')', '')\
      .str.replace(':', '_').str.replace('-', '_').str.replace('/', '_')\
      .str.replace("'", '')\
      .str.replace('__+', '_', regex=True)
  ```

### Schema Design Patterns
- **Main data tables**: Use proper constraints (NOT NULL for required fields)
- **Reference tables**: Use appropriate primary key types (SMALLINT for lookup IDs)
- **Business rules**: Consider foreign key relationships
- **Performance**: Add indexes on frequently queried columns (country_code, lei_code, period)

## Implementation Steps

### Step 1: Environment Setup
```python
import pandas as pd
import psycopg2
from psycopg2 import sql
from sqlalchemy import create_engine
```

### Step 2: Data Analysis Phase
**Before writing any schema:**
1. **Analyze all CSV files** for actual data types and lengths
2. **Check Excel file structure** - sheet names and column structures  
3. **Test column name cleaning** to see exact output
4. **Document findings** before proceeding

### Step 3: Schema Generation
- **Match cleaned column names exactly** - no assumptions
- **Use analyzed data types** - no generic VARCHAR(255)
- **Test schema creation** before data import

### Step 4: Import Implementation  
- **SQLAlchemy engine** for pandas.to_sql()
- **Chunked imports** for large files (chunksize=10000)
- **Error handling** with detailed error messages
- **Progress reporting** for each table

### Step 5: Validation
- **Record count verification** for each table
- **Sample data checks** to ensure integrity
- **Index creation** for performance

## Common Error Patterns to Avoid

### "String data right truncation"
- **Cause**: VARCHAR field too small for actual data
- **Solution**: Analyze max lengths first: `df['field'].str.len().max()`

### "Column does not exist" 
- **Cause**: Mismatch between cleaned column names and schema
- **Solution**: Print both cleaned column names and schema columns to compare

### "Syntax error at or near" special character
- **Cause**: Unescaped special characters in column names
- **Solution**: Comprehensive character cleaning including apostrophes

### "Database is being accessed by other users"
- **Cause**: Existing connections to target database  
- **Solution**: Terminate connections before DROP DATABASE

### "pandas only supports SQLAlchemy connectable"
- **Cause**: Using raw psycopg2 connection with pandas.to_sql()
- **Solution**: Use SQLAlchemy engine for pandas operations

## Database Configuration Template

```python
# Configuration
DB_NAME = "your_database_name"
DB_USER = "postgres"  
DB_HOST = "localhost"
DB_PORT = "5432"  # or your port
DB_PASSWORD = "your_password"

def create_database_connection(db_name=None):
    """PostgreSQL connection for schema operations"""
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, 
        password=DB_PASSWORD, database=db_name or "postgres"
    )

def create_sqlalchemy_engine(db_name=None):
    """SQLAlchemy engine for pandas operations"""
    database = db_name or DB_NAME
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{database}"
    return create_engine(connection_string)
```

## Verification Checklist

- [ ] All CSV files analyzed for proper data types
- [ ] Excel files structure documented (sheet names, columns)
- [ ] Column name cleaning tested and verified
- [ ] Schema matches cleaned column names exactly
- [ ] SQLAlchemy engine used for pandas operations
- [ ] Database creation handles existing connections
- [ ] All tables created without syntax errors
- [ ] Data import completes for all files
- [ ] Record counts match source files
- [ ] Performance indexes created
- [ ] Connection strings work correctly

## Success Criteria

- **Database created** successfully  
- **All tables created** with proper data types  
- **All data imported** without truncation or format errors  
- **Record counts verified** against source files  
- **Performance indexes** created for key fields  
- **No syntax errors** in schema or column names  
- **Script runs end-to-end** without manual intervention

## Final Notes

- **Always analyze first, code second** - don't assume data patterns
- **Test column cleaning early** - it's the most common failure point  
- **Use appropriate tools** - SQLAlchemy for pandas, psycopg2 for schema
- **Validate everything** - data types, column names, record counts
- **Handle edge cases** - special characters, long strings, existing connections

This systematic approach will save hours of debugging and ensure reliable database setup every time.
