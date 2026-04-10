# Package initialization for ifcclash_plus
# This makes the package installable

# Expose main modules for easy importing
from .Rules import (
    Volume, Area, TopSurface, Intersection, Clearance, Above, 
    OBB_Above, Ray_Check
)
from .RuleClass import SelectFacet, SelectRule, RuleFile
from .CustomOBB import Custom_OBB

__all__ = [
    'Volume', 'Area', 'TopSurface', 'Intersection', 'Clearance', 'Above',
    'OBB_Above', 'Ray_Check', 'SelectFacet', 'SelectRule', 'RuleFile',
    'Custom_OBB'
]

__version__ = "0.3.0"