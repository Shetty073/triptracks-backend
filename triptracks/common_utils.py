
def is_none_or_empty(val):
    if val is None:
        return True
    if isinstance(val, str):
        return not bool(val.strip())
    return False
