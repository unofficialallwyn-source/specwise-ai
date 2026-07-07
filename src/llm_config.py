# This file will contain the config for llm invocation

import json
import re

from langchain_openai import ChatOpenAI

def parse_llm_json_response(response) -> dict:
    """Extracts raw content from an LLM response and parses it into a dictionary."""
    # 1. Accept raw LLM response content (supports string, AIMessage, or standard BaseMessage)
    if isinstance(response, BaseMessage):
        raw_content = response.content
    else:
        raw_content = str(response)

    # Clean potential markdown code blocks (```json ... ```) commonly returned by LLMs
    cleaned_content = raw_content.strip()
    if cleaned_content.startswith("```json"):
        cleaned_content = cleaned_content.split("```json", 1)[1].split("```", 1)[0].strip()
    elif cleaned_content.startswith("```"):
        cleaned_content = cleaned_content.split("```", 1)[1].split("```", 1)[0].strip()

    # 2. Try to parse it as JSON
    try:
        parsed_dict = json.loads(cleaned_content)
        
        # 3. Return a Python dictionary if successful
        if isinstance(parsed_dict, dict):
            return parsed_dict
        else:
            print(f"Warning: JSON parsed successfully but returned {type(parsed_dict).__name__}, not a dictionary.")
            return {}
            
    except json.JSONDecodeError as error:
        # 5. Print a clear error message if JSON parsing fails
        print(f"❌ JSON Parsing Failed!")
        print(f"Error Details: {error}")
        print(f"Attempted to parse text:\n{raw_content}\n")
        
        # 4. Return an empty dictionary or useful fallback if parsing fails
        return {}

llm = ChatOpenAI(model="gpt-4o", api_key=userdata.get("OPENAI_API_KEY"))

COMMON_SYSTEM_INSTRUCTION = """
You are SpecWise AI, a Product Owner assistant.

Rules:
- Use only the provided input.
- Do not invent unrelated features.
- Return valid JSON only.
- Do not include markdown.
- Do not include explanations outside JSON.
- Keep output concise and business-readable.
"""

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

