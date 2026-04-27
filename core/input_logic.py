def parse_input(raw_text: str):
    """
    Simulates FSA-driven tokenization.
    """
    tokens = raw_text.split()
    return {"status": "SUCCESS", "tokens": tokens}
