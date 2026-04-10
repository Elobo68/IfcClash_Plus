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

V0.1
Create the main structure of script

V0.2
- Create Above Rule
    This rule check if there is nothing above an object.

- Create several grouping function
    The rule create a list of result. This list of result can be grouped by different way. I implemented several way of grouping object. 
- Create absolute and relative check
    By grouping object, you create a sets of object. It's important to check if these set respect a rule. 
    I must have at least one door intersecting with each space. 
    I must have at exactly 1 drain below a shower drain. 

- Create a criticity automatic classification
    Each result can be automaticaly classified in order to determine it's criticity.This could be exporter toward a BCF. 
- Update the actor automatic classification
    Each result can be automaticaly classified in order to determine an actor to tag. This could be exporter toward a BCF. 




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
- Waterfall of Rule
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
[Clearance Above Object](Clash_Expend/2ObjectsRules/ClearanceAbove/README.md)

## Two Object Rule
* [Clearance Above Object](Clash_Expend/2ObjectsRules/ClearanceAbove/README.md) Status:OK
* [Clearance Below Object](Clash_Expend/2ObjectsRules/ClearanceBelow/README.md) Status:NOK
* [Clearance Next To Object](Clash_Expend/2ObjectsRules/ClearanceNextTo/README.md) Status:NOK


* [Cleareance OBB](Clash_Expend/2ObjectsRules/ClearanceOBB/README.md) Status:NOK
* [Cleareance OBB - Front Or Back](Clash_Expend/2ObjectsRules/ClearanceOBB/README_FrontOrBack.md) Status:NOK
* [Cleareance OBB - Custom OBB](Clash_Expend/2ObjectsRules/ClearanceOBB/README_CustomOBB.md) Status:NOK


* [Direct View](Clash_Expend/2ObjectsRules/DirectView/README.md) Status:NOK
* [Face Check](Clash_Expend/2ObjectsRules/FaceCheck/README.md) Status:NOK
* [Angle Between](Clash_Expend/2ObjectsRules/AngleBetween/README.md) Status:NOK
* [Surface Recover](Clash_Expend/2ObjectsRules/SurfaceRecover/README.md) Status:NOK


## One Object Rule
* [Volume](Clash_Expend/1ObjectsRules/Orientation/README.md) Status:Partial
* [Area](Clash_Expend/1ObjectsRules/Area/README.md) Status:Partial
* [Top Surface](Clash_Expend/1ObjectsRules/TopSurface/README.md) Status:Partial
* [Bottom Surface](Clash_Expend/1ObjectsRules/BottomSurface/README.md) Status:NOK
* [Lateral Surface](Clash_Expend/1ObjectsRules/LateralSurface/README.md) Status:NOK
* [Projected Surface](Clash_Expend/1ObjectsRules/ProjectedSurface/README.md) Status:NOK
* [Orientation](Clash_Expend/1ObjectsRules/Orientation/README.md) Status:NOK


## Complex Rule
* [Free Space in Room](Clash_Expend/1ObjectsRules/Orientation/README.md) Status:NOK
* [Find Path](Clash_Expend/ComplexRules/FindPath/README.md) Status:NOK
* [EvacuationDistance](Clash_Expend/ComplexRules/EvacuationDistance/README.md) Status:NOK
* [Alignement](Clash_Expend/ComplexRules/Alignement/README.md) Status:NOK


# Todo List
#@todo Create a function to create the geometry of each function. This can help to vizualise the clash volume
#@todo Enable to use "another" geometry for each object, main geometry, but we could use "function geometry", or simplified geometry
#@todo Retrieve point of entry and other info about the clash
#@todo 



