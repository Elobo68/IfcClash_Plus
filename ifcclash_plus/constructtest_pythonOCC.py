import numpy as np
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace, BRepBuilderAPI_Sewing
from OCC.Core.BRepExtrema import BRepExtrema_DistShapeShape
from OCC.Core.gp import gp_Pnt
from OCC.Core.TopoDS import TopoDS_Compound
from OCC.Core.BRep import BRep_Builder

import trimesh


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

# Exemple d'utilisation
# Cube 1
vertices1 = [
    [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],  # Base
    [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]   # Haut
]
faces1 = [
    [0, 1, 2], [0, 2, 3],  # Base
    [4, 5, 6], [4, 6, 7],  # Haut
    [0, 1, 5], [0, 5, 4],  # Face avant
    [2, 3, 7], [2, 7, 6],  # Face arrière
    [0, 3, 7], [0, 7, 4],  # Côté gauche
    [1, 2, 6], [1, 6, 5]   # Côté droit
]

# Cube 2 (décalé)
vertices2 = [
    [2, 0, 0], [3, 0, 0], [3, 1, 0], [2, 1, 0],
    [2, 0, 1], [3, 0, 1], [3, 1, 1], [2, 1, 1]
]
faces2 = [
    [0, 1, 2], [0, 2, 3],
    [4, 5, 6], [4, 6, 7],
    [0, 1, 5], [0, 5, 4],
    [2, 3, 7], [2, 7, 6],
    [0, 3, 7], [0, 7, 4],
    [1, 2, 6], [1, 6, 5]
]

result = min_distance_between_meshes(vertices1, faces1, vertices2, faces2)
print(f"Distance minimale : {result['distance']:.3f}")
print(f"Point 1 : {result['point1']}")
print(f"Point 2 : {result['point2']}")