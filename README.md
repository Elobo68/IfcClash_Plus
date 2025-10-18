# IfcClash_Plus
 
This is a test to find the best solution before trying to implement directly to pull into IfcOpenshell.
We have for type of rule that exist inside IfcClash.
-Intersection
-Collision
-Clearance
-Ray Check
The first 4 rules can be expended with other to complete them. With some basics rules, we could easily combine them to construct rule that fit exactly the issue. The idea is to create a lego set of rule.

# New Rule
I will do a sheet for every rule to describe the way it's working.
-Clearance Above Object (and Below)
-Clearance Next To Object
-Direct Ray with Object
-Parralel Object
-Oriented Object

Right now, i am working in python but i intend to replicate the logic in C++

# POC
I have made a first POC to test a new template to describe and launch Clash.
-Selecting objects from several model
-Result of clash can be used as entry set for other rule
-Re-use facet of IDS to select objects based on object data

The idea now is to create robust rule, to expand number of rule without changing the template.
Those rule can fit any template.

