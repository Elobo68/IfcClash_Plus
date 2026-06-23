import shapely
import shapely.ops
import numpy as np
import numpy.typing as npt
import ifcopenshell.ifcopenshell_wrapper as W
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
from ifcopenshell.util.shape_builder import VectorType
from math import radians, cos
from ifcopenshell.geom import ShapeElementType, ShapeType
from typing import Optional, Literal, Union, Dict, List
from OCC.Core.BRepExtrema import BRepExtrema_DistShapeShape
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCC.Core.gp import gp_Pnt, gp_XYZ
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.TopoDS import TopoDS_Compound, TopoDS_Face
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_FACE
from OCC.Core.BRep import BRep_Tool
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh

AXIS_LITERAL = Literal["X", "Y", "Z"]

VECTOR_3D = tuple[float, float, float]

MatrixType = npt.NDArray[np.float64]
"""`npt.NDArray[np.float64]`"""


def get_extreme_faces(
    geometry: ShapeType,
    axis: AXIS_LITERAL = "Z",
    direction: Optional[VECTOR_3D] = None,
) -> list[VECTOR_3D]:
    
    #For skydome, there is no top because the object. It's not really possible to have a top.
    
    

    from ifcopenshell.util.shape import get_vertices,get_faces


 
    MIN_SURFACE_COVERAGE = 0.99


    if direction is None:
        # By default we will retrieve the top surface
        direction = {"X": (1.0, 0.0, 0.0), "Y": (0.0, 1.0, 0.0), "Z": (0.0, 0.0, 1.0)}[axis]

    vertices = get_vertices(geometry)
    faces = get_faces(geometry)

    # Calculate the triangle normal vectors
    v1 = vertices[faces[:, 1]] - vertices[faces[:, 0]]
    v2 = vertices[faces[:, 2]] - vertices[faces[:, 0]]
    triangle_normals = np.cross(v1, v2)

    # Normalize the normal vectors
    triangle_normals = triangle_normals / np.linalg.norm(triangle_normals, axis=1)[:, np.newaxis]
    direction = np.array(direction) / np.linalg.norm(direction)

    # Find the faces with a normal vector pointing in the desired direction using dot product
    # normal_tol < 0 is pointing away, = 0 is perpendicular, and > 0 is pointing towards.
    normal_tol = 0.1  # Close to perpendicular, but with a fuzz for numerical tolerance, 0.01 for almost no tolerance.
    dot_products = np.dot(triangle_normals, direction)
    filtered_face_indices = np.where(dot_products > normal_tol)[0]
    filtered_faces = faces[filtered_face_indices]

    polygons = [shapely.Polygon(vertices[face]) for face in filtered_faces]
    
    #Find the average height of each face in order to check if it's highest or lowest.
    list_of_z_avg=[]
    for face in filtered_faces:
        Points=vertices[face]
        z_avg=(Points[0][2]+Points[1][2]+Points[2][2])/3
        list_of_z_avg.append(z_avg)

    bottom_faces=[]
    for polygon,z_avg,face in zip(polygons,list_of_z_avg,filtered_faces):
        covered_area=0
        for loop_polygon,loop_z_avg in zip(polygons,list_of_z_avg):
            if polygon==loop_polygon:
                continue


            #This function can be used to find Top or Bottom element.
            if direction[2]==-1:
                if z_avg<loop_z_avg:
                    continue
            if direction[2]==1:
                if z_avg>loop_z_avg:
                    continue

            intersection=polygon.intersection(loop_polygon)
            covering_percent=intersection.area/polygon.area
            covered_area+=covering_percent

        #if the face is totaly recover, it's not a top (or bottom element). 
        if MIN_SURFACE_COVERAGE<covered_area:
            continue


        bottom_faces.append(face)
    
    return bottom_faces


def get_extreme_faces_OpenCascade(
    geometry: ShapeType,
    axis: AXIS_LITERAL = "Z",
    direction: Optional[VECTOR_3D] = None,
) -> list[VECTOR_3D]:
    
    #For skydome, there is no top because the object. It's not really possible to have a top.
    
    

    from ifcopenshell.util.shape import get_vertices,get_faces


 
    MIN_SURFACE_COVERAGE = 0.99


    if direction is None:
        # By default we will retrieve the top surface
        direction = {"X": (1.0, 0.0, 0.0), "Y": (0.0, 1.0, 0.0), "Z": (0.0, 0.0, 1.0)}[axis]

    vertices = get_vertices(geometry)
    faces = get_faces(geometry)

    # Calculate the triangle normal vectors
    v1 = vertices[faces[:, 1]] - vertices[faces[:, 0]]
    v2 = vertices[faces[:, 2]] - vertices[faces[:, 0]]
    triangle_normals = np.cross(v1, v2)

    # Normalize the normal vectors
    triangle_normals = triangle_normals / np.linalg.norm(triangle_normals, axis=1)[:, np.newaxis]
    direction = np.array(direction) / np.linalg.norm(direction)

    # Find the faces with a normal vector pointing in the desired direction using dot product
    # normal_tol < 0 is pointing away, = 0 is perpendicular, and > 0 is pointing towards.
    normal_tol = 0.1  # Close to perpendicular, but with a fuzz for numerical tolerance, 0.01 for almost no tolerance.
    dot_products = np.dot(triangle_normals, direction)
    filtered_face_indices = np.where(dot_products > normal_tol)[0]
    filtered_faces = faces[filtered_face_indices]

    polygons = [shapely.Polygon(vertices[face]) for face in filtered_faces]
    
    #Find the average height of each face in order to check if it's highest or lowest.
    list_of_z_avg=[]
    for face in filtered_faces:
        Points=vertices[face]
        z_avg=(Points[0][2]+Points[1][2]+Points[2][2])/3
        list_of_z_avg.append(z_avg)

    bottom_faces=[]
    for polygon,z_avg,face in zip(polygons,list_of_z_avg,filtered_faces):
        covered_area=0
        for loop_polygon,loop_z_avg in zip(polygons,list_of_z_avg):
            if polygon==loop_polygon:
                continue


            #This function can be used to find Top or Bottom element.
            if direction[2]==-1:
                if z_avg<loop_z_avg:
                    continue
            if direction[2]==1:
                if z_avg>loop_z_avg:
                    continue

            intersection=polygon.intersection(loop_polygon)
            covering_percent=intersection.area/polygon.area
            covered_area+=covering_percent

        #if the face is totaly recover, it's not a top (or bottom element). 
        if MIN_SURFACE_COVERAGE<covered_area:
            continue


        bottom_faces.append(face)
    
    return bottom_faces


def triangle_to_occ_face(triangle):
    """Convertit un triangle en face OpenCASCADE"""
    # Check for invalid input (less than 3 points)
    if not triangle or len(triangle) < 3:
        return None
    
    polygon = BRepBuilderAPI_MakePolygon()
    for point in triangle:
        polygon.Add(gp_Pnt(float(point[0]), float(point[1]), float(point[2])))
    polygon.Close()
    
    if polygon.IsDone():
        face = BRepBuilderAPI_MakeFace(polygon.Wire())
        if face.IsDone():
            return face.Face()
    return None


def get_XYZ_placement(Object):
    Origin = ifcopenshell.util.placement.get_local_placement(
        Object.ObjectPlacement
    )
    Origin = Origin[:, 3][:3]
    Origin = (float(Origin[0]), float(Origin[1]), float(Origin[2]))
    return Origin


def calculate_extreme_faces_surface(
    geometry: ShapeType,
    axis: AXIS_LITERAL = "Z",
    direction: Optional[VECTOR_3D] = None
) -> float:
    """
    Calcule la surface totale des faces extrêmes retournées par get_extreme_faces.

    Args:
        geometry: La géométrie à analyser
        axis: Axe selon lequel trouver les faces extrêmes (X, Y, Z)
        direction: Direction personnalisée (optionnel)

    Returns:
        La surface totale en unités carrées
    """
    from ifcopenshell.util.shape import get_vertices

    extreme_faces = get_extreme_faces(geometry, axis, direction)
    vertices = get_vertices(geometry)

    total_surface = 0.0
    for face in extreme_faces:

        points = vertices[face]
        v1 = points[1] - points[0]
        v2 = points[2] - points[0]
        cross_product = np.cross(v1, v2)
        triangle_area = 0.5 * np.linalg.norm(cross_product)
        total_surface += triangle_area

    print("Total Surface", total_surface)
    return total_surface

def get_extreme_faces_with_area(
    geometry: ShapeType,
    axis: AXIS_LITERAL = "Z",
    direction: Optional[VECTOR_3D] = None,
) -> dict:
    """
    Calcule les faces extrêmes selon une direction donnée et retourne leur surface totale.
    
    Args:
        geometry: La géométrie à analyser (ShapeType de ifcopenshell).
        axis: L'axe selon lequel trouver les faces extrêmes (X, Y, Z).
        direction: Direction personnalisée (optionnel). Si None, utilise la direction positive de l'axe.
    
    Returns:
        Un dictionnaire contenant:
        - extrem_faces: Liste des indices des faces extrêmes.
        - total_area: Surface totale des faces extrêmes (sans recouvrement).
    """
    #@todo Verify this function with complex shape
    from ifcopenshell.util.shape import get_vertices
    
    # Utiliser get_extreme_faces pour obtenir les faces extrêmes
    extrem_faces = get_extreme_faces(geometry, axis, direction)
    
    if len(extrem_faces) == 0:
        return {"extrem_faces": [], "total_area": 0.0}
    
    vertices = get_vertices(geometry)
    
    # Calculer la surface totale des faces extrêmes (surface réelle, sans projection)
    total_area = 0.0
    for face in extrem_faces:
        points = vertices[face]
        v1 = points[1] - points[0]
        v2 = points[2] - points[0]
        cross_product = np.cross(v1, v2)
        triangle_area = 0.5 * np.linalg.norm(cross_product)
        total_area += triangle_area
    
    return {"extrem_faces": extrem_faces, "total_area": total_area}


def calculate_geometry_size_from_3_points(p1, p2, p3):
    """
    Calculate the size (area) of a triangle defined by three points in 3D space.

    Args:
        p1 (tuple[float, float, float]): First point coordinates (x, y, z).
        p2 (tuple[float, float, float]): Second point coordinates (x, y, z).
        p3 (tuple[float, float, float]): Third point coordinates (x, y, z).

    Returns:
        float: The area of the triangle formed by the three points.
    """
    # Convert points to numpy arrays for vector operations
    p1_arr = np.array(p1)
    p2_arr = np.array(p2)
    p3_arr = np.array(p3)

    # Calculate vectors from p1 to p2 and p1 to p3
    v1 = p2_arr - p1_arr
    v2 = p3_arr - p1_arr

    # Calculate the cross product of v1 and v2
    cross_product = np.cross(v1, v2)

    # The area of the triangle is half the magnitude of the cross product
    area = 0.5 * np.linalg.norm(cross_product)

    return area


def clash_bvh_copy_from_CPP(
    bvh_a,
    bvh_b,
    extend: float = 0.0
) -> Dict[int, List[int]]:
    """
    Detects collisions between two BVH trees and returns a dictionary of clashing pairs.
    This function is a Python port of the C++ `clash_bvh` function, designed to work with
    OpenCASCADE BVH trees for efficient collision detection.

    Args:
        bvh_a: The first BVH tree (source).
        bvh_b: The second BVH tree (target).
        extend: Additional tolerance for bounding box expansion (default: 0.0).

    Returns:
        A dictionary where keys are indices from `bvh_a` and values are lists of indices from `bvh_b` that collide.
    """
    bvh_clashes: Dict[int, List[int]] = {}

    # Iterate over all nodes in `bvh_a`
    for i in range(bvh_a.Length()):
        if not bvh_a.IsOuter(i):
            continue  # Skip non-outer nodes

        # Get the bounding box for node `i` in `bvh_a`
        bvh_a_min = bvh_a.MinPoint(i)
        bvh_a_max = bvh_a.MaxPoint(i)

        # Expand the bounding box slightly to avoid numerical issues
        bvh_a_min_expanded = gp_XYZ(
            bvh_a_min.X() - 1e-3,
            bvh_a_min.Y() - 1e-3,
            bvh_a_min.Z() - 1e-3,
        )
        bvh_a_max_expanded = gp_XYZ(
            bvh_a_max.X() + 1e-3,
            bvh_a_max.Y() + 1e-3,
            bvh_a_max.Z() + 1e-3,
        )

        # Create a bounding box for `bvh_a` node `i`
        box_a = Bnd_Box()
        box_a.Add(gp_Pnt(bvh_a_min_expanded))
        box_a.Add(gp_Pnt(bvh_a_max_expanded))

        # Use a stack to traverse `bvh_b` (DFS)
        stack = [0]  # Start from the root of `bvh_b`

        while stack:
            j = stack.pop()

            # Get the bounding box for node `j` in `bvh_b`
            bvh_b_min = bvh_b.MinPoint(j)
            bvh_b_max = bvh_b.MaxPoint(j)

            # Expand the bounding box with `extend` and a small tolerance
            bvh_b_min_expanded = gp_XYZ(
                bvh_b_min.X() - (extend + 1e-3),
                bvh_b_min.Y() - (extend + 1e-3),
                bvh_b_min.Z() - (extend + 1e-3),
            )
            bvh_b_max_expanded = gp_XYZ(
                bvh_b_max.X() + (extend + 1e-3),
                bvh_b_max.Y() + (extend + 1e-3),
                bvh_b_max.Z() + (extend + 1e-3),
            )

            # Create a bounding box for `bvh_b` node `j`
            box_b = Bnd_Box()
            box_b.Add(gp_Pnt(bvh_b_min_expanded))
            box_b.Add(gp_Pnt(bvh_b_max_expanded))

            # Check if `box_a` and `box_b` overlap
            if box_a.IsOut(box_b):
                continue  # No collision, skip

            # If `j` is an outer node, record the collision
            if bvh_b.IsOuter(j):
                if i in bvh_clashes:
                    bvh_clashes[i].append(j)
                else:
                    bvh_clashes[i] = [j]
            else:
                # Push children of `j` onto the stack for further traversal
                stack.append(bvh_b.Child(0, j))
                stack.append(bvh_b.Child(1, j))

    return bvh_clashes

