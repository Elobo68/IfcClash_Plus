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

V0.3
- IA Use
I have started to use IA to create function. Previously, it was way more sporadic.

- Create custom OBB Class
This is a customOBB class made with the Bnd_OBB() class from OCC. It will help to modify existing OBB, in order to expand, detach side or top. 
This new OBB will then create a new space that can clash with objects.
The obb is very convienent to modify, and easy enough to apply transformation.

- Function to generate OBB
I created several function to generate OBB from object. Some of them are better than other.
One of them, is interessting, because it create an OBB with the Z axis stuck to (0,0,1). It's helpful for box like object.

- Add a display function
This function should help to see, what should happen in the rule. It will print OBB Box, where the clash should appear.
It will show the object that are 

- OBB Top and bottom
This rule will check if something is above or below an object. It will create a new obb in the top (or bottom) of the object and check if something clash with it.
It's a little bit different from Above or Below rule, because you can modify the size of the OBB more precisely. 

- OBB Front and Back
This rule will check if something is in front or in the back of the object.
It's quite hard to detect what is the front and back. I am using the size of the OBB to detect that. It will be then dependent to each objects.
For a door, the front is the wide part. For some other object, it will be the narrow part.

- Added a few test case to help debug everything
still WIP

1. Expand number of rule and create the base structure for rules
2. Create association of rule in python
3. Studies implementation in ifcclash

# Main functionality
- Create a template to standardize rule creation
    I want to create a catalog of rule. In order for them to work, i need a standardization of the functionality to expand them and make them work all together.
    
    For the standardisation, i started a dictionnary to explain my vocabulary. 
    [Vocabulary](doc/Rule.md)
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
There is a sheet for every rule, that present the rule, the parameters and the edge case.


## One Object Rule
* [Volume](doc/1ObjectsRules/Volume) ----------------Rule:OK Doc:KO test:OK
* [Area](doc/1ObjectsRules/Area) ---------------------Rule:OK Doc:KO test:OK
* [Top Surface](doc/1ObjectsRules/TopSurface) ----------Rule:OK Doc:KO test:OK
* [Bottom Surface](doc/1ObjectsRules/BottomSurface) ----Rule:OK Doc:KO test:KO
* [Lateral Surface](doc/1ObjectsRules/LateralSurface) -----Rule:OK Doc:KO test:KO
* [Projected Surface](doc/1ObjectsRules/ProjectedSurface) -Rule:OK Doc:KO test:KO
* [Orientation](doc/1ObjectsRules/Orientation)-----------Rule:OK Doc:KO test:OK

## Two Object Rule

### Historic IfcClash Rule
* [Clearance](doc/2ObjectsRules/Clearance)------Rule:OK Doc:KO test:OK
* [Intersection](doc/2ObjectsRules/Intersection)-- Rule:OK Doc:KO test:OK
* [Collision](doc/2ObjectsRules/Collision)--------Rule:OK Doc:KO test:OK

### Advance Clearance Rule
* [Clearance Above Object](doc/2ObjectsRules/ClearanceAbove.md)------Rule:OK Doc:KO test:KO
* [Clearance Next To Object](doc/2ObjectsRules/ClearanceNextTo)----Rule:KO Doc:KO test:KO
* [Clearance Below Object](doc/2ObjectsRules/ClearanceBelow)------Rule:KO Doc:KO test:KO

### Clearance with OBB
* [OBB Above](doc/2ObjectsRules/OBB_Above)----------------Rule:OK Doc:KO test:OK
* [OBB Below](doc/2ObjectsRules/OBB_Below)----------------Rule:OK Doc:KO test:Partial
* [OBB Front And Back](doc/2ObjectsRules/OBB_Front_And_Back)--Rule:KO Doc:KO test:KO

### Other type of rule
* [Surface Recover](doc/2ObjectsRules/SurfaceRecover)---Rule:KO Doc:KO test:KO
* [Angle Between](doc/2ObjectsRules/AngleBetween)----Rule:KO Doc:KO test:KO
* [Direct View](doc/2ObjectsRules/DirectView)----------Rule:KO Doc:KO test:KO
* [Face Check](doc/2ObjectsRules/FaceCheck)-----------Rule:KO Doc:KO test:KO


## Complex Rule
* [Free Space in Room](doc/1ObjectsRules/Orientation) Rule:KO Doc:KO test:KO
* [Find Path](doc/ComplexRules/FindPath) Rule:KO Doc:KO test:KO
* [EvacuationDistance](doc/ComplexRules/EvacuationDistance) Rule:NOK Doc:KO test:KO
* [Alignement](doc/ComplexRules/Alignement) Rule:NOK Doc:KO test:KO


# Todo List
