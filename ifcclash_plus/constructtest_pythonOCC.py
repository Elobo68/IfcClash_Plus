"""
Module pour tester la détection d'occlusion et la position relative de faces 3D avec PythonOCC.

Fonctions principales :
- get_faces_toward_direction : obtient les faces orientées vers une direction
- is_face_occluded : vérifie si une face est masquée (version rapide avec boîtes englobantes)
- is_face_occluded_precise : vérifie si une face est masquée (version précise avec projection 2D)
- is_face_below : vérifie si une face est en dessous d'une autre selon un axe donné
- is_face_below_any : vérifie si une face est en dessous de n'importe quelle autre face d'une liste

Fonctions helpers :
- get_box_corners : retourne les 8 coins d'une boîte englobante
- project_on_axis : projette des points sur un axe
- project_on_plane : projette des points sur un plan perpendiculaire à un axe
- rectangles_overlap : vérifie si deux rectangles 2D se chevauchent
"""

import numpy as np
import numpy.typing as npt
import math
from math import radians, cos
from typing import Optional, Literal, Union, Dict, List, Tuple

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.ifcopenshell_wrapper as W
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
from ifcopenshell.util.shape_builder import VectorType
from ifcopenshell.geom import ShapeElementType, ShapeType

import multiprocessing
import trimesh
import shapely
import shapely.ops

# Imports OCC
from OCC.Core.BRep import BRep_Builder, BRep_Tool
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakePolygon, 
    BRepBuilderAPI_MakeFace, 
    BRepBuilderAPI_Sewing,
    BRepBuilderAPI_MakeSolid,
    BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_MakeEdge
)
from OCC.Core.BRepBndLib import brepbndlib
from OCC.Core.BRepExtrema import BRepExtrema_DistShapeShape
from OCC.Core.BRepGProp import BRepGProp_Face
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.BRepCheck import BRepCheck_Analyzer
from OCC.Core.gp import gp_Pnt, gp_XYZ, gp_Ax3, gp_Dir, gp_Trsf, gp_Vec
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.TopoDS import TopoDS_Compound, TopoDS_Face, TopoDS_Shell, topods
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_FACE, TopAbs_SHELL
from OCC.Core.AIS import AIS_Shape
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Display.SimpleGui import init_display


def get_box_corners(box: Bnd_Box) -> List[gp_Pnt]:
    """
    Retourne les 8 coins d'une boîte englobante.
    
    Args:
        box: Bnd_Box - la boîte englobante
        
    Returns:
        List[gp_Pnt]: Liste des 8 points des coins
    """
    corners = []
    min_p = box.CornerMin()
    max_p = box.CornerMax()
    for dx in [min_p.X(), max_p.X()]:
        for dy in [min_p.Y(), max_p.Y()]:
            for dz in [min_p.Z(), max_p.Z()]:
                corners.append(gp_Pnt(dx, dy, dz))
    return corners


def project_on_axis(points: List[gp_Pnt], axis: gp_Dir) -> Tuple[float, float]:
    """
    Projette des points sur un axe, retourne (min, max) des projections.
    
    Args:
        points: Liste de points à projeter
        axis: Direction de l'axe de projection
        
    Returns:
        Tuple[float, float]: (valeur minimale, valeur maximale) des projections
    """
    axis_vec = gp_Vec(axis.X(), axis.Y(), axis.Z())
    projections = [gp_Vec(p.X(), p.Y(), p.Z()).Dot(axis_vec) for p in points]
    return min(projections), max(projections)


def rectangles_overlap(rect1, rect2) -> bool:
    """
    Vérifie si deux rectangles axis-aligned se chevauchent.
    
    Args:
        rect1: Tuple (min_x, max_x, min_y, max_y)
        rect2: Tuple (min_x, max_x, min_y, max_y)
        
    Returns:
        bool: True si les rectangles se chevauchent
    """
    return not (rect1[1] < rect2[0] or rect2[1] < rect1[0] or
                rect1[3] < rect2[2] or rect2[3] < rect1[2])


def project_on_plane(points: List[gp_Pnt], axis: gp_Dir, origin: gp_Pnt = None) -> Tuple[List[Tuple[float, float]], gp_Vec, gp_Vec]:
    """
    Projette des points sur le plan perpendiculaire à axis.
    
    Args:
        points: Liste de points à projeter
        axis: Direction de l'axe normal au plan
        origin: Point d'origine pour la projection (default: (0,0,0))
        
    Returns:
        Tuple: (liste de coordonnées 2D (x,y), vecteur base X, vecteur base Y)
    """
    axis_vec = gp_Vec(axis.X(), axis.Y(), axis.Z())
    
    # Trouver un vecteur perpendiculaire à axis
    if abs(axis_vec.X()) < 0.5:
        base_x = gp_Vec(1, 0, 0)
    else:
        base_x = gp_Vec(0, 1, 0)
    
    # Orthogonaliser base_x par rapport à axis
    dot_x_view = base_x.Dot(axis_vec)
    view_squared = axis_vec.Dot(axis_vec)
    if view_squared > 1e-10:
        factor = dot_x_view / view_squared
        axis_scaled = gp_Vec(axis_vec.X() * factor, axis_vec.Y() * factor, axis_vec.Z() * factor)
        base_x.Subtract(axis_scaled)
    
    # Normaliser base_x
    base_x_mag = base_x.Magnitude()
    if base_x_mag > 1e-10:
        base_x.Divide(base_x_mag)
    
    # base_y = axis × base_x
    base_y = axis_vec.Crossed(base_x)
    base_y_mag = base_y.Magnitude()
    if base_y_mag > 1e-10:
        base_y.Divide(base_y_mag)
    
    # Projeter les points
    if origin is None:
        origin = gp_Pnt(0, 0, 0)
    
    coords_2d = []
    for p in points:
        vec = gp_Vec(p.X() - origin.X(), p.Y() - origin.Y(), p.Z() - origin.Z())
        x = vec.Dot(base_x)
        y = vec.Dot(base_y)
        coords_2d.append((x, y))
    
    return coords_2d, base_x, base_y


def is_face_below(face: TopoDS_Face, other_face: TopoDS_Face, axis: gp_Dir, tolerance: float = 1e-6) -> bool:
    """
    Détermine si face est en dessous de other_face selon l'axe donné,
    avec chevauchement des projections sur le plan perpendiculaire.
    
    Une face est considérée comme "en dessous" si (Option C) :
    1. Leurs projections sur le plan perpendiculaire à l'axe se chevauchent
    2. Le centre de face est en dessous du centre de other_face selon l'axe
    
    Args:
        face: TopoDS_Face - la face candidate à être en dessous
        other_face: TopoDS_Face - la face de référence
        axis: gp_Dir - l'axe selon lequel vérifier (ex: gp_Dir(0,0,1) pour Z)
        tolerance: Tolérance numérique pour les comparaisons
        
    Returns:
        bool: True si face est en dessous de other_face selon axis avec chevauchement
    """
    # Éviter la comparaison avec soi-même
    if face.IsSame(other_face):
        return False
    
    # Calculer les boîtes englobantes
    face_box = Bnd_Box()
    brepbndlib.Add(face, face_box)
    other_box = Bnd_Box()
    brepbndlib.Add(other_face, other_box)
    
    # Obtenir tous les 8 coins
    face_corners = get_box_corners(face_box)
    other_corners = get_box_corners(other_box)
    
    # Calculer les centres pour la comparaison sur l'axe
    face_center = gp_Pnt(
        (face_box.CornerMin().X() + face_box.CornerMax().X()) / 2.0,
        (face_box.CornerMin().Y() + face_box.CornerMax().Y()) / 2.0,
        (face_box.CornerMin().Z() + face_box.CornerMax().Z()) / 2.0
    )
    other_center = gp_Pnt(
        (other_box.CornerMin().X() + other_box.CornerMax().X()) / 2.0,
        (other_box.CornerMin().Y() + other_box.CornerMax().Y()) / 2.0,
        (other_box.CornerMin().Z() + other_box.CornerMax().Z()) / 2.0
    )
    
    # Projeter les centres sur l'axe
    axis_vec = gp_Vec(axis.X(), axis.Y(), axis.Z())
    face_center_proj = gp_Vec(face_center.X(), face_center.Y(), face_center.Z()).Dot(axis_vec)
    other_center_proj = gp_Vec(other_center.X(), other_center.Y(), other_center.Z()).Dot(axis_vec)
    
    # Vérifier la relation "en dessous" : centre de face < centre de other_face sur l'axe
    if face_center_proj >= other_center_proj - tolerance:
        return False
    
    # Projeter sur le plan perpendiculaire à l'axe
    # Utiliser face_center comme origine
    face_2d, base_x, base_y = project_on_plane(face_corners, axis, face_center)
    other_2d, _, _ = project_on_plane(other_corners, axis, face_center)
    
    # Calculer les boîtes englobantes 2D
    face_rect = (
        min(p[0] for p in face_2d),
        max(p[0] for p in face_2d),
        min(p[1] for p in face_2d),
        max(p[1] for p in face_2d)
    )
    other_rect = (
        min(p[0] for p in other_2d),
        max(p[0] for p in other_2d),
        min(p[1] for p in other_2d),
        max(p[1] for p in other_2d)
    )
    
    # Vérifier le chevauchement 2D
    return rectangles_overlap(face_rect, other_rect)


def is_face_below_any(face: TopoDS_Face, other_faces: List[TopoDS_Face], axis: gp_Dir, tolerance: float = 1e-6) -> bool:
    """
    Vérifie si face est en dessous de n'importe quelle autre face dans other_faces
    selon l'axe donné, avec chevauchement des projections.
    
    Les faces doivent appartenir au même objet (c'est la responsabilité de l'appelant
    de passer uniquement des faces du même objet).
    
    Args:
        face: TopoDS_Face - la face à tester
        other_faces: List[TopoDS_Face] - liste des autres faces (du même objet)
        axis: gp_Dir - l'axe selon lequel vérifier (peut être n'importe quelle direction)
        tolerance: Tolérance numérique pour les comparaisons
        
    Returns:
        bool: True si face est en dessous d'au moins une face dans other_faces
    """
    for other_face in other_faces:
        if is_face_below(face, other_face, axis, tolerance):
            return True
    return False


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
    return result


def is_face_occluded(face, potential_occluders, direction: gp_Dir, angle_threshold_deg=45.0):
    """
    Vérifie si une face est masquée par une autre face selon une direction de vue.
    
    Une face est considérée comme masquée si une autre face (orientée vers la direction)
    se trouve entre elle et le point de vue, et que leurs projections sur un plan 
    perpendiculaire à la direction se chevauchent.
    
    Args:
        face: TopoDS_Face - la face à tester
        potential_occluders: list[TopoDS_Face] - liste des faces potentielles qui pourraient masquer
        direction: gp_Dir - direction de vue (depuis la caméra vers la scène)
        angle_threshold_deg: angle seuil pour considérer une face comme orientée vers la direction
    
    Returns:
        bool: True si la face est masquée par au moins une face dans potential_occluders
    """
    if not potential_occluders:
        return False
        
    cos_threshold = math.cos(math.radians(angle_threshold_deg))
    view_dir = gp_Vec(direction.X(), direction.Y(), direction.Z())
    
    # Obtenir les propriétés de la face à tester
    face_props = BRepGProp_Face(face)
    umin, umax, vmin, vmax = face_props.Bounds()
    test_pnt = gp_Pnt()
    test_nor = gp_Vec()
    face_props.Normal((umin+umax)/2, (vmin+vmax)/2, test_pnt, test_nor)
    
    # Normaliser la normale
    test_nor_mag = test_nor.Magnitude()
    if test_nor_mag > 1e-10:
        test_nor.Divide(test_nor_mag)
    
    # Calculer la boîte englobante de la face à tester
    test_box = Bnd_Box()
    brepbndlib.Add(face, test_box)
    
    # Obtenir le centre de la boîte pour calculer la distance
    test_corner_min = test_box.CornerMin()
    test_corner_max = test_box.CornerMax()
    test_center = gp_Pnt(
        (test_corner_min.X() + test_corner_max.X()) / 2.0,
        (test_corner_min.Y() + test_corner_max.Y()) / 2.0,
        (test_corner_min.Z() + test_corner_max.Z()) / 2.0
    )
    test_center_vec = gp_Vec(test_center.X(), test_center.Y(), test_center.Z())
    
    # Distance de la face testée par rapport à la direction (projection sur l'axe de vue)
    test_dist = test_center_vec.Dot(view_dir)
    
    for occluder in potential_occluders:
        # Éviter de comparer avec la même face
        if face.IsSame(occluder):
            continue
            
        # Obtenir les propriétés de la face candidate
        occ_props = BRepGProp_Face(occluder)
        o_umin, o_umax, o_vmin, o_vmax = occ_props.Bounds()
        occ_pnt = gp_Pnt()
        occ_nor = gp_Vec()
        occ_props.Normal((o_umin+o_umax)/2, (o_vmin+o_vmax)/2, occ_pnt, occ_nor)
        
        # Normaliser la normale
        occ_nor_mag = occ_nor.Magnitude()
        if occ_nor_mag > 1e-10:
            occ_nor.Divide(occ_nor_mag)
        
        # Vérifier l'orientation : la face candidate doit être orientée vers la direction
        if occ_nor.Dot(view_dir) <= cos_threshold:
            continue
        
        # Calculer la boîte englobante de la face candidate
        occ_box = Bnd_Box()
        brepbndlib.Add(occluder, occ_box)
        
        # Obtenir le centre de la boîte de la face candidate
        occ_corner_min = occ_box.CornerMin()
        occ_corner_max = occ_box.CornerMax()
        occ_center = gp_Pnt(
            (occ_corner_min.X() + occ_corner_max.X()) / 2.0,
            (occ_corner_min.Y() + occ_corner_max.Y()) / 2.0,
            (occ_corner_min.Z() + occ_corner_max.Z()) / 2.0
        )
        occ_center_vec = gp_Vec(occ_center.X(), occ_center.Y(), occ_center.Z())
        
        # Distance de la face candidate par rapport à la direction
        occ_dist = occ_center_vec.Dot(view_dir)
        
        # La face candidate doit être plus proche de la caméra (devant la face testée)
        # Dans notre système de coordonnées, si on regarde dans la direction D,
        # les objets avec une distance plus petite sont plus proches
        if occ_dist >= test_dist:
            continue
        
        # Vérifier si les boîtes englobantes se chevauchent (test d'occlusion grossier)
        # Utiliser tous les 8 coins pour un test plus précis
        if test_box.IsOut(occ_box):
            continue
        
        # Test plus précis : vérifier que les projections sur le plan perpendiculaire à la direction
        # se chevauchent en utilisant TOUS les coins des boîtes
        test_corners = get_box_corners(test_box)
        occ_corners = get_box_corners(occ_box)
        
        # Projeter sur le plan perpendiculaire à la direction
        test_2d, base_x, base_y = project_on_plane(test_corners, direction, test_center)
        occ_2d, _, _ = project_on_plane(occ_corners, direction, test_center)
        
        # Calculer les boîtes englobantes 2D
        test_rect = (
            min(p[0] for p in test_2d),
            max(p[0] for p in test_2d),
            min(p[1] for p in test_2d),
            max(p[1] for p in test_2d)
        )
        occ_rect = (
            min(p[0] for p in occ_2d),
            max(p[0] for p in occ_2d),
            min(p[1] for p in occ_2d),
            max(p[1] for p in occ_2d)
        )
        
        # Vérifier le chevauchement 2D
        if not rectangles_overlap(test_rect, occ_rect):
            continue
        
        # Les projections 2D se chevauchent et l'occuldeur est devant, donc il y a occlusion
        return True
    
    return False


def is_face_occluded_precise(face, potential_occluders, direction: gp_Dir, angle_threshold_deg=45.0):
    """
    Vérifie si une face est masquée par une autre face selon une direction de vue,
    avec un test de projection 2D précis.
    
    Cette version est plus précise que is_face_occluded car elle vérifie l'intersection
    des projections 2D des faces sur un plan perpendiculaire à la direction de vue.
    
    Args:
        face: TopoDS_Face - la face à tester
        potential_occluders: list[TopoDS_Face] - liste des faces potentielles qui pourraient masquer
        direction: gp_Dir - direction de vue (depuis la caméra vers la scène)
        angle_threshold_deg: angle seuil pour considérer une face comme orientée vers la direction
    
    Returns:
        bool: True si la face est masquée par au moins une face dans potential_occluders
    """
    if not potential_occluders:
        return False
        
    cos_threshold = math.cos(math.radians(angle_threshold_deg))
    view_dir = gp_Vec(direction.X(), direction.Y(), direction.Z())
    
    # Obtenir les propriétés de la face à tester
    face_props = BRepGProp_Face(face)
    umin, umax, vmin, vmax = face_props.Bounds()
    test_pnt = gp_Pnt()
    test_nor = gp_Vec()
    face_props.Normal((umin+umax)/2, (vmin+vmax)/2, test_pnt, test_nor)
    
    # Normaliser la normale
    test_nor_mag = test_nor.Magnitude()
    if test_nor_mag > 1e-10:
        test_nor.Divide(test_nor_mag)
    
    # Calculer la boîte englobante de la face à tester
    test_box = Bnd_Box()
    brepbndlib.Add(face, test_box)
    
    # Obtenir le centre de la boîte pour calculer la distance
    test_corner_min = test_box.CornerMin()
    test_corner_max = test_box.CornerMax()
    test_center = gp_Pnt(
        (test_corner_min.X() + test_corner_max.X()) / 2.0,
        (test_corner_min.Y() + test_corner_max.Y()) / 2.0,
        (test_corner_min.Z() + test_corner_max.Z()) / 2.0
    )
    test_center_vec = gp_Vec(test_center.X(), test_center.Y(), test_center.Z())
    test_dist = test_center_vec.Dot(view_dir)
    
    # Créer un système de coordonnées local pour la projection 2D
    # L'axe Z est la direction de vue
    # Les axes X et Y forment un plan perpendiculaire
    # Trouver un axe X perpendiculaire à la direction
    if abs(view_dir.X()) > abs(view_dir.Y()):
        # Direction est proche de X, donc on prend Y comme axe X local
        local_x = gp_Vec(0, 1, 0)
    else:
        # Direction est proche de Y ou Z, donc on prend X comme axe X local
        local_x = gp_Vec(1, 0, 0)
    
    # Orthogonaliser local_x par rapport à view_dir
    # local_x = local_x - (local_x.Dot(view_dir) / view_dir.Dot(view_dir)) * view_dir
    dot_x_view = local_x.Dot(view_dir)
    view_squared = view_dir.Dot(view_dir)
    if view_squared > 1e-10:
        # Calculer la composante à soustraire
        factor = dot_x_view / view_squared
        view_dir_scaled = gp_Vec(view_dir.X() * factor, view_dir.Y() * factor, view_dir.Z() * factor)
        local_x.Subtract(view_dir_scaled)
    
    # Normaliser local_x
    local_x_mag = local_x.Magnitude()
    if local_x_mag > 1e-10:
        local_x.Divide(local_x_mag)
    
    # local_y = view_dir Cross local_x
    local_y = view_dir.Crossed(local_x)
    local_y_mag = local_y.Magnitude()
    if local_y_mag > 1e-10:
        local_y.Divide(local_y_mag)
    
    for occluder in potential_occluders:
        # Éviter de comparer avec la même face
        if face.IsSame(occluder):
            continue
            
        # Obtenir les propriétés de la face candidate
        occ_props = BRepGProp_Face(occluder)
        o_umin, o_umax, o_vmin, o_vmax = occ_props.Bounds()
        occ_pnt = gp_Pnt()
        occ_nor = gp_Vec()
        occ_props.Normal((o_umin+o_umax)/2, (o_vmin+o_vmax)/2, occ_pnt, occ_nor)
        
        # Normaliser la normale
        occ_nor_mag = occ_nor.Magnitude()
        if occ_nor_mag > 1e-10:
            occ_nor.Divide(occ_nor_mag)
        
        # Vérifier l'orientation
        if occ_nor.Dot(view_dir) <= cos_threshold:
            continue
        
        # Calculer la boîte englobante de la face candidate
        occ_box = Bnd_Box()
        brepbndlib.Add(occluder, occ_box)
        
        # Obtenir le centre de la boîte de la face candidate
        occ_corner_min = occ_box.CornerMin()
        occ_corner_max = occ_box.CornerMax()
        occ_center = gp_Pnt(
            (occ_corner_min.X() + occ_corner_max.X()) / 2.0,
            (occ_corner_min.Y() + occ_corner_max.Y()) / 2.0,
            (occ_corner_min.Z() + occ_corner_max.Z()) / 2.0
        )
        occ_center_vec = gp_Vec(occ_center.X(), occ_center.Y(), occ_center.Z())
        occ_dist = occ_center_vec.Dot(view_dir)
        
        # La face candidate doit être plus proche de la caméra
        if occ_dist >= test_dist:
            continue
        
        # Vérifier si les boîtes englobantes se chevauchent (test rapide)
        if test_box.IsOut(occ_box):
            continue
        
        # Projeter TOUS les coins des boîtes sur le plan 2D (local_x, local_y)
        # Pour la face testée
        test_corners = get_box_corners(test_box)
        occ_corners = get_box_corners(occ_box)
        
        # Projeter les coins sur le plan 2D
        test_2d = []
        for corner in test_corners:
            vec = gp_Vec(corner.X(), corner.Y(), corner.Z())
            vec.Subtract(gp_Vec(test_center.X(), test_center.Y(), test_center.Z()))
            proj_x = vec.Dot(local_x)
            proj_y = vec.Dot(local_y)
            test_2d.append((proj_x, proj_y))
        
        # Pour la face candidate
        occ_2d = []
        for corner in occ_corners:
            vec = gp_Vec(corner.X(), corner.Y(), corner.Z())
            vec.Subtract(gp_Vec(test_center.X(), test_center.Y(), test_center.Z()))
            proj_x = vec.Dot(local_x)
            proj_y = vec.Dot(local_y)
            occ_2d.append((proj_x, proj_y))
        
        # Calculer les boîtes englobantes 2D
        test_rect = (
            min(p[0] for p in test_2d),
            max(p[0] for p in test_2d),
            min(p[1] for p in test_2d),
            max(p[1] for p in test_2d)
        )
        occ_rect = (
            min(p[0] for p in occ_2d),
            max(p[0] for p in occ_2d),
            min(p[1] for p in occ_2d),
            max(p[1] for p in occ_2d)
        )
        
        # Vérifier si les rectangles 2D se chevauchent
        if not rectangles_overlap(test_rect, occ_rect):
            continue
        
        # Les projections 2D se chevauchent, donc il y a occlusion
        return True
    
    return False



def add_to_display(display,geom):
    ais_shape=AIS_Shape(geom)
    ais_shape.SetTransparency(0.2)
    display.Context.Display(ais_shape, True)
    return display

def add_to_display_green(display,geom):
    ais_shape=AIS_Shape(geom)
    green_color = Quantity_Color(0.0, 1.0, 0.0, Quantity_TOC_RGB)
    ais_shape.SetColor(green_color)
    ais_shape.SetTransparency(0.2)
    display.Context.Display(ais_shape, True)
    return display

def add_to_display_red(display,geom):
    """Affiche une géométrie en rouge pour les faces masquées"""
    ais_shape=AIS_Shape(geom)
    red_color = Quantity_Color(1.0, 0.0, 0.0, Quantity_TOC_RGB)
    ais_shape.SetColor(red_color)
    ais_shape.SetTransparency(0.5)
    display.Context.Display(ais_shape, True)
    return display

def add_to_display_yellow(display,geom):
    """Affiche une géométrie en rouge pour les faces masquées"""
    ais_shape=AIS_Shape(geom)
    red_color = Quantity_Color(1.0, 1.0, 0.0, Quantity_TOC_RGB)
    ais_shape.SetColor(red_color)
    ais_shape.SetTransparency(0.9)
    display.Context.Display(ais_shape, True)
    return display


if __name__ == "__main__":
    Chemin="/home/jocelin/Documents/200 - IFC/IfcSampleFiles-main/Ifc2x3_Duplex_Architecture.ifc"
    file=ifcopenshell.open(Chemin)

    objects=file.by_type("IfcFurnishingElement")
    the_settings=ifcopenshell.geom.settings()
    the_settings.set("use-python-opencascade", True)
    iterator = ifcopenshell.geom.iterator(
                the_settings,
                file,
                multiprocessing.cpu_count(),
                include=objects,
            )


    display, start_display, add_menu, add_function = init_display()
    
    # Liste pour stocker toutes les faces visibles (orientées vers la direction)
    
    direction_to_check=gp_Dir(0.0, 0.0, 1.0)
    
    if iterator.initialize():
        # Première passe : collecter toutes les faces visibles
        while True:
            shape = iterator.get()
            geom = shape.geometry
            entity = file.by_id(shape.data.id)

            display = add_to_display_yellow(display, geom)

            List_of_faces = get_faces_toward_direction(geom,direction_to_check)


            for oneface in List_of_faces:
                # Utiliser la nouvelle fonction pour détecter les faces en dessous
                # selon l'axe Z (direction_to_check = (0,0,1))
                if is_face_below_any(oneface, List_of_faces, direction_to_check):
                    display = add_to_display_red(display, oneface)
                else:
                    display = add_to_display_green(display, oneface)



            if not iterator.next():
                break

    display.FitAll()
    start_display()