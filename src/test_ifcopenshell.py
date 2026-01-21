import ifcopenshell
import ifcopenshell.util.element as attt

chemin="Ifc_Model/Ifc2s3_Duplex_Electrical.ifc"
file=ifcopenshell.open(chemin)

spaces=file.by_type("IFCSPACE")
space=spaces[0]

property="Other.RoomTag"

result=attt.get_property([space],name=property)
result=attt.get_pset(space,name="Other",prop="RoomTag")
result=space.get_info()

print(result)