# IfcClash_Plus
This is a test to find the best solution before trying to implement directly into IfcClash.
We have for type of rule that exist inside IfcClash.
-Intersection
-Collision
-Clearance
-Ray Check
The first 4 rules can be expended with other to complete them. With some basics rules, we could easily combine them to construct rule that fit exactly the issue. The idea is to create a lego set of rule.

# Progress
The first step is to create new rule to expand possibilities. Those rule can be used in any template.

1. Expand number of rule
2. Create them in python
3. Create a C++ version
4. Add rule in existing IfcClash
5. Look for association of rules


# New Rule
I will do a sheet for every rule to describe the way it's working and the intended result of that rule.

This is my starting point.
[Clearance Above Object](Clash_Expend/2ObjectsRules/ClearanceAbove)

## Two Object Rule
* [Clearance Above Object](Clash_Expend/2ObjectsRules/ClearanceAbove)
* [Clearance Next To Object](Clash_Expend/2ObjectsRules/ClearanceNextTo)
* [Clearance Below Object](Clash_Expend/2ObjectsRules/ClearanceBelow)
* [Cleareance In Front Of](Clash_Expend/2ObjectsRules/ClearanceInFrontOf)
* [Direct View](Clash_Expend/2ObjectsRules/DirectView)
* [Face Check](Clash_Expend/2ObjectsRules/FaceCheck)
* [Angle Between](Clash_Expend/2ObjectsRules/AngleBetween)
* [Surface Recover](Clash_Expend/2ObjectsRules/SurfaceRecover)


## One Object Rule
* [Volume](Clash_Expend/1ObjectsRules/Orientation)
* [Orientation](Clash_Expend/1ObjectsRules/Orientation)


## Complex Rule
* [Free Space in Room](Clash_Expend/1ObjectsRules/Orientation)
* [Find Path](Clash_Expend/ComplexRules/FindPath)
* [EvacuationDistance](Clash_Expend/ComplexRules/EvacuationDistance)
* [Alignement](Clash_Expend/ComplexRules/Alignement)


Right now, i am working in python but i intend to replicate the logic in C++.
It must give me all the edge case.

# POC
I have made a first POC to test a new template to describe and launch Clash.
* Selecting objects from several model
* Result of clash can be used as entry set for other rule
* Re-use facet of IDS to select objects based on object data

Here you can find some explanation of the POC.
[https://github.com/IfcOpenShell/IfcOpenShell/discussions/6863]

The POC is over. 


