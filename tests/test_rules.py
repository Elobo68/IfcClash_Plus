"""
Test suite for Rules classes in Rules.py
"""
import unittest
import ifcopenshell
import sys
sys.path.insert(0, './ifcclash_plus')
from Rules import Volume, Area, TopSurface, Intersection, Above, OBB_Above
from RuleClass import SelectFacet,RuleFile,ClashResultOneObject,ClashResultTwoObjects,Collision,Clearance
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

        wall_facet = ids.Entity(name="IFCWALLSTANDARDCASE")
        select_facet = SelectFacet()
        select_facet.applicability = [wall_facet]

        area_rule = Area(select_facet, 0, 1)

        OneRuleFile.contains=[area_rule]
        OneRuleFile.run()

        self.assertEqual(len(area_rule.result), 8) 
        for result in area_rule.result:
            self.assertIsInstance(result, ClashResultOneObject)

    def test_top_surface_rule(self):
        """Test TopSurface rule"""
        OneRuleFile = RuleFile()
        OneRuleFile.list_ifc_path= [self.ifc_path]

        wall_facet = ids.Entity(name="IFCFURNISHINGELEMENT")
        select_facet = SelectFacet()
        select_facet.applicability = [wall_facet]

        top_surface_rule = TopSurface(select_facet, 1, 2)

        OneRuleFile.contains=[top_surface_rule]
        OneRuleFile.run()

        self.assertEqual(len(top_surface_rule.result), 4) 
        for result in top_surface_rule.result:
            self.assertIsInstance(result, ClashResultOneObject)

    def test_intersection_rule(self):
        """Test Intersection rule"""

        OneRuleFile = RuleFile()
        OneRuleFile.list_ifc_path= [self.ifc_path]
        wall_facet = ids.Entity(name="IFCWALLSTANDARDCASE")
        wall_select = SelectFacet()
        wall_select.applicability = [wall_facet]
        wall_select.list_ifc_path = [self.ifc_path]

        window_facet = ids.Entity(name="IFCFURNISHINGELEMENT")
        window_select = SelectFacet()
        window_select.applicability = [window_facet]
        window_select.list_ifc_path = [self.ifc_path]

        intersection_rule = Intersection(window_select, wall_select, 0.01) 

        OneRuleFile.contains=[intersection_rule]
        OneRuleFile.run()

 
        self.assertEqual(len(intersection_rule.result), 1)
        for result in intersection_rule.result:
            self.assertIsInstance(result, ClashResultTwoObjects)

    def test_collision_rule(self):
        """Test Intersection rule"""

        OneRuleFile = RuleFile()
        OneRuleFile.list_ifc_path= [self.ifc_path]
        wall_facet = ids.Entity(name="IFCWALLSTANDARDCASE")
        wall_select = SelectFacet()
        wall_select.applicability = [wall_facet]
        wall_select.list_ifc_path = [self.ifc_path]

        window_facet = ids.Entity(name="IFCFURNISHINGELEMENT")
        window_select = SelectFacet()
        window_select.applicability = [window_facet]
        window_select.list_ifc_path = [self.ifc_path]

        intersection_rule = Collision(window_select, wall_select, 0.01) 

        OneRuleFile.contains=[intersection_rule]
        OneRuleFile.run()

 
        self.assertEqual(len(intersection_rule.result), 1)
        for result in intersection_rule.result:
            self.assertIsInstance(result, ClashResultTwoObjects)

    def test_clearance_rule(self):
        """Test Intersection rule"""

        OneRuleFile = RuleFile()
        OneRuleFile.list_ifc_path= [self.ifc_path]
        wall_facet = ids.Entity(name="IFCWALLSTANDARDCASE")
        wall_select = SelectFacet()
        wall_select.applicability = [wall_facet]
        wall_select.list_ifc_path = [self.ifc_path]

        window_facet = ids.Entity(name="IFCFURNISHINGELEMENT")
        window_select = SelectFacet()
        window_select.applicability = [window_facet]
        window_select.list_ifc_path = [self.ifc_path]

        intersection_rule = Clearance(window_select, wall_select, 1) 

        OneRuleFile.contains=[intersection_rule]
        OneRuleFile.run()

 
        self.assertEqual(len(intersection_rule.result), 1)
        for result in intersection_rule.result:
            self.assertIsInstance(result, ClashResultTwoObjects)






    def test_above_rule(self):
        """Test Above rule"""

        OneRuleFile = RuleFile()
        OneRuleFile.list_ifc_path= [self.ifc_path]
        wall_facet = ids.Entity(name="IFCWALLSTANDARDCASE")
        wall_select = SelectFacet()
        wall_select.applicability = [wall_facet]
        wall_select.list_ifc_path = [self.ifc_path]

        window_facet = ids.Entity(name="IFCWINDOW")
        window_select = SelectFacet()
        window_select.applicability = [window_facet]
        window_select.list_ifc_path = [self.ifc_path]

        above_rule = Above(source=wall_select, target=window_select, tolerance=1, above_type="Above_MaxToMax")
        above_rule.run()

        self.assertGreaterEqual(len(above_rule.result), 0)
        for result in above_rule.result:
            self.assertIsInstance(result, above_rule.ClashResultTwoObjects)

    def test_obb_above_rule(self):
        """Test OBB_Above rule"""
        window_facet = ids.Entity(name="IFCWINDOW")
        window_select = SelectFacet()
        window_select.applicability = [window_facet]
        window_select.list_ifc_path = [self.ifc_path]

        window_select2 = SelectFacet()
        window_select2.applicability = [window_facet]
        window_select2.list_ifc_path = [self.ifc_path]

        obb_above_rule = OBB_Above(window_select, window_select2, 0.1)
        obb_above_rule.run()

        self.assertGreaterEqual(len(obb_above_rule.result), 0)#@todo create a real test
        for result in obb_above_rule.result:
            self.assertIsInstance(result, obb_above_rule.ClashResultTwoObjects)


if __name__ == '__main__':
    unittest.main()
