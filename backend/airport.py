from typing import Dict, Any, Tuple
from const import DATABASE_URL
import asyncpg
# Function to search airport using PostgreSQL Levenshtein distance
import asyncpg
from rapidfuzz import process, fuzz
from typing import Dict, Any





async def search_airport(query: str) -> Dict[str, Any]:
    """
    Search for airport information using Levenshtein distance in the PostgreSQL database.
    """
    conn = await asyncpg.connect(DATABASE_URL)

    # SQL query to find the closest matching airport name or city using Levenshtein distance
    sql = """
    WITH exact_match AS (
    SELECT airport_name, city, state_ut, iata_code
    FROM airport_codes
    WHERE lower(city) = lower($1)
),
partial_match AS (
    SELECT airport_name, city, state_ut, iata_code
    FROM airport_codes
    WHERE lower(city) ILIKE '%' || lower($1) || '%'
),
levenshtein_match AS (
    SELECT airport_name, city, state_ut, iata_code
    FROM airport_codes
    ORDER BY levenshtein(lower(city), lower($1)) ASC
    LIMIT 1
)


SELECT * FROM exact_match
UNION ALL
SELECT * FROM partial_match
WHERE NOT EXISTS (SELECT 1 FROM exact_match)
UNION ALL
SELECT * FROM levenshtein_match
WHERE NOT EXISTS (SELECT 1 FROM exact_match)
  AND NOT EXISTS (SELECT 1 FROM partial_match)
LIMIT 1;


    """
    try:
        result = await conn.fetchrow(sql, query)
        await conn.close()
        if result:
            return {
                "airport_name": result["airport_name"],
                "city": result["city"],
                "state_ut": result["state_ut"],
                "iata_code": result["iata_code"]
            }
        else:
            return {"status": False, "message": "No matching airport found."}
    except Exception as e:
        await conn.close()
        return {"status": False, "message": f"Error occurred: {str(e)}"}

def get_airport_code(airport_data: Dict[str, Any]) -> Tuple[bool, str, str]:
    """
    Extract airport code and full name from airport data
    Returns: (success, code, full_name)
    """
    if not airport_data:
        return False, "", ""

    code = airport_data.get("iata_code", "")
    full_name = f"{airport_data.get('airport_name', '')} ({airport_data.get('city', '')})"
    return True, code, full_name

def format_airport_search_response(city: str, airport_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the response for airport code search
    """
    success, code, full_name = get_airport_code(airport_data)

    if success:
        response_text = f"Airport code for {city} is {code} ({full_name})"
    else:
        response_text = f"Cannot find airport code for {city}"

    return {
        "fulfillmentText": response_text,
        "fulfillmentMessages": [{
            "text": {
                "text": [response_text]
            }
        }]
        
    }
