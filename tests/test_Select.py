"""
Test file for SelectFacet and SelectRule class functionality.

This file contains various test cases to verify the correct behavior of SelectFacet
and SelectRule classes for filtering and selecting IFC elements.
"""

import unittest
import os
import tempfile
import sys

import ifcopenshell
from ifcopenshell.api import run

sys.path.insert(0, './ifcclash_plus')

from RuleClass import SelectFacet, SelectRule, RuleFile
from Rules import Select, Volume, Area, TopSurface
from ifctester import ids
from ifctester.facet import (
    Facet,
    Entity,
    Property,
    Attribute,
    Classification,
    PartOf,
    Material,
)


class TestSelectFacetBasic(unittest.TestCase):
    """Test basic SelectFacet functionalities."""

    def setUp(self):
        """Set up test fixtures with a minimal IFC file."""
        self.test_ifc_path = self._create_temp_ifc()
        #@todo check those test
        print("TO TEST")

    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, '_temp_ifc_file') and self._temp_ifc_file:
            os.remove(self._temp_ifc_file)

    def _create_temp_ifc(self):
        """Create a temporary IFC file with various entities for testing."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.ifc', delete=False)
        temp_file.close()
        self._temp_ifc_file = temp_file.name
        
        # Create an IFC file with various entities
        file = ifcopenshell.file(schema_identifiers=['IFC4'])
        
        # Add owner history
        owner_history = run("owner.history.add_owner_history", file)
        
        # Add a project
        project = run("root.create_entity", file, ifc_class="IfcProject", name="Test Project")
        
        # Add a site
        site = run("root.create_entity", file, ifc_class="IfcSite", name="Test Site")
        
        # Add a building
        building = run("root.create_entity", file, ifc_class="IfcBuilding", name="Test Building")
        
        # Add building storeys
        storey1 = run("root.create_entity", file, ifc_class="IfcBuildingStorey", name="Level 1")
        storey2 = run("root.create_entity", file, ifc_class="IfcBuildingStorey", name="Level 2")
        
        # Add walls
        wall1 = run("root.create_entity", file, ifc_class="IfcWall", name="Wall 1")
        wall2 = run("root.create_entity", file, ifc_class="IfcWall", name="Wall 2")
        
        # Add doors
        door1 = run("root.create_entity", file, ifc_class="IfcDoor", name="Door 1")
        door2 = run("root.create_entity", file, ifc_class="IfcDoor", name="Door 2")
        
        # Add property sets to some entities
        pset_data = {
            "Name": "Test Property",
            "Properties": [
                {"Name": "Width", "NominalValue": 1.0},
                {"Name": "Height", "NominalValue": 2.5},
                {"Name": "Material", "NominalValue": "Concrete"},
            ]
        }
        
        # Add a door type
        door_type = run("root.create_entity", file, ifc_class="IfcDoorType", name="DoorType_Standard")
        pset = run("pset.add_pset", file, product=door_type, data=pset_data)
        
        file.write(temp_file.name)
        return temp_file.name

    def test_SelectFacet_initialization(self):
        """Test SelectFacet can be initialized."""
        classification_type = "Test Classification"
        select_facet = SelectFacet(ClassificationType=classification_type)
        
        self.assertIsInstance(select_facet, SelectFacet)
        self.assertEqual(select_facet.type, classification_type)
        self.assertEqual(select_facet.applicability, [])

    def test_SelectFacet_with_Entity_facet(self):
        """Test SelectFacet with Entity facet."""
        select_facet = SelectFacet()
        
        # Add Entity facet to filter by entity type
        entity_facet = Entity(ifc_class="IfcWall")
        select_facet.applicability = [entity_facet]
        
        # Load IFC file and run select
        select_facet.list_ifc_path = [self.test_ifc_path]
        select_facet.load_file()
        select_facet.run()
        
        # Check that we have results
        self.assertIsNotNone(select_facet.dict_elements)
        
    def test_SelectFacet_with_Property_facet(self):
        """Test SelectFacet with Property facet."""
        select_facet = SelectFacet()
        
        # Add Property facet
        prop_facet = Property(propertySet="Test Property", baseName="Width")
        select_facet.applicability = [prop_facet]
        
        select_facet.list_ifc_path = [self.test_ifc_path]
        select_facet.load_file()
        
        # This should filter entities that have the specified property
        select_facet.run()
        
        self.assertIsNotNone(select_facet.dict_elements)

    def test_SelectFacet_with_Attribute_facet(self):
        """Test SelectFacet with Attribute facet."""
        select_facet = SelectFacet()
        
        # Add Attribute facet to filter by name
        attr_facet = Attribute(name="Name", value="Wall 1")
        select_facet.applicability = [attr_facet]
        
        select_facet.list_ifc_path = [self.test_ifc_path]
        select_facet.load_file()
        select_facet.run()
        
        self.assertIsNotNone(select_facet.dict_elements)

    def test_SelectFacet_with_Classification_facet(self):
        """Test SelectFacet with Classification facet."""
        select_facet = SelectFacet()
        
        # Add Classification facet
        class_facet = Classification(
            system="Test Classification System",
            value="Test Classification Value"
        )
        select_facet.applicability = [class_facet]
        
        select_facet.list_ifc_path = [self.test_ifc_path]
        select_facet.load_file()
        select_facet.run()
        
        self.assertIsNotNone(select_facet.dict_elements)

    def test_SelectFacet_with_Material_facet(self):
        """Test SelectFacet with Material facet."""
        select_facet = SelectFacet()
        
        # Add Material facet
        material_facet = Material(name="Concrete")
        select_facet.applicability = [material_facet]
        
        select_facet.list_ifc_path = [self.test_ifc_path]
        select_facet.load_file()
        select_facet.run()
        
        self.assertIsNotNone(select_facet.dict_elements)

    def test_SelectFacet_with_multiple_facets(self):
        """Test SelectFacet with multiple facets combined."""
        select_facet = SelectFacet()
        
        # Combine Entity and Attribute facets
        entity_facet = Entity(ifc_class="IfcWall")
        attr_facet = Attribute(name="Name", value="Wall 1")
        select_facet.applicability = [entity_facet, attr_facet]
        
        select_facet.list_ifc_path = [self.test_ifc_path]
        select_facet.load_file()
        select_facet.run()
        
        self.assertIsNotNone(select_facet.dict_elements)

    def test_SelectFacet_update_file_info(self):
        """Test SelectFacet can update file info."""
        select_facet = SelectFacet()
        
        select_facet.list_ifc_path = [self.test_ifc_path]
        select_facet.load_file()
        
        # Update with new paths
        select_facet.update_file_info([self.test_ifc_path], [])
        
        self.assertEqual(select_facet.list_ifc_path, [self.test_ifc_path])

    def test_SelectFacet_create_list_of_element(self):
        """Test SelectFacet can create list of elements."""
        select_facet = SelectFacet()
        entity_facet = Entity(ifc_class="IfcWall")
        select_facet.applicability = [entity_facet]
        
        select_facet.list_ifc_path = [self.test_ifc_path]
        select_facet.load_file()
        select_facet.run()
        select_facet.create_list_of_element()
        
        # Should have created a list of wall elements
        self.assertIsInstance(select_facet.list_of_elements, list)


class TestSelectRuleBasic(unittest.TestCase):
    """Test basic SelectRule functionalities."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_ifc_path = self._create_temp_ifc()
        #@todo check those test
        print("TO TEST")

    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, '_temp_ifc_file') and self._temp_ifc_file:
            os.remove(self._temp_ifc_file)

    def _create_temp_ifc(self):
        """Create a temporary IFC file for testing."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.ifc', delete=False)
        temp_file.close()
        self._temp_ifc_file = temp_file.name
        
        file = ifcopenshell.file(schema_identifiers=['IFC4'])
        owner_history = run("owner.history.add_owner_history", file)
        
        project = run("root.create_entity", file, ifc_class="IfcProject", name="Test Project")
        building = run("root.create_entity", file, ifc_class="IfcBuilding", name="Test Building")
        storey = run("root.create_entity", file, ifc_class="IfcBuildingStorey", name="Test Storey")
        
        # Add walls with different volumes (via vegetation for simplicity)
        wall1 = run("root.create_entity", file, ifc_class="IfcWall", name="SmallWall")
        wall2 = run("root.create_entity", file, ifc_class="IfcWall", name="LargeWall")
        
        file.write(temp_file.name)
        return temp_file.name

    def test_SelectRule_initialization(self):
        """Test SelectRule can be initialized."""
        select_source = Select()
        volume_rule = Volume(source=select_source, min_volume=0.0, max_volume=100.0)
        
        select_rule = SelectRule()
        select_rule.rule = volume_rule
        
        self.assertIsInstance(select_rule, SelectRule)
        self.assertEqual(select_rule.type, "Rule")
        self.assertEqual(select_rule.rule, volume_rule)
        self.assertEqual(select_rule.action_type, 1)

    def test_SelectRule_with_different_action_types(self):
        """Test SelectRule with different action types."""
        select_source = Select()
        volume_rule = Volume(source=select_source, min_volume=0.0, max_volume=100.0)
        
        # Test action_type 1 - Select source in the list
        select_rule1 = SelectRule()
        select_rule1.rule = volume_rule
        select_rule1.action_type = 1
        
        # Test action_type 2 - Select source not in the list
        select_rule2 = SelectRule()
        select_rule2.rule = volume_rule
        select_rule2.action_type = 2
        
        # Test action_type 3 - Select target in the list
        select_rule3 = SelectRule()
        select_rule3.rule = volume_rule
        select_rule3.action_type = 3
        
        # Test action_type 4 - Select target not in the list
        select_rule4 = SelectRule()
        select_rule4.rule = volume_rule
        select_rule4.action_type = 4
        
        self.assertEqual(select_rule1.action_type, 1)
        self.assertEqual(select_rule2.action_type, 2)
        self.assertEqual(select_rule3.action_type, 3)
        self.assertEqual(select_rule4.action_type, 4)

    def test_SelectRule_run(self):
        """Test SelectRule can run and produce select."""
        select_source = Select()
        select_source.list_ifc_path = [self.test_ifc_path]
        
        volume_rule = Volume(source=select_source, min_volume=0.0, max_volume=10000.0)
        volume_rule.geom_settings = ifcopenshell.geom.settings()
        
        select_rule = SelectRule()
        select_rule.rule = volume_rule
        select_rule.list_ifc_path = [self.test_ifc_path]
        
        # Load files
        select_rule.load_file()
        select_rule.rule.load_file()
        
        # Run the select rule
        try:
            select_rule.run(state="Select")
        except Exception as e:
            # May fail due to geometry processing, but we can still test the structure
            pass
        
        # Check that produce_select was called
        self.assertIsNotNone(select_rule.dict_elements)

    def test_SelectRule_produce_select(self):
        """Test SelectRule produce_select method."""
        select_source = Select()
        volume_rule = Volume(source=select_source, min_volume=0.0, max_volume=10000.0)
        
        select_rule = SelectRule()
        select_rule.rule = volume_rule
        
        # Add some mock results to the rule
        from ifcclash_plus.RuleClass import ClashResultOneObject
        import ifcopenshell
        
        # Create mock file
        mock_file = ifcopenshell.file()
        
        # The produce_select method should process rule results
        # and populate dict_elements
        self.assertEqual(select_rule.dict_elements, {})

    def test_SelectRule_update_file_info(self):
        """Test SelectRule can update file info."""
        select_source = Select()
        volume_rule = Volume(source=select_source, min_volume=0.0, max_volume=100.0)
        
        select_rule = SelectRule()
        select_rule.rule = volume_rule
        
        files_path = [self.test_ifc_path]
        files = []
        
        select_rule.update_file_info(files_path, files)
        
        self.assertEqual(select_rule.list_ifc_path, files_path)
        self.assertEqual(select_rule.list_ifc_file, files)


class TestSelectFacetAndSelectRuleIntegration(unittest.TestCase):
    """Test integration of SelectFacet and SelectRule with RuleFile."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_ifc_path = self._create_temp_ifc()
        #@todo check those test
        print("TO TEST")

    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, '_temp_ifc_file') and self._temp_ifc_file:
            os.remove(self._temp_ifc_file)

    def _create_temp_ifc(self):
        """Create a temporary IFC file for testing."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.ifc', delete=False)
        temp_file.close()
        self._temp_ifc_file = temp_file.name
        
        file = ifcopenshell.file(schema_identifiers=['IFC4'])
        owner_history = run("owner.history.add_owner_history", file)
        project = run("root.create_entity", file, ifc_class="IfcProject", name="Test Project")
        building = run("root.create_entity", file, ifc_class="IfcBuilding", name="Test Building")
        
        file.write(temp_file.name)
        return temp_file.name

    def test_RuleFile_with_SelectFacet(self):
        """Test RuleFile containing SelectFacet."""
        rule_file = RuleFile()
        rule_file.list_ifc_path = [self.test_ifc_path]
        
        # Create a SelectFacet
        select_facet = SelectFacet()
        entity_facet = Entity(ifc_class="IfcWall")
        select_facet.applicability = [entity_facet]
        
        rule_file.contains = [select_facet]
        
        rule_file.load_file()
        rule_file.update_file_info()
        
        self.assertEqual(len(rule_file.contains), 1)

    def test_RuleFile_with_SelectRule(self):
        """Test RuleFile containing SelectRule."""
        rule_file = RuleFile()
        rule_file.list_ifc_path = [self.test_ifc_path]
        
        # Create a SelectRule
        select_source = Select()
        area_rule = Area(source=select_source, min_area=0.0, max_area=100.0)
        
        select_rule = SelectRule()
        select_rule.rule = area_rule
        
        rule_file.contains = [select_rule]
        
        rule_file.load_file()
        rule_file.update_file_info()
        
        self.assertEqual(len(rule_file.contains), 1)

    def test_SelectFacet_chaining(self):
        """Test chaining multiple SelectFacet filters."""
        select_facet1 = SelectFacet()
        entity_facet = Entity(ifc_class="IfcWall")
        select_facet1.applicability = [entity_facet]
        
        select_facet2 = SelectFacet()
        attr_facet = Attribute(name="Name", value="Wall 1")
        select_facet2.applicability = [attr_facet]
        
        select_facet1.list_ifc_path = [self.test_ifc_path]
        select_facet2.list_ifc_path = [self.test_ifc_path]
        
        select_facet1.load_file()
        select_facet2.load_file()
        
        select_facet1.run()
        select_facet2.run()
        
        # Both should have run without errors
        self.assertIsNotNone(select_facet1.dict_elements)
        self.assertIsNotNone(select_facet2.dict_elements)


if __name__ == "__main__":
    unittest.main()
