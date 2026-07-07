# Utility methods used by LangGraph node functions

import json
import re
from typing import List, Dict, Any

def get_state_text(value: Any) -> str:
    """
    Converts different state value formats into plain text.

    This helps if raw_requirement is stored as:
    - a string
    - a LangChain message
    - a list of messages
    """

    if value is None:
        return ""

    if isinstance(value, str):
        return value

    if isinstance(value, list):
        text_parts = []

        for item in value:
            if hasattr(item, "content"):
                text_parts.append(str(item.content))
            else:
                text_parts.append(str(item))

        return "\n".join(text_parts)

    if hasattr(value, "content"):
        return str(value.content)

    return str(value)

def compact_json(data: Dict[str, Any]) -> str:
    """
    Converts Python dictionary to compact JSON string.
    This reduces unnecessary spaces in the prompt.
    """
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))

def safe_json_parse(raw_text: str) -> Dict[str, Any]:
    """
    Safely parses LLM response into a Python dictionary.
    If the LLM returns markdown or extra text, it tries to extract JSON.
    """

    if raw_text is None or raw_text.strip() == "":
        print("JSON parse warning: Empty response received.")
        return {}

    cleaned_text = raw_text.strip()

    # Remove common markdown code fences if the model accidentally returns them
    cleaned_text = cleaned_text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        pass

    # Try to extract the first JSON object from the response
    match = re.search(r"\{.*\}", cleaned_text, re.DOTALL)

    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    print("JSON parse warning: Could not parse response.")
    print("Raw response was:")
    print(raw_text)

    return {}

def normalize_list(value: Any) -> List[str]:
    """
    Ensures a value is always returned as a list of strings.
    """

    if value is None:
        return []

    if isinstance(value, list):
        return [str(item) for item in value]

    if isinstance(value, str):
        if value.strip() == "":
            return []
        return [value]

    return [str(value)]
