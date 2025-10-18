import ifcopenshell

class Clash_Result():

    id:str

    Source:list[ifcopenshell.entity_instance]=[]
    Target:list[ifcopenshell.entity_instance]=[]

    Status:str=None
    Criticity:str=None
    Actor:str=None