# Description

This rule aims to detect objects based on their bottom surface area.

It will identify the faces of each selected object that are oriented downward (pointing in the negative Z direction) and are the lowest faces of the geometry. These faces are then combined into a single polygon, and the total area is calculated.

# Property
Source: The objects to be analyzed.

Min: The minimum bottom surface area threshold. Objects with a bottom surface area greater than this value will be considered.

Max: The maximum bottom surface area threshold. Objects with a bottom surface area less than this value will be considered.

# Result

The result will list all objects whose bottom surface area is between the Min and Max values.

# Example

It can be used to detect objects with specific bottom surface characteristics, such as filtering structural elements by their base area.
