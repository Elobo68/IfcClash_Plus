# Set of Objects
In this project, we will give name to each set in the rules.
We have three type of elements
* Source
* Target
* Context

The set of objects may be from differents models.

## Source
Those are the objects we are testing. They will be our primary set for the clash.

## Target
The targets are beeing tested. They will be the secondary set for the clash.

## Context Objects
The context objects are not directly in the clash, but they will be used as complementary information.
For example, if we want to test free sight between two objects (A and B). The wall and slab will be used as context elements to determine free sight.

# ASymetric Rule
When the rule has two sets, the rule is not symetric. 
* A vs B does not produce the same result as B vs A.

By default, this will help to understand the result of a rule. The rule will always provide the source objects (A is that case).
B objects can be given has well in the result, but they will be complimentary.

# Type Of Rule
Rule can be classified into several categories. They are centered with the number of elements needed for the clash.
All rule can be launched on set of objects, but at the end, the script will test single, pair or multiple objects against each other.

## One Object Rules
This rule will only test one object a the time.

### Example
The object must have a top surface of 10m2.
The object must be oriented to the south.

## Two Objects Rules
These rules are the most common one. They will take the form A vs B.



## Two Faces Rules
WORK IN PROGRESS
This rule work on a face level. It can restrict rule application to certains cases.
If the Object Rule find a relevant face, i can still pass it threw Faces Rule to check if the restriction is OK.
I need to pass the faces with the result.




### Example
The table is below the light.
The wall is at one meter of a chair
The top of the light is below a slab.

## Complex Rules
Complex rules will need several set of objects.

### Example
Rule to check the wheelchair circle will use IfcSpace and furniture.
* We can't say if the space is falty or the furniture.
Check if there is a cable carrier path in between two room.
* We can't really aim for a source object, nor a target.

# Grouping Result


## Group by IfcRelation
Group by IfcSpace
Group by IfcBuildingStorey

## Other Group Method
Group by Source Object
Group by Gravity
Group with clustering

## Filtering Grouping
WORK IN PROGRESS
After Grouping, we could still select a restriction of objects.
Keep only the two closest one
Keep only the two fu

# Exceptions
"Exception that proves the rule"
With every rule, we need to consider exceptions. Edge case are everywhere.
There will always be exceptions, but we can at least reduce them.

## Geometry Exception
If we have a 2 objects Rule, that will produce a pair of two objects, we can reuse existing 2 objects rules to make futher check.

## Relation Exception
IfcSystem Exception

## Example
If we detect collision between two cable carrier, we must check if they are in the same IfcSystem. 
If they are, that's probably only a modeling problem, not a real world issue.

# Must Rule
WORK IN PROGRESS
## Absolute Number of Elements

The number of target elements must be X times the number of source elements. 

The relation can be from source.


## Relative Number of Elements

## Absolute Quantity

## Relative Quantity

# Activation of a Rule
WORK IN PROGRESS



# Folder of Rule
WORK IN PROGRESS