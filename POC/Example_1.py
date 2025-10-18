
import Select
import ifcopenshell.util.placement
import ifcopenshell.util.selector
import RuleClass


if __name__ == '__main__':
    path1="Ifc_Model/Ifc2s3_Duplex_Electrical.ifc"
    path2="Ifc_Model/Ifc2x3_Duplex_Architecture.ifc"
    path3 = "Ifc_Model/Ifc2x3_Duplex_MEP.ifc"

    file1=ifcopenshell.open(path1)
    file2=ifcopenshell.open(path2)
    file3=ifcopenshell.open(path3)

    Spaces=ifcopenshell.util.selector.filter_elements(file2,"IfcSpace")
    Beds = ifcopenshell.util.selector.filter_elements(file2, "IfcFurnishingElement,Name=/M_Bed/")
    Light = ifcopenshell.util.selector.filter_elements(file3, "IfcFlowTerminal,Name=/M_Lighting/")

    list_of_model=[path1,path2,path3]

    Select_Space = Select.Select_Facet()
    Select_Space.list_ifc_path=list_of_model
    Select_Space.elements=Spaces

    Select_Light = Select.Select_Facet()
    Select_Light.list_ifc_path=list_of_model
    Select_Light.elements = Light

    Select_Beds = Select.Select_Facet()
    Select_Beds.list_ifc_path = list_of_model
    Select_Beds.elements = Beds


    RuleContains=RuleClass.Intersection(source=Select_Space, target=Select_Beds)
    Select_Space_Contains_Bed = Select.Select_Rule()
    Select_Space_Contains_Bed.rule=RuleContains #This Selection is use to get all the rooms that contains beds.


    FinalRule=RuleClass.Clearance(source=Select_Space_Contains_Bed, target=Select_Light,clearance=0.05)
    #We can reuse this selection to an input of another clash that can detect all the flow terminal in Bedrooms.

    FinalRule.Run()


    for OneResult in FinalRule.results:
        print(OneResult.a,OneResult.b)



    """
    #1442=IfcSpace('0BTBFw6f90Nfh9rP1dlXrc',#33,'A202','',$,#1422,#1441,'Bedroom 1',.ELEMENT.,.INTERNAL.,$) #77098=IfcFlowTerminal('1BZbxAG8L6z9EEpSZfugOW',#33,'M_Lighting Switches:Single Pole:Single Pole:575392',$,'Single Pole',#77097,#77091,'575392')
    #2789=IfcSpace('0BTBFw6f90Nfh9rP1dl_39',#33,'B203','',$,#2768,#2788,'Bedroom 2',.ELEMENT.,.INTERNAL.,$) #77173=IfcFlowTerminal('1K7eM1Qof1dOc9$mY9I4C0',#33,'M_Lighting Switches:Single Pole:Single Pole:575394',$,'Single Pole',#77172,#77166,'575394')
    #1218=IfcSpace('0BTBFw6f90Nfh9rP1dlXrb',#33,'A203','',$,#1197,#1217,'Bedroom 2',.ELEMENT.,.INTERNAL.,$) #77313=IfcFlowTerminal('1K7eM1Qof1dOc9$mY9I4C8',#33,'M_Lighting Switches:Single Pole:Single Pole:575402',$,'Single Pole',#77312,#77306,'575402')
    #3013=IfcSpace('0BTBFw6f90Nfh9rP1dl_3A',#33,'B202','',$,#2993,#3012,'Bedroom 1',.ELEMENT.,.INTERNAL.,$) #77278=IfcFlowTerminal('1K7eM1Qof1dOc9$mY9I4CA',#33,'M_Lighting Switches:Single Pole:Single Pole:575400',$,'Single Pole',#77277,#77271,'575400')

    """