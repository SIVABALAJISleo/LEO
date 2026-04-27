# Static knowledge maps
DOMAIN_MAP = {
    "NVIDIA": "TECH_ENTITY",
    "HYPER": "CORE_SYSTEM"
}

def resolve_entity(name: str):
    return DOMAIN_MAP.get(name, "UNKNOWN")
