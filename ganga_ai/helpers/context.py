from typing import NamedTuple

"""
A chunk is one of the following
1. input + output pairs
2. assist + llm response
3. An error + llm response
"""
class ContextWindow(NamedTuple):
    size: int
    start: int
    end: int

def get_context_size(content: str) -> int:
    return len(content)
