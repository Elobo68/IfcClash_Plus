# Description

This rule aims to detect objects based on their lateral (side) surface area.

It will identify the faces of each selected object that are oriented laterally (on the sides of the object) and are the exterior side faces of the geometry. These faces are then combined into a single polygon, and the total lateral surface area is calculated.

# Property
Source: The objects to be analyzed.

Min: The minimum lateral surface area threshold. Objects with a lateral surface area greater than this value will be considered.

Max: The maximum lateral surface area threshold. Objects with a lateral surface area less than this value will be considered.

# Result

The result will list all objects whose lateral surface area is between the Min and Max values.

# Example

It can be used to detect objects with specific lateral surface characteristics, such as filtering elements by their side surface area.
