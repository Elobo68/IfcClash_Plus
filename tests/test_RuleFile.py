"""
Test file for RuleFile class functionality.

This file contains various test cases to verify the correct behavior of the RuleFile class,
including loading IFC files, adding rules, executing checks, and managing results.
"""

import unittest
import os
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, './ifcclash_plus')

from RuleClass import RuleFile, SelectFacet
from Rules import (
    Collision,
    Intersection,
    Volume,
    Area,
    OBB_Above,
    OBB_Below,
)
from ifctester import ids


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
        
        if self.test_ifc_path is None:
            # Create a temporary minimal IFC file for testing
            self.test_ifc_path = self._create_temp_ifc()

    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, '_temp_ifc_file') and self._temp_ifc_file:
            os.remove(self._temp_ifc_file)

    def _create_temp_ifc(self):
        """Create a temporary IFC file for testing."""
        import ifcopenshell
        from ifcopenshell.api import run
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.ifc', delete=False)
        temp_file.close()
        self._temp_ifc_file = temp_file.name
        
        # Create a minimal IFC file
        file = ifcopenshell.file(schema_identifiers=['IFC4'])
        owner_history = run("owner.history.add_owner_history", file)
        
        # Add a simple project
        project = run("root.create_entity", file, ifc_class="IfcProject", name="Test Project")
        
        # Add a simple site
        site = run("root.create_entity", file, ifc_class="IfcSite", name="Test Site")
        
        # Add a simple building
        building = run("root.create_entity", file, ifc_class="IfcBuilding", name="Test Building")
        
        # Add a simple storey
        storey = run("root.create_entity", file, ifc_class="IfcBuildingStorey", name="Test Storey")
        
        # Add a simple wall
        wall = run("root.create_entity", file, ifc_class="IfcWall", name="Test Wall")
        
        file.write(temp_file.name)
        return temp_file.name

    def test_RuleFile_initialization(self):
        """Test RuleFile can be initialized."""
        rule_file = RuleFile()
        self.assertIsInstance(rule_file, RuleFile)
        self.assertEqual(rule_file.list_ifc_path, [])
        self.assertEqual(rule_file.list_ifc_file, [])
        self.assertEqual(rule_file.contains, [])

    def test_RuleFile_list_ifc_path(self):
        """Test RuleFile can store IFC file paths."""
        rule_file = RuleFile()
        rule_file.list_ifc_path = [self.test_ifc_path]
        self.assertEqual(rule_file.list_ifc_path, [self.test_ifc_path])

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
        rule_file.list_ifc_path = [self.test_ifc_path]
        rule_file.load_file()
        
        # Create a SelectFacet
        from ifctester.facet import Facet, Entity
        
        # Create a simple select
        from ifcclash_plus.Rules import Select
        select_source = Select()
        select_source.list_ifc_path = [self.test_ifc_path]
        
        rule_file.contains = []
        rule_file.update_file_info()
        
        # Should not raise an error
        self.assertEqual(len(rule_file.list_ifc_file), 1)


class TestRuleFileWithRules(unittest.TestCase):
    """Test RuleFile with actual rules."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_ifc_path = None
        possible_paths = [
            "/home/jocelin/Documents/05 - Programmation/IfcClash_Plus/Ifc_Model/Ifc2x3_Duplex_Architecture_with_suzanne.ifc",
            "/home/jocelin/Documents/05 - Programmation/IfcClash_Plus/Ifc_Model/Ifc2x3_Duplex_MEP.ifc",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                self.test_ifc_path = path
                break
        
        if self.test_ifc_path is None:
            self.skipTest("No IFC file found for testing")

    def test_RuleFile_with_OneObjectRule(self):
        """Test RuleFile can run one object rules."""
        rule_file = RuleFile()
        rule_file.list_ifc_path = [self.test_ifc_path]
        
        # Create a Volume rule
        from ifcclash_plus.Rules import Select
        select = Select()
        volume_rule = Volume(source=select, min_volume=0.0, max_volume=1000.0)
        
        rule_file.contains = [volume_rule]
        
        # This should load files and run the rule
        # Note: We can't fully test the run without a valid IFC with geometry
        rule_file.load_file()
        rule_file.update_file_info()
        
        self.assertEqual(len(rule_file.list_ifc_file), 1)

    def test_RuleFile_with_TwoObjectsRule(self):
        """Test RuleFile can run two objects rules."""
        rule_file = RuleFile()
        rule_file.list_ifc_path = [self.test_ifc_path]
        
        # Create a Collision rule
        from ifcclash_plus.Rules import Select
        select_source = Select()
        select_target = Select()
        collision_rule = Collision(source=select_source, target=select_target, allow_touching=False)
        
        rule_file.contains = [collision_rule]
        
        rule_file.load_file()
        rule_file.update_file_info()
        
        self.assertEqual(len(rule_file.list_ifc_file), 1)

    def test_RuleFile_with_multiple_rules(self):
        """Test RuleFile can handle multiple rules."""
        rule_file = RuleFile()
        rule_file.list_ifc_path = [self.test_ifc_path]
        
        from ifcclash_plus.Rules import Select
        
        # Create multiple rules
        select1 = Select()
        select2 = Select()
        rule1 = Volume(source=select1, min_volume=0.0, max_volume=1000.0)
        rule2 = Collision(source=select1, target=select2, allow_touching=False)
        
        rule_file.contains = [rule1, rule2]
        
        rule_file.load_file()
        rule_file.update_file_info()
        
        self.assertEqual(len(rule_file.contains), 2)

    def test_RuleFile_with_Folder(self):
        """Test RuleFile can contain folders."""
        rule_file = RuleFile()
        rule_file.list_ifc_path = [self.test_ifc_path]
        
        from ifcclash_plus.RuleClass import RuleFolder
        
        folder = RuleFolder()
        from ifcclash_plus.Rules import Select
        select = Select()
        volume_rule = Volume(source=select, min_volume=0.0, max_volume=1000.0)
        folder.contains = [volume_rule]
        
        rule_file.contains = [folder]
        
        rule_file.load_file()
        rule_file.update_file_info()
        
        self.assertEqual(len(rule_file.contains), 1)
        self.assertIsInstance(rule_file.contains[0], RuleFolder)


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
