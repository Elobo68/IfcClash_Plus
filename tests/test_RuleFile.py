"""
Test file for RuleFile class functionality.

This file contains various test cases to verify the correct behavior of the RuleFile class,
including loading IFC files, adding rules, executing checks, and managing results.
"""

import unittest
import ifcopenshell
import sys
sys.path.insert(0, './ifcclash_plus')
from Rules import  Intersection, Above,Below ,OBB_Above,Clearance,Collision,OBB_Below, AngleBetween,Volume
from RuleClass import SelectFacet,RuleFile,ClashResultOneObject,ClashResultTwoObjects,RuleFolder
from ifctester import ids
import os


class TestRuleFileBasic(unittest.TestCase):
    """Test basic RuleFile functionalities."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_ifc_path = None
        # Try to find an example IFC file in the repository
        possible_paths = [
            "/home/jocelin/Documents/05 - Programmation/IfcClash_Plus/Ifc_Model/Ifc2x3_Duplex_Architecture_with_suzanne.ifc",
            "/home/jocelin/Documents/05 - Programmation/IfcClash_Plus/Ifc_Model/Ifc2x3_Duplex_MEP.ifc",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                self.test_ifc_path = path
                break
        

    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, '_temp_ifc_file') and self._temp_ifc_file:
            os.remove(self._temp_ifc_file)

    def test_RuleFile_initialization(self):
        """Test RuleFile can be initialized."""
        rule_file = RuleFile()
        self.assertIsInstance(rule_file, RuleFile)
        self.assertEqual(rule_file.list_ifc_path, [])
        self.assertEqual(rule_file.list_ifc_file, [])
        self.assertEqual(rule_file.contains, [])


    def test_RuleFile_load_file(self):
        """Test RuleFile can load IFC files."""
        rule_file = RuleFile()
        rule_file.list_ifc_path = [self.test_ifc_path]
        rule_file.load_file()
        
        self.assertEqual(len(rule_file.list_ifc_file), 1)
        self.assertIsNotNone(rule_file.list_ifc_file[0])

    def test_RuleFile_update_file_info(self):
        """Test RuleFile can update file info in contained rules."""
        rule_file = RuleFile()
        possible_paths = [
            "/home/jocelin/Documents/05 - Programmation/IfcClash_Plus/Ifc_Model/Ifc2x3_Duplex_Architecture.ifc",
            "/home/jocelin/Documents/05 - Programmation/IfcClash_Plus/Ifc_Model/Ifc2x3_Duplex_MEP.ifc",
        ]
        rule_file.list_ifc_path=possible_paths


        rule_file.load_file()
        
        # Create a SelectFacet
        from ifctester.facet import Facet, Entity
        
        # Create a simple select
        from ifcclash_plus.Rules import Collision

        first_facet = ids.Entity(name="IFCWALLSTANDARDCASE")
        first_select = SelectFacet()
        first_select.applicability = [first_facet]

        second_facet = ids.Entity(name="IFCSLAB")
        second_select = SelectFacet()
        second_select.applicability = [second_facet]

        rule_collision=Collision(first_select,second_select)
                
        rule_file.contains = [rule_collision]
        rule_file.update_file_info()


        for rule in rule_file.contains:
            self.assertEqual(len(rule.select_source.list_ifc_file), 2)
            self.assertEqual(len(rule.select_target.list_ifc_file), 2)
            self.assertEqual(len(rule.select_source.list_ifc_path), 2)
            self.assertEqual(len(rule.select_target.list_ifc_path), 2)


class TestRuleFileWithRules(unittest.TestCase):
    """Test RuleFile with actual rules."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_ifc_path = None
        possible_paths = [
            "/home/jocelin/Documents/05 - Programmation/IfcClash_Plus/Ifc_Model/Ifc2x3_Duplex_Architecture.ifc",
            "/home/jocelin/Documents/05 - Programmation/IfcClash_Plus/Ifc_Model/Ifc2x3_Duplex_MEP.ifc",
        ]

        self.test_ifc_path=possible_paths


    def test_RuleFile_with_multiple_rules(self):
        """Test RuleFile can handle multiple rules."""
        rule_file = RuleFile()
        rule_file.list_ifc_path = self.test_ifc_path
        
        # Create multiple rules
        first_facet = ids.Entity(name="IFCWALLSTANDARDCASE")
        first_select = SelectFacet()
        first_select.applicability = [first_facet]

        second_facet = ids.Entity(name="IFCDOOR")
        second_select = SelectFacet()
        second_select.applicability = [second_facet]

        rule1 = Volume(source=first_select, volume_min=0.0, volume_max=1000.0)
        rule2 = Collision(source=first_select, target=second_select, allow_touching=False)
        
        rule_file.contains = [rule1, rule2]
        
        rule_file.run()


        
        self.assertEqual(len(rule_file.contains[0].result), 56)
        self.assertEqual(len(rule_file.contains[1].result), 7)


    def test_RuleFile_with_Folder(self):
        """Test RuleFile can contain folders."""

        rule_file = RuleFile()
        rule_file.list_ifc_path = self.test_ifc_path

        folder=RuleFolder()
        
        # Create multiple rules
        first_facet = ids.Entity(name="IFCWALLSTANDARDCASE")
        first_select = SelectFacet()
        first_select.applicability = [first_facet]

        second_facet = ids.Entity(name="IFCDOOR")
        second_select = SelectFacet()
        second_select.applicability = [second_facet]

        rule1 = Volume(source=first_select, volume_min=0.0, volume_max=1000.0)
        rule2 = Collision(source=first_select, target=second_select, allow_touching=False)

        folder.contains=[rule1, rule2]
        
        rule_file.contains = [folder]
        
        rule_file.run()


        
        self.assertEqual(len(rule_file.contains[0].contains[0].result), 56)
        self.assertEqual(len(rule_file.contains[0].contains[1].result), 7)

    def test_RuleFile_with_Folder_activation_rule(self):
        """Test RuleFile can contain folders."""

        rule_file = RuleFile()
        rule_file.list_ifc_path = self.test_ifc_path

        folder=RuleFolder()
        
        # Create multiple rules
        first_facet = ids.Entity(name="IFCWALLSTANDARDCASE")
        first_select = SelectFacet()
        first_select.applicability = [first_facet]

        second_facet = ids.Entity(name="IFCDOOR")
        second_select = SelectFacet()
        second_select.applicability = [second_facet]

        rule1 = Volume(source=first_select, volume_min=0.0, volume_max=1000.0)
        rule2 = Collision(source=first_select, target=second_select, allow_touching=False)

        folder.contains=[rule2]
        folder.activation_rule=rule1
        
        rule_file.contains = [folder]
        
        rule_file.run()

        self.assertEqual(len(rule_file.contains[0].contains[0].result), 7)

    def test_RuleFile_with_Folder_activation_facet(self):
        """Test RuleFile can contain folders."""

        rule_file = RuleFile()
        rule_file.list_ifc_path = self.test_ifc_path

        folder=RuleFolder()
        
        # Create multiple rules
        first_facet = ids.Entity(name="IFCWALLSTANDARDCASE")
        first_select = SelectFacet()
        first_select.applicability = [first_facet]

        second_facet = ids.Entity(name="IFCDOOR")
        second_select = SelectFacet()
        second_select.applicability = [second_facet]

        rule1 = Volume(source=first_select, volume_min=0.0, volume_max=1000.0)
        rule2 = Collision(source=first_select, target=second_select, allow_touching=False)

        folder.contains=[rule2]
        folder.activation_rule=first_select
        
        rule_file.contains = [folder]
        
        rule_file.run()

        self.assertEqual(len(rule_file.contains[0].contains[0].result), 7)

class TestRuleFileProperties(unittest.TestCase):
    """Test RuleFile properties and attributes."""

    def test_RuleFile_id(self):
        """Test RuleFile id property."""
        rule_file = RuleFile()
        rule_file.id = "test_rule_file"
        self.assertEqual(rule_file.id, "test_rule_file")

    def test_RuleFile_path_to_save(self):
        """Test RuleFile path_to_save property."""
        rule_file = RuleFile()
        rule_file.path_to_save = "/tmp/test_output.xml"
        self.assertEqual(rule_file.path_to_save, "/tmp/test_output.xml")


if __name__ == "__main__":
    unittest.main()
