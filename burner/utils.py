def filter_alnum(input: str) -> str:
    return "".join([c if c.isalnum() else " " if c == "-" else "" for c in input])
