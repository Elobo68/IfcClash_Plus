import RuleClass
from RuleClass import SelectFacet, SelectRule
from Rules import Volume, Area, TopSurface, Intersection, Clearance
from ifctester import ids
from ifcopenshell import file
import ifcopenshell


def IntersectionCheck():
    Chemin = "Ifc_Model/Ifc2x3_Duplex_Architecture.ifc"
    Wall_Select = SelectFacet()
    Wall_Facet = ids.Entity(name="IFCWALLSTANDARDCASE")
    Wall_Select.applicability = [Wall_Facet]
    Wall_Select.list_ifc_path = [Chemin]

    Window_Select = SelectFacet()
    Window_Facet = ids.Entity(name="IFCWINDOW")
    Window_Select.applicability = [Window_Facet]
    Window_Select.list_ifc_path = [Chemin]

    intersect_rule = Intersection(Window_Select, Wall_Select, 0.001)

    intersect_rule.run()

    for result in intersect_rule.result:
        if result.status:
            print("Clash", result.source.Name, result.target.Name)
        else:
            print("No Clash", result.source.Name, result.target.Name)


def Rule_Select():
    path_arc = "Ifc_Model/Ifc2x3_Duplex_Architecture.ifc"

    Wall_Select = SelectFacet()
    Wall_Facet = ids.Entity(name="IFCWALLSTANDARDCASE")
    Wall_Select.applicability = [Wall_Facet]
    Wall_Select.list_ifc_path = [path_arc]

    door_select = SelectFacet()
    door_facet = ids.Entity(name="IFCDOOR")
    door_select.applicability = [door_facet]
    door_select.list_ifc_path = [path_arc]

    furnishing_select = SelectFacet()
    furnishing_facet = ids.Entity(name="IFCFURNISHINGELEMENT")
    furnishing_select.applicability = [furnishing_facet]
    furnishing_select.list_ifc_path = [path_arc]

    wall_vs_door = Intersection(source=Wall_Select, target=door_select, tolerance=0.001)
    rule_select = SelectRule()
    rule_select.rule = wall_vs_door
    # I select all the wall that intersect a door. This list will be use in the next rule, as an entry.

    the_check = Clearance(source=rule_select, target=furnishing_select, clearance=1.2)
    # I check that the wall that collide door, are colliding furnishing.

    the_check.run()

    for intermediate_result in the_check.select_source.rule.result:
        print(
            "Intermediate Clash ",
            "source:",
            intermediate_result.source.Name,
            "target:",
            intermediate_result.target.Name,
        )

    for result in the_check.result:
        if result.status:
            print("Clashing wall", result.source.Name, result.target.Name)
        else:
            print("No Clash", result.source.Name, result.target.Name)


if __name__ == "__main__":
    results = Rule_Select()
