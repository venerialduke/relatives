from models.entities.entities import Structure

class Collector(Structure):
    def __init__(self, id: str, location_space_id: str):
        super().__init__(id=id, name="Collector", location_space_id=location_space_id)

class Factory(Structure):
    def __init__(self, id: str, location_space_id: str):
        super().__init__(id=id, name="Factory", location_space_id=location_space_id)

class Settlement(Structure):
    def __init__(self, id: str, location_space_id: str):
        super().__init__(id=id, name="Settlement", location_space_id=location_space_id)

class FuelPump(Structure):
    def __init__(self, id: str, location_space_id: str):
        super().__init__(id=id, name="Fuel Pump", location_space_id=location_space_id)

class Scanner(Structure):
    def __init__(self, id: str, location_space_id: str):
        super().__init__(id=id, name="Scanner", location_space_id=location_space_id)


STRUCTURE_CLS_MAP = {
    "Collector": Collector,
    "Factory": Factory,
    "Settlement": Settlement,
    "FuelPump": FuelPump,
    "Scanner": Scanner
}

def get_structure_class_by_type(type_name: str):
    return STRUCTURE_CLS_MAP.get(type_name)