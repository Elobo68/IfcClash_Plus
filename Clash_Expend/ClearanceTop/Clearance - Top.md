---
Synthese: Permet de vérifier si rien n'est au dessus d'un objet
2 Objects Rules: true
Must X: true
IsRule: true
Priority: 1
---
# Description

This rule aims to detect objects that are on top of each other. 

It will first detect, on each object, the face that will be anaylzed.
- All faces must point to the top, or bottom.
- The faces must be the highest, or lower, point of the geometry.
	- The faces of an holes point to the top but aren't the highest point of the geometry.



The rule will detect the two faces of the object. Those two faces will be analyze in order to detect if they are in or out.


[Clash_Top.jpg]


# Property
A: Object A
B: Object B
Type: 
- MinToMax: The lower part of A will be collided with the highest part of B.
- MinToMin : The lower part of A will be collided with the lowest part of B.
- MaxToMin : The highest part of A will be collided with the lowest part of B.
- MaxToMax : The highest part of A will be collided with the highest part of B.
Min : If the faces of object B is higher than min, it will raise a clash.
Max : if the faces of object B is lower than Max, it will raise a clash.
Lateral_Tolerance: 
By default 0, the lateral tolerance aims to detect that the B object may be offset. 

If the value is negative, it can enforce that the B object is under A object.


# Result



# Example

