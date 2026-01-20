import ifcopenshell


ifcfile = ifcopenshell.open("/home/jocelin/Documents/05 - Programmation/IfcClash_Plus/Ifc_Model/Ifc2x3_Duplex_Architecture.ifc")


ifcwall = ifcfile.by_type("IfcWall")


if ifcwall[0] in ifcwall:
    print("Dans la liste")


