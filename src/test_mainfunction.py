import RuleClass
from RuleClass import SelectFacet,SelectRule
from Rules import Volume, Area, TopSurface,Intersection
from ifctester import ids
from ifcopenshell import file
import ifcopenshell


def Test_Folder():
    OneRuleFile = RuleClass.RuleFile()

    OneFolder1 = RuleClass.RuleFolder()
    OneFolder1_1 = RuleClass.RuleFolder()
    OneFolder1_2 = RuleClass.RuleFolder()

    OneFolder1_1.contains = ["Rule A", "Rule B"]
    OneFolder1_2.contains = ["Rule 1", "Rule 2"]

    OneFolder1.contains = [OneFolder1_1, OneFolder1_2]
    OneRuleFile.contains = [OneFolder1]

    OneRuleFile.run()


def Volume_Check():
    Chemin = "Ifc_Model/Ifc2x3_Duplex_Architecture.ifc"
    OneSelect_Facet = SelectFacet()
    Wall_Facet = ids.Entity(name="IFCWALLSTANDARDCASE")
    OneSelect_Facet.applicability = [Wall_Facet]
    OneSelect_Facet.list_ifc_path = [Chemin]

    rulevolume = Volume(OneSelect_Facet, 1, 2)
    rulevolume.run()

    print("Sucess", rulevolume.sucess)
    print("Fail", rulevolume.fail)


def Exception_Check():
    Chemin = "Ifc_Model/Ifc2x3_Duplex_Architecture.ifc"
    OneSelect_Facet = SelectFacet()
    Wall_Facet = ids.Entity(name="IFCWALLSTANDARDCASE")
    OneSelect_Facet.applicability = [Wall_Facet]
    OneSelect_Facet.list_ifc_path = [Chemin]

    rulevolume = Volume(OneSelect_Facet, 1, 2)
    ruleArea = Volume(OneSelect_Facet, 0, 2)

    rulevolume.select_exception = [ruleArea]
    rulevolume.run()


def Grouping_Test():
    Chemin = "Ifc_Model/Ifc2x3_Duplex_Architecture.ifc"
    OneSelect_Facet = SelectFacet()
    Wall_Facet = ids.Entity(name="IFCWALLSTANDARDCASE")
    OneSelect_Facet.applicability = [Wall_Facet]
    OneSelect_Facet.list_ifc_path = [Chemin]

    rulevolume = Volume(OneSelect_Facet, 1, 2)
    rulevolume.grouping = "ENTITY"

    rulevolume.run()
    for x in rulevolume.result:
        print(x.source_group, x.source)

def Actor_And_Criticity_Test():
    Chemin = "Ifc_Model/Ifc2x3_Duplex_Architecture.ifc"

    WallStandardCase_Facet = ids.Entity(name="IFCWALLSTANDARDCASE")
    Wall_Facet = ids.Entity(name="IFCWALL")

    OneSelect_Facet = SelectFacet()
    OneSelect_Facet.applicability = [WallStandardCase_Facet]
    OneSelect_Facet.list_ifc_path = [Chemin]

    select_actor = SelectFacet()
    select_actor.classification_name = "Jean"
    select_actor.applicability = [WallStandardCase_Facet]

    select_criticity = SelectFacet()
    select_criticity.classification_name = "High"
    select_criticity.applicability = [WallStandardCase_Facet]

    rulevolume = Volume(OneSelect_Facet, 1, 2)
    rulevolume.grouping = "ENTITY"
    rulevolume.select_actor = select_actor
    rulevolume.select_criticity = select_criticity

    rulevolume.run()
    for x in rulevolume.result:
        print(x.source_group, x.status, x.actor, x.criticity, x.source)

def Top_Surface():
    Chemin = "Ifc_Model/Ifc2x3_Duplex_Architecture.ifc"

    WallStandardCase_Facet = ids.Entity(name="IFCWALLSTANDARDCASE")
    Wall_Facet = ids.Entity(name="IFCWALL")

    OneSelect_Facet = SelectFacet()
    OneSelect_Facet.applicability = [WallStandardCase_Facet]
    OneSelect_Facet.list_ifc_path = [Chemin]

    rulevolume = TopSurface(OneSelect_Facet, 1, 2)

    rulevolume.run()

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

    rulevolume = Intersection(Window_Select, Wall_Select,0.01)

    exception_rule = Intersection(None,None,0.1)
    select_rule=SelectRule()
    select_rule.rule=exception_rule


    rulevolume.select_exception=[select_rule]
    rulevolume.run()

def ExceptionMakinProcess():
    from RuleClass import Select
    Chemin = "Ifc_Model/Ifc2x3_Duplex_Architecture.ifc"
    ifc_file=ifcopenshell.open(Chemin)

    ifc_window=ifc_file.by_guid("1hOSvn6df7F8_7GcBWlS_W")
    ifc_wall=ifc_file.by_guid("2O2Fr$t4X7Zf8NOew3FLOH")



    exception_rule = Intersection(None,None,0.01)

    exception_rule.select_source=Select()
    exception_rule.select_source.dict_elements={ifc_wall.file:[ifc_wall]}
    exception_rule.select_source.list_ifc_file=[ifc_wall.file]
    exception_rule.select_target=Select()
    exception_rule.select_target.dict_elements={ifc_window.file:[ifc_window]}
    exception_rule.select_target.list_ifc_file=[ifc_window.file]

    Resultat=exception_rule.run()

    for key,value in exception_rule.__dict__.items():
        print(key,value)

    print("Les Resulstas")
    print(exception_rule.result[0].__dict__)




def OneElement():
    Chemin = "Ifc_Model/Ifc2x3_Duplex_Architecture.ifc"
    import ifcopenshell
    ifc_file=ifcopenshell.open(Chemin)

    ifc_wall=ifc_file.by_type("IFCWALL")



if __name__ == "__main__":
    IntersectionCheck()
