# Description
This rule check that the object is facing the right direction.


# Property

Direction: It is the point (X,Y,Z) to check

Direction Method : 
Ifc Direction, it use the data of the IFC to get the direction of the object
Bouding Box, it use oriented object bounding box to determine the longest direction of an object.

Angle Difference : The target angle between the two objects.
0 to get parralel objects
90 to get perpendicular objects

Angle Tolerance : In degre, it is use to determine to tolerance of angle in between the two objects.


# Result


# Example
This could be used to check if a window is facing North (or south).
