def filter_alnum(input: str) -> str:
    return "".join([c for c in input if c.isalnum()])
