import RuleClass
from RuleClass import SelectFacet, SelectRule
from Rules import Volume, Area, TopSurface, Intersection, Clearance,Above
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

def AboveConstruct():
    Chemin = "Ifc_Model/Ifc2x3_Duplex_Architecture.ifc"
    Source_Select = SelectFacet()
    Source_Facet = ids.Entity(name="IFCWALLSTANDARDCASE")
    Source_Select.applicability = [Source_Facet]
    Source_Select.list_ifc_path = [Chemin]

    Target_Select = SelectFacet()
    Target_Facet = ids.Entity(name="IFCWINDOW")
    Target_Select.applicability = [Target_Facet]
    Target_Select.list_ifc_path = [Chemin]

    rule = Above(source=Source_Select, target=Target_Select,tolerance=1,above_type="Above_MaxToMax")

    """
#3797=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FNtn',#33,'Basic Wall:Exterior - Brick on Block:138062',$,'Basic Wall:Exterior - Brick on Block:130892',#3781,#3796,'138062') #7407=IfcWindow('1hOSvn6df7F8_7GcBWlSga',#33,'M_Fixed:819mm x 759mm:819mm x 759mm:147994',$,'819mm x 759mm',#7406,#7401,'147994',0.758999999999998,0.819)
#3797=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FNtn',#33,'Basic Wall:Exterior - Brick on Block:138062',$,'Basic Wall:Exterior - Brick on Block:130892',#3781,#3796,'138062') #7407=IfcWindow('1hOSvn6df7F8_7GcBWlSga',#33,'M_Fixed:819mm x 759mm:819mm x 759mm:147994',$,'819mm x 759mm',#7406,#7401,'147994',0.758999999999998,0.819)
#4043=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FNr2',#33,'Basic Wall:Exterior - Brick on Block:138237',$,'Basic Wall:Exterior - Brick on Block:130892',#4030,#4042,'138237') #7847=IfcWindow('1hOSvn6df7F8_7GcBWlS2V',#33,'M_Fixed:819mm x 759mm:819mm x 759mm:149537',$,'819mm x 759mm',#7846,#7841,'149537',0.758999999999998,0.819)
#4043=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FNr2',#33,'Basic Wall:Exterior - Brick on Block:138237',$,'Basic Wall:Exterior - Brick on Block:130892',#4030,#4042,'138237') #7847=IfcWindow('1hOSvn6df7F8_7GcBWlS2V',#33,'M_Fixed:819mm x 759mm:819mm x 759mm:149537',$,'819mm x 759mm',#7846,#7841,'149537',0.758999999999998,0.819)
#3999=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FNqI',#33,'Basic Wall:Exterior - Brick on Block:138157',$,'Basic Wall:Exterior - Brick on Block:130892',#3986,#3998,'138157') #7847=IfcWindow('1hOSvn6df7F8_7GcBWlS2V',#33,'M_Fixed:819mm x 759mm:819mm x 759mm:149537',$,'819mm x 759mm',#7846,#7841,'149537',0.758999999999998,0.819)
#3999=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FNqI',#33,'Basic Wall:Exterior - Brick on Block:138157',$,'Basic Wall:Exterior - Brick on Block:130892',#3986,#3998,'138157') #7847=IfcWindow('1hOSvn6df7F8_7GcBWlS2V',#33,'M_Fixed:819mm x 759mm:819mm x 759mm:149537',$,'819mm x 759mm',#7846,#7841,'149537',0.758999999999998,0.819)
#3999=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FNqI',#33,'Basic Wall:Exterior - Brick on Block:138157',$,'Basic Wall:Exterior - Brick on Block:130892',#3986,#3998,'138157') #22344=IfcWindow('1l0GAJtRTFv8$zmKJOH4hv',#33,'M_Fixed:819mm x 759mm:819mm x 759mm:181583',$,'819mm x 759mm',#22343,#22338,'181583',0.758999999999999,0.819)
#3999=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FNqI',#33,'Basic Wall:Exterior - Brick on Block:138157',$,'Basic Wall:Exterior - Brick on Block:130892',#3986,#3998,'138157') #22344=IfcWindow('1l0GAJtRTFv8$zmKJOH4hv',#33,'M_Fixed:819mm x 759mm:819mm x 759mm:181583',$,'819mm x 759mm',#22343,#22338,'181583',0.758999999999999,0.819)
#4087=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FNhv',#33,'Basic Wall:Exterior - Brick on Block:138310',$,'Basic Wall:Exterior - Brick on Block:130892',#4074,#4086,'138310') #7407=IfcWindow('1hOSvn6df7F8_7GcBWlSga',#33,'M_Fixed:819mm x 759mm:819mm x 759mm:147994',$,'819mm x 759mm',#7406,#7401,'147994',0.758999999999998,0.819)
#4087=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FNhv',#33,'Basic Wall:Exterior - Brick on Block:138310',$,'Basic Wall:Exterior - Brick on Block:130892',#4074,#4086,'138310') #7407=IfcWindow('1hOSvn6df7F8_7GcBWlSga',#33,'M_Fixed:819mm x 759mm:819mm x 759mm:147994',$,'819mm x 759mm',#7406,#7401,'147994',0.758999999999998,0.819)
#4087=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FNhv',#33,'Basic Wall:Exterior - Brick on Block:138310',$,'Basic Wall:Exterior - Brick on Block:130892',#4074,#4086,'138310') #22084=IfcWindow('1l0GAJtRTFv8$zmKJOH4qs',#33,'M_Fixed:819mm x 759mm:819mm x 759mm:180864',$,'819mm x 759mm',#22083,#22078,'180864',0.758999999999999,0.819)
#4087=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FNhv',#33,'Basic Wall:Exterior - Brick on Block:138310',$,'Basic Wall:Exterior - Brick on Block:130892',#4074,#4086,'138310') #22084=IfcWindow('1l0GAJtRTFv8$zmKJOH4qs',#33,'M_Fixed:819mm x 759mm:819mm x 759mm:180864',$,'819mm x 759mm',#22083,#22078,'180864',0.758999999999999,0.819)
    
    """


    rule.run()


if __name__ == "__main__":
    results = Rule_Select()
    #TODO Expand the examples

