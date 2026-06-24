import numpy as np
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace, BRepBuilderAPI_Sewing
from OCC.Core.BRepExtrema import BRepExtrema_DistShapeShape
from OCC.Core.gp import gp_Pnt
from OCC.Core.TopoDS import TopoDS_Compound
from OCC.Core.BRep import BRep_Builder
import ifcopenshell
import trimesh
import multiprocessing
import ifcopenshell.geom
from OCC.Core.AIS import AIS_Shape
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Display.SimpleGui import init_display
from OCC.Core.AIS import AIS_Shape
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB


def vertices_to_occ_shape(vertices, faces):
    """
    Convertit des vertices et faces en TopoDS_Shape OpenCASCADE
    
    Args:
        vertices: Liste ou array de vertices [[x1,y1,z1], [x2,y2,z2], ...]
        faces: Liste ou array de faces (indices des vertices) [[0,1,2], [1,2,3], ...]
    """
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
    
    sewing = BRepBuilderAPI_Sewing()
    
    for face_indices in faces:
        # Créer un polygone pour chaque face
        polygon = BRepBuilderAPI_MakePolygon()
        
        for idx in face_indices:
            v = vertices[idx]
            polygon.Add(gp_Pnt(float(v[0]), float(v[1]), float(v[2])))
        
        # Fermer le polygone
        polygon.Close()
        
        if polygon.IsDone():
            wire = polygon.Wire()
            # Créer une face à partir du wire
            face_builder = BRepBuilderAPI_MakeFace(wire)
            if face_builder.IsDone():
                sewing.Add(face_builder.Face())
    
    sewing.Perform()
    return sewing.SewedShape()

def min_distance_between_meshes(vertices1, faces1, vertices2, faces2):
    """
    Calcule la distance minimale entre deux meshes
    
    Args:
        vertices1: Array/liste de vertices du premier mesh (Nx3)
        faces1: Array/liste de faces du premier mesh (Mx3)
        vertices2: Array/liste de vertices du second mesh (Nx3)
        faces2: Array/liste de faces du second mesh (Mx3)
    
    Returns:
        dict avec distance, points les plus proches, etc.
    """
    # Convertir en numpy arrays si nécessaire
    vertices1 = np.array(vertices1)
    faces1 = np.array(faces1)
    vertices2 = np.array(vertices2)
    faces2 = np.array(faces2)
    
    # Créer les shapes OpenCASCADE
    shape1 = vertices_to_occ_shape(vertices1, faces1)
    shape2 = vertices_to_occ_shape(vertices2, faces2)
    
    # Calculer la distance
    dist_calc = BRepExtrema_DistShapeShape(shape1, shape2)
    
    if dist_calc.IsDone():
        distance = dist_calc.Value()
        point1 = dist_calc.PointOnShape1(1)
        point2 = dist_calc.PointOnShape2(1)
        
        return {
            'distance': distance,
            'point1': np.array([point1.X(), point1.Y(), point1.Z()]),
            'point2': np.array([point2.X(), point2.Y(), point2.Z()]),
            'collision': distance < 1e-6
        }
    else:
        raise RuntimeError("Échec du calcul de distance")


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
    if iterator.initialize():
        
        while True:
            shape = iterator.get()
            geom = shape.geometry
            entity = file.by_id(shape.data.id)

            ais_shape=AIS_Shape(geom)
            green_color = Quantity_Color(0.0, 1.0, 0.0, Quantity_TOC_RGB)
            #ais_shape.SetColor(green_color)
            ais_shape.SetTransparency(0.2)
            display.Context.Display(ais_shape, True)

            if not iterator.next():
                break

    display.FitAll()
    start_display()