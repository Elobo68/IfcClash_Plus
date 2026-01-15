# IfcClash_Plus
This is a test to find the best solution before trying to implement directly into IfcClash.
We have 4 type of rule that exist inside IfcClash.
-Intersection
-Collision 
-Clearance
-Ray Check 
The idea is to create a lego set of rule that can be used together.

# Progress
The first step is to create new rule to expand possibilities. Those rule can be used in any template.

1. Expand number of rule and create the base structure for rules
2. Create association of rule in python
3. Studies implementation in ifcclash

# Main functionality
- Create a template to standardize rule creation
    I want to create a catalog of rule. In order for them to work, i need a standardization of the functionality to expand them and make them work all together.
    
    For the standardisation, i started a dictionnary to explain my vocabulary. 
    [Vocabulary](Clash_Expend/Rule.md)
- Use IDS to select
    The idea is to reuse IDS Facet to select list of elements. I am pretty sure more and more people are starting to use it, so it will be easier for everyone with time.
- Rule
    The result of a rule will produce a list of object. This list of object can be used in another rule. This can be used to expand the rule functionnality, and complexity.
- Authorize exception
    There is edge case in every case. You can either select them by hand or reduce them. This aim to reduce the edge case to the bare minimum.
- Categorize result
    The BCF can carry information like actor, or criticity. Sometime, these can be done with a script.
    - by actor
    - by criticity
- Regroup result by several way
    I want to expand the way to regroup result of clash.
- Group rule in folder




# Catalog of rule
I will do a sheet for every rule to describe the way it's working and the intended result of that rule.

This is my starting point for a new rule.
[Clearance Above Object](Clash_Expend/2ObjectsRules/ClearanceAbove)

## Two Object Rule
* [Clearance Above Object](Clash_Expend/2ObjectsRules/ClearanceAbove) Status:NOK
* [Clearance Next To Object](Clash_Expend/2ObjectsRules/ClearanceNextTo) Status:NOK
* [Clearance Below Object](Clash_Expend/2ObjectsRules/ClearanceBelow) Status:NOK
* [Cleareance OBB](Clash_Expend/2ObjectsRules/ClearanceOBB) Status:NOK
* [Direct View](Clash_Expend/2ObjectsRules/DirectView) Status:NOK
* [Face Check](Clash_Expend/2ObjectsRules/FaceCheck) Status:NOK
* [Angle Between](Clash_Expend/2ObjectsRules/AngleBetween) Status:NOK
* [Surface Recover](Clash_Expend/2ObjectsRules/SurfaceRecover) Status:NOK


## One Object Rule
* [Volume](Clash_Expend/1ObjectsRules/Orientation) Status:Partial
* [Area](Clash_Expend/1ObjectsRules/Area) Status:NOK
* [Top Surface](Clash_Expend/1ObjectsRules/TopSurface) Status:NOK
* [Bottom Surface](Clash_Expend/1ObjectsRules/BottomSurface) Status:NOK
* [Lateral Surface](Clash_Expend/1ObjectsRules/LateralSurface) Status:NOK
* [Projected Surface](Clash_Expend/1ObjectsRules/ProjectedSurface) Status:NOK

* [Orientation](Clash_Expend/1ObjectsRules/Orientation) Status:NOK


## Complex Rule
* [Free Space in Room](Clash_Expend/1ObjectsRules/Orientation) Status:NOK
* [Find Path](Clash_Expend/ComplexRules/FindPath) Status:NOK
* [EvacuationDistance](Clash_Expend/ComplexRules/EvacuationDistance) Status:NOK
* [Alignement](Clash_Expend/ComplexRules/Alignement) Status:NOK


# Todo List

Create MUST Rule 
Create Actor 