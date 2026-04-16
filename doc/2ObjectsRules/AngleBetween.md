# Description

This rule aims to detect pairs of objects based on the angle between their main directions.

It calculates the main direction of each object in a pair using the specified direction method, then measures the angle between these two directions. This allows for identifying object pairs that are aligned at specific angular relationships, such as parallel or perpendicular arrangements.

# Property

Source: The first set of objects to analyze.

Target: The second set of objects to compare against the source.

Direction Method: The method used to determine each object's main direction:
- **Ifc Direction**: Uses the direction data stored in the IFC file for the object
- **Bounding Box**: Uses the oriented bounding box (OBB) to determine the longest dimension of the object

Angle Difference: The target angle between the two objects in degrees:
- **0**: To find parallel objects (aligned in the same direction)
- **90**: To find perpendicular objects (aligned at right angles)
- Any other value: To find objects at that specific angle

Angle Tolerance: The acceptable deviation in degrees from the target Angle Difference. Objects with angles within ±Tolerance of the target angle will be considered matches.

# Result

The result will list all pairs of objects (Source and Target) where the angle between their main directions is within the Angle Tolerance of the specified Angle Difference.

# Example

This rule can be used for various spatial analysis tasks, such as:
- Verify that structural columns are parallel to each other
- Check that beams are perpendicular to walls they connect to
- Identify pairs of elements that should be aligned at specific angles for proper installation
- Detect coordination issues where elements are not oriented as expected relative to each other
