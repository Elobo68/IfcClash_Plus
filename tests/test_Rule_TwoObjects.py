"""
Test suite for Rules classes in Rules.py
"""
import unittest
import ifcopenshell
import sys
sys.path.insert(0, './ifcclash_plus')
from Rules import Volume, Area, TopSurface, Intersection, Above, OBB_Above,Clearance,Collision,OBB_Below
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

    def test_intersection_rule(self):
        """Test Intersection rule"""

        OneRuleFile = RuleFile()
        OneRuleFile.list_ifc_path= [self.ifc_path]



        first_facet = ids.Entity(name="IFCWALLSTANDARDCASE")
        first_select = SelectFacet()
        first_select.applicability = [first_facet]

        second_facet = ids.Entity(name="IFCFURNISHINGELEMENT")
        second_select = SelectFacet()
        second_select.applicability = [second_facet]



        intersection_rule = Intersection(first_select, second_select, 0.01) 

        OneRuleFile.contains=[intersection_rule]
        OneRuleFile.run()

 
        self.assertEqual(len(intersection_rule.result), 1)
        for result in intersection_rule.result:
            self.assertIsInstance(result, ClashResultTwoObjects)

    def test_collision_rule(self):
        """Test collision rule"""

        OneRuleFile = RuleFile()
        OneRuleFile.list_ifc_path= [self.ifc_path]
        first_facet = ids.Entity(name="IFCDOOR")
        first_select = SelectFacet()
        first_select.applicability = [first_facet]


        second_facet = ids.Entity(name="IFCSLAB")
        second_select = SelectFacet()
        second_select.applicability = [second_facet]


        rule = Collision(first_select, second_select, False) 

        OneRuleFile.contains=[rule]
        OneRuleFile.run()

        self.assertEqual(len(rule.result), 24)
        for result in rule.result:
            self.assertIsInstance(result, ClashResultTwoObjects)

    def test_clearance_rule(self):
        """Test Intersection rule"""

        OneRuleFile = RuleFile()
        OneRuleFile.list_ifc_path= [self.ifc_path]
        first_facet = ids.Entity(name="IFCWALLSTANDARDCASE")
        first_select = SelectFacet()
        first_select.applicability = [first_facet]


        second_facet = ids.Entity(name="IFCFURNISHINGELEMENT")
        second_select = SelectFacet()
        second_select.applicability = [second_facet]

        intersection_rule = Clearance(first_select, second_select, 0.5) 

        OneRuleFile.contains=[intersection_rule]
        OneRuleFile.run()

        for result in intersection_rule.result:
            self.assertIsInstance(result, ClashResultTwoObjects)

        self.assertEqual(len(intersection_rule.result), 152)

    def test_above_rule(self):
        """Test Above rule"""

        OneRuleFile = RuleFile()
        OneRuleFile.list_ifc_path= [self.ifc_path]

        first_facet = ids.Entity(name="IFCFURNISHINGELEMENT")
        first_select = SelectFacet()
        first_select.applicability = [first_facet]

        second_facet = ids.Entity(name="IFCSLAB")
        second_select = SelectFacet()
        second_select.applicability = [second_facet]


        above_rule = Above(source=first_select, target=second_select, tolerance=0.81, above_type="Above_MaxToMin")
        above_rule.run()

        OneRuleFile.contains=[above_rule]
        OneRuleFile.run()

        self.assertEqual(len(above_rule.result), 8)
        for result in above_rule.result:
            self.assertIsInstance(result, above_rule.ClashResultTwoObjects)

    def test_obb_above_rule(self):
        """Test OBB_Above rule"""

        OneRuleFile = RuleFile()
        OneRuleFile.list_ifc_path= [self.ifc_path]

        first_facet = ids.Entity(name="IFCFURNISHINGELEMENT")
        first_select = SelectFacet()
        first_select.applicability = [first_facet]

        second_facet = ids.Entity(name="IFCSLAB")
        second_select = SelectFacet()
        second_select.applicability = [second_facet]

        obb_above_rule = OBB_Above(first_select, second_select, 0.81)
        
        OneRuleFile.contains=[obb_above_rule]
        OneRuleFile.run()

        self.assertEqual(len(obb_above_rule.result), 8)
        for result in obb_above_rule.result:
            self.assertIsInstance(result, ClashResultTwoObjects)


    def test_obb_below_rule(self):
        """Test OBB_Below rule"""

        OneRuleFile = RuleFile()
        OneRuleFile.list_ifc_path= [self.ifc_path]

        first_facet = ids.Entity(name="IfcWindow")
        first_select = SelectFacet()
        first_select.applicability = [first_facet]

        second_facet = ids.Entity(name="IfcSLab")
        second_select = SelectFacet()
        second_select.applicability = [second_facet]

        obb_above_rule = OBB_Below(first_select, second_select, 0.1)
        
        OneRuleFile.contains=[obb_above_rule]
        OneRuleFile.run()

        self.assertEqual(len(obb_above_rule.result), 34)
        #There is a lot of layer of slab in the house
        for result in obb_above_rule.result:
            self.assertIsInstance(result, ClashResultTwoObjects)

    def test_obb_below_rule_2(self):
        """Test OBB_Below rule. It's the inverse of OBB Above, to cross check"""

        OneRuleFile = RuleFile()
        OneRuleFile.list_ifc_path= [self.ifc_path]

        first_facet = ids.Entity(name="IfcSLab")
        first_select = SelectFacet()
        first_select.applicability = [first_facet]

        second_facet = ids.Entity(name="IFCFURNISHINGELEMENT")
        second_select = SelectFacet()
        second_select.applicability = [second_facet]

        obb_above_rule = OBB_Below(first_select, second_select, 0.81)
        
        OneRuleFile.contains=[obb_above_rule]
        OneRuleFile.run()

        self.assertEqual(len(obb_above_rule.result), 8)
        #We should find the same number as the above test rule. 
        for result in obb_above_rule.result:
            self.assertIsInstance(result, ClashResultTwoObjects)

    def test_obb_above_rule_2(self):
        """Test OBB_above rule, it's the inverse of OBB_Below, to cross check"""

        OneRuleFile = RuleFile()
        OneRuleFile.list_ifc_path= [self.ifc_path]

        first_facet = ids.Entity(name="IfcSlab")
        first_select = SelectFacet()
        first_select.applicability = [first_facet]

        second_facet = ids.Entity(name="IfcWindow")
        second_select = SelectFacet()
        second_select.applicability = [second_facet]

        obb_above_rule = OBB_Above(first_select, second_select, 0.1)
        
        OneRuleFile.contains=[obb_above_rule]
        OneRuleFile.run()

        self.assertEqual(len(obb_above_rule.result), 34)
        #We should find the same number as the above test rule. 
        for result in obb_above_rule.result:
            self.assertIsInstance(result, ClashResultTwoObjects)


if __name__ == '__main__':
    unittest.main()
