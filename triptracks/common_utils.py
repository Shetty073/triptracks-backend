
def is_none_or_empty(val: str):
    return bool(val and val.strip()) if isinstance(val, str) else True
