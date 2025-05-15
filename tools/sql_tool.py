from typing import Union
import json

def generate_sql_query(parsed_info: dict) -> str:
    """
    Generate SQL query based on parsed document details.

    Args:
        parsed_info (dict): Fields like developer name, property ID, etc.

    Returns:
        str: SQL SELECT query.
    """
    developer = parsed_info.get("developer_name", "UNKNOWN")
    project = parsed_info.get("project_name", "")

    query = f"""
    SELECT *
    FROM transactions
    WHERE developer_name = '{developer}'
      AND project_name = '{project}';
    """.strip()
    return query


def sql_query_tool(input: Union[str, dict]) -> str:
    """
    Entry point for AutoGen to call.

    Args:
        input (str | dict): JSON string or dictionary with parsed info.

    Returns:
        str: Generated SQL query.
    """
    if isinstance(input, str):
        parsed_info = json.loads(input)
    else:
        parsed_info = input

    query = generate_sql_query(parsed_info)
    return f"Generated SQL:\n{query}"
