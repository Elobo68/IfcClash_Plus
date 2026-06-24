"""
Module pour tester la détection d'occlusion de faces 3D avec PythonOCC.

Fonctions principales :
- get_faces_toward_direction : obtient les faces orientées vers une direction
- is_face_occluded : vérifie si une face est masquée (version rapide avec boîtes englobantes)
- is_face_occluded_precise : vérifie si une face est masquée (version précise avec projection 2D)
"""

import numpy as np
import numpy.typing as npt
import math
from math import radians, cos
from typing import Optional, Literal, Union, Dict, List

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
        # les objets avec une distance plus petite (plus négative) sont plus proches
        if occ_dist >= test_dist:
            continue
        
        # Vérifier si les boîtes englobantes se chevauchent (test d'occlusion grossier)
        # Si les boîtes ne se chevauchent pas, il n'y a pas d'occlusion
        if test_box.IsOut(occ_box):
            continue
        
        # Test plus précis : vérifier que les projections sur le plan perpendiculaire à la direction
        # se chevauchent. On utilise une approximation avec les boîtes.
        # 
        # Pour simplifier, on considère que si les boîtes 3D se chevauchent et que la face candidate
        # est devant, alors il y a occlusion. C'est une approximation conservative.
        # Pour un test plus précis, on pourrait projeter les faces sur un plan 2D.
        
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
        
        # Projeter les coins des boîtes sur le plan 2D (local_x, local_y)
        # Pour la face testée
        test_2d_min_x = float('inf')
        test_2d_max_x = float('-inf')
        test_2d_min_y = float('inf')
        test_2d_max_y = float('-inf')
        
        for corner in [test_corner_min, test_corner_max]:
            vec = gp_Vec(corner.X(), corner.Y(), corner.Z())
            # Soustraire l'origine (on utilise test_center comme origine)
            vec.Subtract(gp_Vec(test_center.X(), test_center.Y(), test_center.Z()))
            proj_x = vec.Dot(local_x)
            proj_y = vec.Dot(local_y)
            test_2d_min_x = min(test_2d_min_x, proj_x)
            test_2d_max_x = max(test_2d_max_x, proj_x)
            test_2d_min_y = min(test_2d_min_y, proj_y)
            test_2d_max_y = max(test_2d_max_y, proj_y)
        
        # Pour la face candidate
        occ_2d_min_x = float('inf')
        occ_2d_max_x = float('-inf')
        occ_2d_min_y = float('inf')
        occ_2d_max_y = float('-inf')
        
        for corner in [occ_corner_min, occ_corner_max]:
            vec = gp_Vec(corner.X(), corner.Y(), corner.Z())
            # Soustraire la même origine pour avoir des coordonnées comparables
            vec.Subtract(gp_Vec(test_center.X(), test_center.Y(), test_center.Z()))
            proj_x = vec.Dot(local_x)
            proj_y = vec.Dot(local_y)
            occ_2d_min_x = min(occ_2d_min_x, proj_x)
            occ_2d_max_x = max(occ_2d_max_x, proj_x)
            occ_2d_min_y = min(occ_2d_min_y, proj_y)
            occ_2d_max_y = max(occ_2d_max_y, proj_y)
        
        # Vérifier si les rectangles 2D se chevauchent
        if (test_2d_max_x < occ_2d_min_x or occ_2d_max_x < test_2d_min_x or
            test_2d_max_y < occ_2d_min_y or occ_2d_max_y < test_2d_min_y):
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
    ais_shape.SetTransparency(0.5)
    display.Context.Display(ais_shape, True)
    return display


if __name__ == "__main__":
    Chemin="/home/jocelin/Documents/200 - IFC/IfcSampleFiles-main/Ifc2x3_Duplex_Architecture.ifc"
    file=ifcopenshell.open(Chemin)

    objects=file.by_type("IfcFurnishingElement")
    objects=file.by_type("IfcWallStandardCase")
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

            List_of_faces = get_faces_toward_direction(geom,direction_to_check)
            if len(List_of_faces)==1:
                iterator.next()


            for oneface in List_of_faces:
                # Utiliser la version rapide (basée sur les boîtes englobantes)
                if is_face_occluded(oneface, List_of_faces, direction_to_check):
                    print("RED")
                    display = add_to_display_red(display, oneface)
                else:
                    display = add_to_display_green(display, oneface)



            if not iterator.next():
                break

    display.FitAll()
    start_display()