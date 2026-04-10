import RuleClass
from RuleClass import SelectFacet, SelectRule
from Rules import Volume, Area, TopSurface, Intersection, Clearance,Above
from ifctester import ids
from ifcopenshell import file
import ifcopenshell


def IntersectionCheck():
    Chemin = "Ifc_Model/Ifc2x3_Duplex_Architecture.ifc"

    OneRuleFile = RuleClass.RuleFile()
    OneRuleFile.list_ifc_path= [Chemin]


    Wall_Select = SelectFacet()
    Wall_Facet = ids.Entity(name="IFCWALLSTANDARDCASE")
    Wall_Select.applicability = [Wall_Facet]


    Window_Select = SelectFacet()
    Window_Facet = ids.Entity(name="IFCWINDOW")
    Window_Select.applicability = [Window_Facet]


    intersect_rule = Intersection(Window_Select, Wall_Select, 0.001)

    OneRuleFile.contains=[intersect_rule]

    OneRuleFile.run()

    for result in intersect_rule.result:
        if result.status:
            print("Clash", result.source.Name, result.target.Name)
        else:
            print("No Clash", result.source.Name, result.target.Name)

    """
    Clash M_Fixed:750mm x 2200mm:750mm x 2200mm:146885 Basic Wall:Exterior - Brick on Block:138157
Clash M_Fixed:819mm x 759mm:819mm x 759mm:180864 Basic Wall:Exterior - Brick on Block:143590
Clash M_Fixed:819mm x 759mm:819mm x 759mm:181583 Basic Wall:Exterior - Brick on Block:143478
Clash M_Fixed:819mm x 759mm:819mm x 759mm:180663 Basic Wall:Exterior - Brick on Block:143590
Clash M_Fixed:750mm x 2200mm:750mm x 2200mm:147051 Basic Wall:Exterior - Brick on Block:138310
Clash M_Fixed:4835mm x 2420mm:4835mm x 2420mm:146016 Basic Wall:Exterior - Brick on Block:138237
Clash M_Fixed:819mm x 759mm:819mm x 759mm:148722 Basic Wall:Exterior - Brick on Block:143410
Clash M_Fixed:819mm x 759mm:819mm x 759mm:147994 Basic Wall:Exterior - Brick on Block:143410
Clash M_Fixed:2800mm x 2410mm:2800mm x 2410mm:147686 Basic Wall:Exterior - Brick on Block:143410
Clash M_Fixed:750mm x 2200mm:750mm x 2200mm:182101 Basic Wall:Exterior - Brick on Block:143590
Clash M_Fixed:750mm x 2200mm:750mm x 2200mm:181930 Basic Wall:Exterior - Brick on Block:143478
Clash M_Fixed:2800mm x 2410mm:2800mm x 2410mm:149278 foo
Clash M_Fixed:819mm x 759mm:819mm x 759mm:149537 foo
Clash M_Fixed:819mm x 759mm:819mm x 759mm:149924 foo
    """

def Rule_Select():
    path_arc = "Ifc_Model/Ifc2x3_Duplex_Architecture.ifc"

    OneRuleFile = RuleClass.RuleFile()
    OneRuleFile.list_ifc_path= [path_arc]

    Wall_Select = SelectFacet()
    Wall_Facet = ids.Entity(name="IFCWALLSTANDARDCASE")
    Wall_Select.applicability = [Wall_Facet]

    door_select = SelectFacet()
    door_facet = ids.Entity(name="IFCDOOR")
    door_select.applicability = [door_facet]

    furnishing_select = SelectFacet()
    furnishing_facet = ids.Entity(name="IFCFURNISHINGELEMENT")
    furnishing_select.applicability = [furnishing_facet]

    wall_vs_door = Intersection(source=Wall_Select, target=door_select, tolerance=0.001)
    rule_select = SelectRule()
    rule_select.rule = wall_vs_door
    # I select all the wall that intersect a door. This list will be use in the next rule, as an entry.

    the_check = Clearance(source=rule_select, target=furnishing_select, clearance=1.2)
    # I check that the wall that collide door, are colliding furnishing.

    OneRuleFile.contains=[the_check]

    OneRuleFile.run() #We start the rule

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



    """
    Intermediate Clash  source: Basic Wall:Interior - Partition (92mm Stud):143921 target: M_Single-Flush:0762 x 2032mm:0762 x 2032mm:203720
Intermediate Clash  source: Basic Wall:Interior - Partition (92mm Stud):143921 target: M_Single-Flush:0864 x 2032mm:0864 x 2032mm:150378
Intermediate Clash  source: Basic Wall:Interior - Partition (92mm Stud):144586 target: M_Single-Flush:0864 x 2032mm:0864 x 2032mm:150478
Intermediate Clash  source: Basic Wall:Interior - Partition (92mm Stud):144586 target: M_Single-Flush:0864 x 2032mm:0864 x 2032mm:159834
Intermediate Clash  source: Basic Wall:Interior - Partition (92mm Stud):144586 target: M_Single-Flush:0762 x 2032mm:0762 x 2032mm:204034
Intermediate Clash  source: Basic Wall:Interior - Partition (92mm Stud):139939 target: M_Single-Glass 1:0813 x 2420mm:0813 x 2420mm:171975
Intermediate Clash  source: Basic Wall:Interior - Partition (92mm Stud):138584 target: M_Single-Glass 1:0813 x 2420mm:0813 x 2420mm:171853
Clashing wall Basic Wall:Interior - Partition (92mm Stud):143921 M_Tall Cabinet-Single Door(2):800 mm:800 mm:157200
Clashing wall Basic Wall:Interior - Partition (92mm Stud):143921 M_Tall Cabinet-Single Door(2):800 mm:800 mm:158081
Clashing wall Basic Wall:Interior - Partition (92mm Stud):144586 M_Tall Cabinet-Single Door(2):800 mm:800 mm:157983
Clashing wall Basic Wall:Interior - Partition (92mm Stud):144586 M_Tall Cabinet-Single Door(2):800 mm:800 mm:157951
    
    
    """

def AboveConstruct():
    Chemin = "Ifc_Model/Ifc2x3_Duplex_Architecture.ifc"

    OneRuleFile = RuleClass.RuleFile()
    OneRuleFile.list_ifc_path= [Chemin]


    Source_Select = SelectFacet()
    Source_Facet = ids.Entity(name="IFCWALLSTANDARDCASE")
    Source_Select.applicability = [Source_Facet]


    Target_Select = SelectFacet()
    Target_Facet = ids.Entity(name="IFCWINDOW")
    Target_Select.applicability = [Target_Facet]


    rule = Above(source=Source_Select, target=Target_Select,tolerance=1,above_type="Above_MaxToMax")

    OneRuleFile.contains=[rule]

    OneRuleFile.run()

    for result in rule.result:
        print(result.source,result.target)

    """
#4043=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FNr2',#33,'Basic Wall:Exterior - Brick on Block:138237',$,'Basic Wall:Exterior - Brick on Block:130892',#4030,#4042,'138237') #7847=IfcWindow('1hOSvn6df7F8_7GcBWlS2V',#33,'M_Fixed:819mm x 759mm:819mm x 759mm:149537',$,'819mm x 759mm',#7846,#7841,'149537',0.758999999999998,0.819)
#4043=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FNr2',#33,'Basic Wall:Exterior - Brick on Block:138237',$,'Basic Wall:Exterior - Brick on Block:130892',#4030,#4042,'138237') #7847=IfcWindow('1hOSvn6df7F8_7GcBWlS2V',#33,'M_Fixed:819mm x 759mm:819mm x 759mm:149537',$,'819mm x 759mm',#7846,#7841,'149537',0.758999999999998,0.819)
#3999=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FNqI',#33,'Basic Wall:Exterior - Brick on Block:138157',$,'Basic Wall:Exterior - Brick on Block:130892',#3986,#3998,'138157') #7847=IfcWindow('1hOSvn6df7F8_7GcBWlS2V',#33,'M_Fixed:819mm x 759mm:819mm x 759mm:149537',$,'819mm x 759mm',#7846,#7841,'149537',0.758999999999998,0.819)
#3999=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FNqI',#33,'Basic Wall:Exterior - Brick on Block:138157',$,'Basic Wall:Exterior - Brick on Block:130892',#3986,#3998,'138157') #7847=IfcWindow('1hOSvn6df7F8_7GcBWlS2V',#33,'M_Fixed:819mm x 759mm:819mm x 759mm:149537',$,'819mm x 759mm',#7846,#7841,'149537',0.758999999999998,0.819)
#3999=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FNqI',#33,'Basic Wall:Exterior - Brick on Block:138157',$,'Basic Wall:Exterior - Brick on Block:130892',#3986,#3998,'138157') #22344=IfcWindow('1l0GAJtRTFv8$zmKJOH4hv',#33,'M_Fixed:819mm x 759mm:819mm x 759mm:181583',$,'819mm x 759mm',#22343,#22338,'181583',0.758999999999999,0.819)
#3999=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FNqI',#33,'Basic Wall:Exterior - Brick on Block:138157',$,'Basic Wall:Exterior - Brick on Block:130892',#3986,#3998,'138157') #22344=IfcWindow('1l0GAJtRTFv8$zmKJOH4hv',#33,'M_Fixed:819mm x 759mm:819mm x 759mm:181583',$,'819mm x 759mm',#22343,#22338,'181583',0.758999999999999,0.819)
#3797=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FNtn',#33,'Basic Wall:Exterior - Brick on Block:138062',$,'Basic Wall:Exterior - Brick on Block:130892',#3781,#3796,'138062') #7407=IfcWindow('1hOSvn6df7F8_7GcBWlSga',#33,'M_Fixed:819mm x 759mm:819mm x 759mm:147994',$,'819mm x 759mm',#7406,#7401,'147994',0.758999999999998,0.819)
#3797=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FNtn',#33,'Basic Wall:Exterior - Brick on Block:138062',$,'Basic Wall:Exterior - Brick on Block:130892',#3781,#3796,'138062') #7407=IfcWindow('1hOSvn6df7F8_7GcBWlSga',#33,'M_Fixed:819mm x 759mm:819mm x 759mm:147994',$,'819mm x 759mm',#7406,#7401,'147994',0.758999999999998,0.819)
#4087=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FNhv',#33,'Basic Wall:Exterior - Brick on Block:138310',$,'Basic Wall:Exterior - Brick on Block:130892',#4074,#4086,'138310') #7407=IfcWindow('1hOSvn6df7F8_7GcBWlSga',#33,'M_Fixed:819mm x 759mm:819mm x 759mm:147994',$,'819mm x 759mm',#7406,#7401,'147994',0.758999999999998,0.819)
#4087=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FNhv',#33,'Basic Wall:Exterior - Brick on Block:138310',$,'Basic Wall:Exterior - Brick on Block:130892',#4074,#4086,'138310') #7407=IfcWindow('1hOSvn6df7F8_7GcBWlSga',#33,'M_Fixed:819mm x 759mm:819mm x 759mm:147994',$,'819mm x 759mm',#7406,#7401,'147994',0.758999999999998,0.819)
#4087=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FNhv',#33,'Basic Wall:Exterior - Brick on Block:138310',$,'Basic Wall:Exterior - Brick on Block:130892',#4074,#4086,'138310') #22084=IfcWindow('1l0GAJtRTFv8$zmKJOH4qs',#33,'M_Fixed:819mm x 759mm:819mm x 759mm:180864',$,'819mm x 759mm',#22083,#22078,'180864',0.758999999999999,0.819)
#4087=IfcWallStandardCase('2O2Fr$t4X7Zf8NOew3FNhv',#33,'Basic Wall:Exterior - Brick on Block:138310',$,'Basic Wall:Exterior - Brick on Block:130892',#4074,#4086,'138310') #22084=IfcWindow('1l0GAJtRTFv8$zmKJOH4qs',#33,'M_Fixed:819mm x 759mm:819mm x 759mm:180864',$,'819mm x 759mm',#22083,#22078,'180864',0.758999999999999,0.819)
    
    """


    


if __name__ == "__main__":
    AboveConstruct()
    #IntersectionCheck()
    #Rule_Select()
    #
    #TODO Expand the examples

