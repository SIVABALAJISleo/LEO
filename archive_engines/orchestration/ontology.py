import uuid
import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class Property:
    property_name: str
    data_type: str # int, float, string, datetime
    unit: Optional[str] = None
    domain_tag: str = "general"
    description: str = ""

@dataclass
class MetaSchema:
    object_id: uuid.UUID = field(default_factory=uuid.uuid4)
    object_type: str = "generic"
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)

class GlobalPropertyRegistry:
    """
    Module 2: GLOBAL PROPERTY REGISTRY
    Central dictionary of all properties with strict enforcement.
    """
    def __init__(self):
        self._properties: Dict[str, Property] = {}
        self._initialize_core_ontology()

    def _initialize_core_ontology(self):
        # Financial Domain
        self.register(Property("revenue", "float", unit="USD", domain_tag="finance"))
        self.register(Property("expense", "float", unit="USD", domain_tag="finance"))
        self.register(Property("conversion_rate", "float", unit="%", domain_tag="marketing"))
        
        # Environmental Domain
        self.register(Property("temperature", "float", unit="°C", domain_tag="iot"))
        self.register(Property("humidity", "float", unit="%", domain_tag="iot"))
        
        self.register(Property("user_id", "string", domain_tag="identity"))
        self.register(Property("timestamp", "datetime", domain_tag="core"))
        self.register(Property("event_type", "string", domain_tag="core"))

    def register(self, prop: Property):
        if prop.property_name in self._properties:
            existing = self._properties[prop.property_name]
            if existing.data_type != prop.data_type or existing.unit != prop.unit:
                raise ValueError(f"Ontology Violation: Property '{prop.property_name}' conflicts with existing definition.")
            return
        
        self._properties[prop.property_name] = prop

    def get(self, name: str) -> Optional[Property]:
        return self._properties.get(name)

    def list_properties(self, domain: Optional[str] = None) -> List[Property]:
        if domain:
            return [p for p in self._properties.values() if p.domain_tag == domain]
        return list(self._properties.values())

    def validate_data(self, property_name: str, value: Any):
        prop = self.get(property_name)
        if not prop:
            raise ValueError(f"Unknown Property: '{property_name}' is not in the Global Registry.")
        
        # Strict Type Check
        if prop.data_type == "int" and not isinstance(value, int):
            raise TypeError(f"Type Mismatch: '{property_name}' expects int, got {type(value)}")
        if prop.data_type == "float" and not isinstance(value, (int, float)):
            raise TypeError(f"Type Mismatch: '{property_name}' expects float, got {type(value)}")
        if prop.data_type == "string" and not isinstance(value, str):
            raise TypeError(f"Type Mismatch: '{property_name}' expects string, got {type(value)}")

global_registry = GlobalPropertyRegistry()
