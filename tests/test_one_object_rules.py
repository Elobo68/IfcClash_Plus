"""
Test suite for Rules classes in Rules.py
"""
import unittest
import ifcopenshell
import sys
sys.path.insert(0, './ifcclash_plus')
from Rules import Volume, Area, TopSurface, Intersection, Above, OBB_Above,Clearance,Collision,OBB_Below,Orientation
from RuleClass import SelectFacet,RuleFile,ClashResultOneObject,ClashResultTwoObjects
from ifctester import ids


class TestRules(unittest.TestCase):
    """
    Made with AI
    Test cases for Rules classes methods
    """

    def setUp(self):
        """Set up test fixtures"""
        self.ifc_path = "Ifc_Model/Ifc2x3_Duplex_Architecture.ifc"
        self.ifc_file = ifcopenshell.open(self.ifc_path)

    def test_volume_rule(self):
        """Test Volume rule"""

        OneRuleFile = RuleFile()
        OneRuleFile.list_ifc_path= [self.ifc_path]

        wall_facet = ids.Entity(name="IFCWALLSTANDARDCASE")
        select_facet = SelectFacet()
        select_facet.applicability = [wall_facet]

        volume_rule = Volume(select_facet, 16, 17)

        OneRuleFile.contains=[volume_rule]
        OneRuleFile.run()

        self.assertEqual(len(volume_rule.result), 2) 
        for result in volume_rule.result:
            self.assertIsInstance(result, ClashResultOneObject)

    def test_area_rule(self):
        """Test area rule"""

        OneRuleFile = RuleFile()
        OneRuleFile.list_ifc_path= [self.ifc_path]

        first_facet = ids.Entity(name="IFCWALLSTANDARDCASE")
        first_select = SelectFacet()
        first_select.applicability = [first_facet]


        area_rule = Area(first_select, 0, 1)

        OneRuleFile.contains=[area_rule]
        OneRuleFile.run()

        self.assertEqual(len(area_rule.result), 8) 
        for result in area_rule.result:
            self.assertIsInstance(result, ClashResultOneObject)

    def test_top_surface_rule(self):
        """Test TopSurface rule"""
        OneRuleFile = RuleFile()
        OneRuleFile.list_ifc_path= [self.ifc_path]

        first_facet = ids.Entity(name="IFCFURNISHINGELEMENT")
        first_select = SelectFacet()
        first_select.applicability = [first_facet]

        top_surface_rule = TopSurface(first_select, 1, 2)

        OneRuleFile.contains=[top_surface_rule]
        OneRuleFile.run()

        self.assertEqual(len(top_surface_rule.result), 4) 
        for result in top_surface_rule.result:
            self.assertIsInstance(result, ClashResultOneObject)

    def test_orientation_rule(self):
        """Test TopSurface rule"""
        OneRuleFile = RuleFile()
        OneRuleFile.list_ifc_path= [self.ifc_path]

        first_facet = ids.Entity(name="IFCWALLSTANDARDCASE")
        first_select = SelectFacet()
        first_select.applicability = [first_facet]


        up_orientation=(1.0,1.0,0.0)

        rule = Orientation(first_select, up_orientation,"narrow",'Parrallel')

        OneRuleFile.contains=[rule]
        OneRuleFile.run()

        self.assertEqual(len(rule.result), 56) 
        for result in rule.result:
            self.assertIsInstance(result, ClashResultOneObject)



if __name__ == '__main__':
    unittest.main()
