# Hot-cache memory state
HOT_CACHE = {}

def get_state(key: str):
    return HOT_CACHE.get(key, "NULL")

def set_state(key: str, value: str):
    HOT_CACHE[key] = value
