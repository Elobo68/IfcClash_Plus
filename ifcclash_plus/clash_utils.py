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
from OCC.Core.BRep import BRep_Builder
from OCC.Core.TopoDS import TopoDS_Compound, TopoDS_Shell, topods
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeSolid, BRepBuilderAPI_Sewing
from OCC.Core.TopAbs import TopAbs_SHELL
import math
from OCC.Core.gp import gp_Ax3, gp_Pnt, gp_Dir, gp_Trsf, gp_XYZ, gp_Vec
from OCC.Core.BRepGProp import BRepGProp_Face
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeEdge
from OCC.Core.TopoDS import TopoDS_Shell, TopoDS_Face
from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepCheck import BRepCheck_Analyzer


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


def faces_to_compound(faces):
    """Toujours valide, même avec une seule face."""
    if not faces:
        return None
    builder = BRep_Builder()
    compound = TopoDS_Compound()
    builder.MakeCompound(compound)
    for face in faces:
        builder.Add(compound, face)
    return compound


def list_of_faces_to_list_of_TopoDS_Face(list_of_faces,vertices):

    list_of_faces=[]
    
    for source_face in list_of_faces:

        s0 = vertices[source_face[0]]
        g0 = gp_Pnt(s0[0],s0[1],s0[2])

        s1 = vertices[source_face[1]]
        g1 = gp_Pnt(s1[0],s1[1],s1[2])

        s2 = vertices[source_face[2]]
        g2 = gp_Pnt(s2[0],s2[1],s2[2])


        edge1 = BRepBuilderAPI_MakeEdge(g0,g1).Edge()
        edge2 = BRepBuilderAPI_MakeEdge(g1, g2).Edge()
        edge3 = BRepBuilderAPI_MakeEdge(g2, g0).Edge()
        wire = BRepBuilderAPI_MakeWire(edge1, edge2, edge3).Wire()
        face = BRepBuilderAPI_MakeFace(wire).Face()
        list_of_faces.append(face)

    return list_of_faces 

def faces_to_shell(faces: list[TopoDS_Face]) -> TopoDS_Shell:
    """
    Construit un TopoDS_Shell à partir d'une liste de TopoDS_Face.

    Args:
        faces: Liste de faces à assembler

    Returns:
        TopoDS_Shell contenant toutes les faces
    """
    builder = BRep_Builder()
    shell = TopoDS_Shell()
    builder.MakeShell(shell)

    for face in faces:
        builder.Add(shell, face)

    return shell

def faces_to_shell_sewed(
    faces: list[TopoDS_Face],
    tolerance: float = 1e-3
) -> TopoDS_Shell:
    """
    Construit un TopoDS_Shell cousu (sewed) à partir d'une liste de TopoDS_Face.
    Le sewing recoud les edges partagées entre faces adjacentes,
    produisant un shell topologiquement propre.

    Args:
        faces:     Liste de faces à assembler
        tolerance: Tolérance de couture (défaut 1e-3)

    Returns:
        TopoDS_Shell cousu
    """
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Sewing
    from OCC.Core.TopoDS import topods

    sewing = BRepBuilderAPI_Sewing(tolerance)

    for face in faces:
        sewing.Add(face)

    sewing.Perform()
    sewed_shape = sewing.SewedShape()

    # Le résultat peut être un Shell, un Compound, ou une Face selon les cas
    from OCC.Core.TopAbs import TopAbs_SHELL, TopAbs_FACE, TopAbs_COMPOUND
    from OCC.Core.TopExp import TopExp_Explorer

    if sewed_shape.ShapeType() == TopAbs_SHELL:
        return topods.Shell(sewed_shape)

    # Si c'est un Compound (faces non connexes), on extrait le premier shell
    # ou on en construit un manuellement
    shell_faces = []
    explorer = TopExp_Explorer(sewed_shape, TopAbs_FACE)  # TopAbs_FACE pas TopAbs_SHELL car faces disjointes
    while explorer.More():
        shell_faces.append(explorer.Current())
        explorer.Next()

    builder = BRep_Builder()
    shell = TopoDS_Shell()
    builder.MakeShell(shell)
    for f in shell_faces:
        builder.Add(shell, f)

    return shell


def check_shell(shell: TopoDS_Shell) -> dict:
    """
    Vérifie la validité du shell et retourne un rapport.
    """
    analyzer = BRepCheck_Analyzer(shell)
    is_valid = analyzer.IsValid()

    from OCC.Core.TopExp import TopExp_Explorer
    from OCC.Core.TopAbs import TopAbs_FACE

    face_count = 0
    explorer = TopExp_Explorer(shell, TopAbs_FACE)
    while explorer.More():
        face_count += 1
        explorer.Next()

    return {
        "is_valid": is_valid,
        "face_count": face_count,
    }

from OCC.Core.TopoDS import TopoDS_Shell
from OCC.Core.ShapeFix import ShapeFix_Shell, ShapeFix_Shape
from OCC.Core.BRepCheck import BRepCheck_Analyzer
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_FACE

from OCC.Core.BRepCheck import BRepCheck_ListIteratorOfListOfStatus
def diagnose_shell(shell: TopoDS_Shell) -> dict:
    from OCC.Core.BRepCheck import (
        BRepCheck_NoError,
        BRepCheck_InvalidPointOnCurve,
        BRepCheck_InvalidPointOnCurveOnSurface,
        BRepCheck_InvalidPointOnSurface,
        BRepCheck_No3DCurve,
        BRepCheck_Multiple3DCurve,
        BRepCheck_Invalid3DCurve,
        BRepCheck_NoCurveOnSurface,
        BRepCheck_InvalidCurveOnSurface,
        BRepCheck_InvalidCurveOnClosedSurface,
        BRepCheck_InvalidSameRangeFlag,
        BRepCheck_InvalidSameParameterFlag,
        BRepCheck_NotClosed,
        BRepCheck_NotConnected,
        BRepCheck_RedundantFace,
    )

    ERROR_LABELS = {
        BRepCheck_NoError: "NoError",
        BRepCheck_InvalidPointOnCurve: "InvalidPointOnCurve",
        BRepCheck_InvalidPointOnCurveOnSurface: "InvalidPointOnCurveOnSurface",
        BRepCheck_InvalidPointOnSurface: "InvalidPointOnSurface",
        BRepCheck_No3DCurve: "No3DCurve",
        BRepCheck_Multiple3DCurve: "Multiple3DCurve",
        BRepCheck_Invalid3DCurve: "Invalid3DCurve",
        BRepCheck_NoCurveOnSurface: "NoCurveOnSurface",
        BRepCheck_InvalidCurveOnSurface: "InvalidCurveOnSurface",
        BRepCheck_InvalidCurveOnClosedSurface: "InvalidCurveOnClosedSurface",
        BRepCheck_InvalidSameRangeFlag: "InvalidSameRangeFlag",
        BRepCheck_InvalidSameParameterFlag: "InvalidSameParameterFlag",
        BRepCheck_NotClosed: "NotClosed",
        BRepCheck_NotConnected: "NotConnected",
        BRepCheck_RedundantFace: "RedundantFace",
    }

    def iter_status(result, shape_label: str) -> list:
        """Itère sur un BRepCheck_Result et retourne les erreurs."""
        if result is None:
            return []
        errors = []
        status_list = result.Status()
        it = BRepCheck_ListIteratorOfListOfStatus(status_list)
        while it.More():
            code = it.Value()
            if code != BRepCheck_NoError:
                label = ERROR_LABELS.get(code, f"Unknown({code})")
                errors.append({"shape": shape_label, "error": label, "code": code})
            it.Next()
        return errors

    analyzer = BRepCheck_Analyzer(shell)
    errors = []

    # Vérification de chaque face
    explorer = TopExp_Explorer(shell, TopAbs_FACE)
    while explorer.More():
        face = explorer.Current()
        errors += iter_status(analyzer.Result(face), "Face")
        explorer.Next()

    # Vérification du shell lui-même
    errors += iter_status(analyzer.Result(shell), "Shell")

    return {
        "is_valid": analyzer.IsValid(),
        "errors": errors,
    }

def repair_shell(
    shell: TopoDS_Shell,
    tolerance: float = 1e-3,
    fix_orientation: bool = True,
) -> TopoDS_Shell:
    """
    Répare un TopoDS_Shell invalide via ShapeFix.

    Corrections appliquées :
      - Réorientation des faces incohérentes
      - Couture des edges libres (free edges)
      - Correction des courbes 3D / pcurves manquantes
      - Correction same-range / same-parameter
      - Suppression des faces redondantes

    Args:
        shell:           Shell à réparer
        tolerance:       Tolérance de réparation
        fix_orientation: Tente de rendre le shell fermé en réorientant les faces

    Returns:
        Shell réparé (nouveau TopoDS_Shell)
    """
    from OCC.Core.TopoDS import topods

    fixer = ShapeFix_Shell(shell)

    fixer.SetPrecision(tolerance)
    fixer.SetMinTolerance(tolerance * 0.01)
    fixer.SetMaxTolerance(tolerance * 10.0)

    # Réorientation des faces dont la normale est incohérente avec le shell
    fixer.SetFixOrientationMode(1 if fix_orientation else 0)

    # Recoud les edges libres restantes
    fixer.SetFixFaceMode(1)

    fixer.Perform()

    result = fixer.Shell()

    explorer = TopExp_Explorer(result, TopAbs_SHELL)
    if explorer.More():
        return topods.Shell(explorer.Current())

    if result.ShapeType() == TopAbs_SHELL:  # ✅ comparaison directe avec la constante
        return topods.Shell(result)

    return shell  # fallback

def get_faces_toward_direction(shape, direction: gp_Dir, angle_threshold_deg=45.0):
    cos_threshold = math.cos(math.radians(angle_threshold_deg))
    ref = gp_Vec(direction.X(), direction.Y(), direction.Z())

    result = []
    explorer = TopExp_Explorer(shape, TopAbs_FACE)

    while explorer.More():
        face = topods.Face(explorer.Current())
        props = BRepGProp_Face(face)

        umin, umax, vmin, vmax = props.Bounds()
        u_mid = (umin + umax) / 2.0
        v_mid = (vmin + vmax) / 2.0

        pnt = gp_Pnt()
        nor = gp_Vec()
        props.Normal(u_mid, v_mid, pnt, nor)

        mag = nor.Magnitude()
        if mag > 1e-10:
            nor.Divide(mag)
            if nor.Dot(ref) > cos_threshold:
                result.append(face)

        explorer.Next()

    # Retourner directement un compound — pas besoin de sewing ni de solid
    return faces_to_compound(result)

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

from OCC.Core.TopoDS import TopoDS_Shape, TopoDS_Face
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_FACE
from OCC.Core.BRep import BRep_Tool
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.GeomAbs import GeomAbs_Plane
from OCC.Core.gp import gp_Dir, gp_Pnt, gp_Lin
from OCC.Core.BRepIntCurveSurface import BRepIntCurveSurface_Inter
from OCC.Core.IntCurveSurface import IntCurveSurface_TransitionOnCurve
from OCC.Core.BRepGProp import brepgprop
from OCC.Core.GProp import GProp_GProps
from OCC.Core.BRepBndLib import brepbndlib
from OCC.Core.Bnd import Bnd_Box


def get_face_normal(face: TopoDS_Face) -> gp_Dir:
    """
    Retourne la normale moyenne d'une face plane.
    Pour les faces non-planes, utilise le centre de la surface.
    """
    surface = BRepAdaptor_Surface(face)

    u_mid = (surface.FirstUParameter() + surface.LastUParameter()) / 2.0
    v_mid = (surface.FirstVParameter() + surface.LastVParameter()) / 2.0

    props = surface.Surface()

    # Calcul de la normale via les dérivées partielles
    from OCC.Core.gp import gp_Vec
    p, du, dv = gp_Pnt(), gp_Vec(), gp_Vec()
    surface.D1(u_mid, v_mid, p, du, dv)

    normal_vec = du.Crossed(dv)
    if normal_vec.Magnitude() < 1e-10:
        return None

    normal_dir = gp_Dir(normal_vec)

    # Inverser si la face est orientée "reversed" dans la shape
    from OCC.Core.TopAbs import TopAbs_REVERSED
    if face.Orientation() == TopAbs_REVERSED:
        normal_dir.Reverse()

    return normal_dir


def get_face_center(face: TopoDS_Face) -> gp_Pnt:
    """Retourne le centre de gravité d'une face."""
    props = GProp_GProps()
    brepgprop.SurfaceProperties(face, props)
    return props.CentreOfMass()


def is_face_oriented_toward_direction(
    face: TopoDS_Face,
    direction: gp_Dir,
    angle_tolerance_deg: float = 45.0
) -> bool:
    """
    Vérifie si une face est orientée dans la direction donnée.
    La normale de la face doit former un angle <= angle_tolerance_deg avec la direction.
    """
    import math
    normal = get_face_normal(face)
    if normal is None:
        return False

    dot = normal.Dot(direction)
    angle_rad = math.acos(max(-1.0, min(1.0, dot)))
    angle_deg = math.degrees(angle_rad)

    return angle_deg <= angle_tolerance_deg


def is_face_visible(
    face: TopoDS_Face,
    shape: TopoDS_Shape,
    direction: gp_Dir,
    n_samples: int = 5
) -> bool:
    from OCC.Core.gp import gp_Vec

    OFFSET = 1e-3

    surface = BRepAdaptor_Surface(face)
    u_min = surface.FirstUParameter()
    u_max = surface.LastUParameter()
    v_min = surface.FirstVParameter()
    v_max = surface.LastVParameter()

    sample_params = []
    for i in range(n_samples):
        for j in range(n_samples):
            u = u_min + (u_max - u_min) * (i + 0.5) / n_samples
            v = v_min + (v_max - v_min) * (j + 0.5) / n_samples
            sample_params.append((u, v))

    visible_count = 0

    for u, v in sample_params:
        p = gp_Pnt()
        du, dv = gp_Vec(), gp_Vec()
        surface.D1(u, v, p, du, dv)

        origin = gp_Pnt(
            p.X() + direction.X() * OFFSET,
            p.Y() + direction.Y() * OFFSET,
            p.Z() + direction.Z() * OFFSET,
        )

        ray = gp_Lin(origin, direction)

        inter = BRepIntCurveSurface_Inter()
        inter.Init(shape, ray, 1e-7)

        hit_other_face = False
        while inter.More():
            t = inter.W()
            if t > OFFSET:
                hit_face = inter.Face()
                if not hit_face.IsSame(face):
                    hit_other_face = True
                    break
            inter.Next()

        if not hit_other_face:
            visible_count += 1

    return visible_count > (n_samples * n_samples) / 2

def get_visible_faces_in_direction(
    shape: TopoDS_Shape,
    direction: gp_Dir,
    angle_tolerance_deg: float = 45.0,
    n_ray_samples: int = 3,
) -> list[TopoDS_Face]:
    """
    Retourne la liste des faces du TopoDS_Shape qui sont :
      1. Orientées dans la direction donnée (normale alignée avec direction)
      2. Non occultées par d'autres faces de la géométrie

    Args:
        shape:               La géométrie d'entrée
        direction:           Direction de vue (gp_Dir)
        angle_tolerance_deg: Tolérance angulaire entre la normale et la direction (défaut 45°)
        n_ray_samples:       Nombre de subdivisions par axe pour le lancer de rayons (défaut 3 → 9 rayons)

    Returns:
        Liste de TopoDS_Face visibles dans la direction.
    """
    candidate_faces = []

    # Étape 1 : Explorer toutes les faces et filtrer par orientation
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    while explorer.More():
        face = explorer.Current()
        if is_face_oriented_toward_direction(face, direction, angle_tolerance_deg):
            candidate_faces.append(face)
        explorer.Next()

    # Étape 2 : Parmi les candidats, ne garder que les faces non occultées
    visible_faces = []
    for face in candidate_faces:
        if is_face_visible(face, shape, direction, n_samples=n_ray_samples):
            visible_faces.append(face)

    return visible_faces

def min_distance_two_faces(ListPoint1, ListPoint2):
    face1 = triangle_to_occ_face(ListPoint1)
    face2 = triangle_to_occ_face(ListPoint2)
    
    if face1 is None or face2 is None:
        raise ValueError("Not possible to create face")
    
    dist_calc = BRepExtrema_DistShapeShape(face1, face2)
    
    if dist_calc.IsDone():
        point1 = dist_calc.PointOnShape1(1)
        point2 = dist_calc.PointOnShape2(1)
        
        return {
            'distance': dist_calc.Value(),
            'point1': [point1.X(), point1.Y(), point1.Z()],
            'point2': [point2.X(), point2.Y(), point2.Z()]
        }
    
    raise RuntimeError("Fail to calculate distance")

# ── Exemple d'utilisation ────────────────────────────────────────────────────

if __name__ == "__main__":
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
    from OCC.Core.gp import gp_Dir

    # Création d'une boîte de test
    box = BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape()

    # Direction : on cherche les faces visibles depuis le dessus (+Z)
    direction = gp_Dir(0.0, 0.0, 1.0)

    faces = get_visible_faces_in_direction(
        shape=box,
        direction=direction,
        angle_tolerance_deg=45.0,
        n_ray_samples=3,
    )

    print(f"Faces visibles dans la direction {direction.X(), direction.Y(), direction.Z()} : {len(faces)}")
    for i, f in enumerate(faces):
        center = get_face_center(f)
        normal = get_face_normal(f)
        print(f"  Face {i}: centre=({center.X():.2f}, {center.Y():.2f}, {center.Z():.2f}), "
              f"normale=({normal.X():.2f}, {normal.Y():.2f}, {normal.Z():.2f})")