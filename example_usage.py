#!/usr/bin/env python3
"""
Example usage of IfcClash_Plus with the new import system
"""

import sys
sys.path.insert(0, './src')

# Simple import of the main package
import src

# Or import specific classes directly
from src import Volume, Area, SelectFacet
from src.RuleClass import RuleFile

def main():
    print("IfcClash_Plus - Example Usage")
    print("=" * 40)
    
    # Show available classes from the package
    print("\nAvailable classes from 'import src':")
    classes = [name for name in dir(src) if not name.startswith('_') and name[0].isupper()]
    for cls in classes:
        print(f"  - {cls}")
    
    print("\n" + "=" * 40)
    print("Example: Creating a Volume rule")
    print("-" * 40)
    
    # Example usage (this would need actual IFC files to run)
    print("from src import Volume, SelectFacet")
    print("from ifctester import ids")
    print()
    print("# Create a facet selector")
    print("wall_facet = ids.Entity(name='IFCWALLSTANDARDCASE')")
    print("select_facet = SelectFacet()")
    print("select_facet.applicability = [wall_facet]")
    print("select_facet.list_ifc_path = ['model.ifc']")
    print()
    print("# Create and run volume rule")
    print("volume_rule = Volume(select_facet, 0.001, 1000)")
    print("volume_rule.run()")
    print()
    print("# Access results")
    print("for result in volume_rule.result:")
    print("    print(f'Element: {result.ifc_element}, Volume: {result.volume}')")
    
    print("\n" + "=" * 40)
    print("For more examples, see:")
    print("  - src/exemple.py")
    print("  - tests/test_rules.py")
    print("=" * 40)

if __name__ == "__main__":
    main()