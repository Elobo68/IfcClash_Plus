# Package initialization for ifcclash_plus
# This makes the package installable

# Expose main modules for easy importing
from .Rules import (
    Volume, Area, TopSurface, Intersection, Clearance, Above, 
    OBB_Above, Ray_Check
)
from .RuleClass import SelectFacet, SelectRule, RuleFile
from .CustomOBB import Custom_OBB
from .rule_serializer import save_to_xml, load_from_xml

__all__ = [
    'Volume', 'Area', 'TopSurface', 'Intersection', 'Clearance', 'Above',
    'OBB_Above', 'Ray_Check', 'SelectFacet', 'SelectRule', 'RuleFile',
    'Custom_OBB', 'save_to_xml', 'load_from_xml'
]

__version__ = "0.3.0"
