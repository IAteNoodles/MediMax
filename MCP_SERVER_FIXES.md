# MCP Server Bug Fixes

## Issues Fixed

### 1. Timeout Parameter Validation Error

**Problem:** 
The `Run_Cypher_Query` function was receiving unexpected `timeout` parameter causing validation errors:
```
ValidationError: 1 validation error for call[run_cypher_query]
timeout: Unexpected keyword argument [type=unexpected_keyword_argument, input_value=120000, input_type=int]
```

**Solution:**
Modified the function signature to accept `**kwargs` for compatibility:
```python
def run_cypher_query(cypher: str, **kwargs) -> dict:
```

### 2. Deprecated id() Function Warnings

**Problem:**
Neo4j was generating deprecation warnings for queries using the `id()` function:
```
WARNING:neo4j.notifications: The query used a deprecated function. ('id' has been replaced by 'elementId or consider using an application-generated id')
```

**Solution:**
- Added automatic detection and warning for deprecated `id()` function usage
- Created `fix_deprecated_cypher()` helper function that automatically replaces `id(p)` with `elementId(p)`
- Added logging to track when queries are automatically fixed

### 3. Query Validation and Error Handling

**Problem:**
Malformed Cypher queries like `"p MRN: p.mrn"` were causing syntax errors that crashed the query execution.

**Solution:**
- Added basic query validation before execution
- Added proper error handling and logging
- Return structured error messages instead of crashing

## Implementation Details

### New Function: `fix_deprecated_cypher()`
```python
def fix_deprecated_cypher(cypher: str) -> str:
    """
    Fix common deprecated Cypher patterns.
    
    Args:
        cypher (str): Original Cypher query
        
    Returns:
        str: Fixed Cypher query with suggestions
    """
    fixed_cypher = cypher
    
    # Replace deprecated id() function with elementId()
    if 'id(' in cypher:
        import re
        fixed_cypher = re.sub(r'\bid\(([^)]+)\)', r'elementId(\1)', fixed_cypher)
        logger.info(f"Fixed deprecated id() function in query")
    
    return fixed_cypher
```

### Enhanced `run_cypher_query()` Function
The function now includes:
- Parameter validation (`**kwargs` for compatibility)
- Basic Cypher syntax checking
- Deprecated function detection and automatic fixing
- Enhanced error reporting
- Query fix tracking (returns both original and fixed queries)

### Response Format
The function now returns additional information when queries are fixed:
```json
{
    "success": true,
    "query": "MATCH (p:Patient) RETURN elementId(p) AS internal_id...",
    "original_query": "MATCH (p:Patient) RETURN id(p) AS internal_id...",
    "results": [...],
    "result_count": 5
}
```

## Benefits

1. **Backward Compatibility**: The server now accepts additional parameters without throwing validation errors
2. **Automatic Migration**: Deprecated `id()` functions are automatically converted to `elementId()`
3. **Better Error Handling**: Malformed queries are caught and reported clearly instead of crashing
4. **Enhanced Logging**: Better visibility into what queries are being executed and fixed
5. **Future-Proof**: Prepared for Neo4j deprecation timeline

## Files Modified

- `backend_noodles/mcp_server.py`:
  - Modified `run_cypher_query()` function signature and implementation
  - Added `fix_deprecated_cypher()` helper function
  - Enhanced error handling and validation

## Testing

A test script (`test_mcp_fixes.py`) was created to verify:
- Timeout parameter compatibility
- Deprecated `id()` function automatic fixing
- Malformed query validation

## Deployment Notes

- The server maintains the same API interface
- No breaking changes for existing clients
- Automatic query fixing is transparent to callers
- Original port 8005 is maintained for compatibility