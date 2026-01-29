from OCC.Core.Bnd import Bnd_Box, Bnd_OBB
from OCC.Core.BRepBndLib import brepbndlib
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.gp import gp_Ax3, gp_Pnt, gp_Dir, gp_Trsf
from OCC.Core.BRepExtrema import BRepExtrema_DistShapeShape
import numpy as np

def create_obb_with_fixed_z(shape):
    """
    Crée une OBB avec l'axe Z fixé à (0,0,1)
    """
    # 1. Créer une bounding box AABB pour obtenir les limites Z
    aabb = Bnd_Box()
    brepbndlib.Add(shape, aabb)
    xmin, ymin, zmin, xmax, ymax, zmax = aabb.Get()
    
    # 2. Calculer les projections des points sur le plan XY
    # Pour cela, on peut transformer la shape ou analyser ses vertices
    from OCC.Core.TopExp import TopExp_Explorer
    from OCC.Core.TopAbs import TopAbs_VERTEX
    from OCC.Core.BRep import BRep_Tool
    
    points_xy = []
    explorer = TopExp_Explorer(shape, TopAbs_VERTEX)
    while explorer.More():
        vertex = explorer.Current()
        pnt = BRep_Tool.Pnt(vertex)
        points_xy.append([pnt.X(), pnt.Y()])
        explorer.Next()
    
    points_xy = np.array(points_xy)
    
    # 3. Calculer l'OBB 2D optimale dans le plan XY
    # Méthode simple: tester différentes rotations autour de Z
    min_area = float('inf')
    best_angle = 0
    
    for angle in np.linspace(0, np.pi, 180):
        # Matrice de rotation
        cos_a, sin_a = np.cos(angle), np.sin(angle)
        rot_matrix = np.array([[cos_a, sin_a], [-sin_a, cos_a]])
        
        # Rotation des points
        rotated = points_xy @ rot_matrix.T
        
        # Calculer les dimensions de la bounding box alignée sur les axes
        x_range = rotated[:, 0].max() - rotated[:, 0].min()
        y_range = rotated[:, 1].max() - rotated[:, 1].min()
        area = x_range * y_range
        
        if area < min_area:
            min_area = area
            best_angle = angle
            best_x_range = x_range
            best_y_range = y_range
            best_x_center = (rotated[:, 0].max() + rotated[:, 0].min()) / 2
            best_y_center = (rotated[:, 1].max() + rotated[:, 1].min()) / 2
    
    # 4. Transformer le centre dans le repère global
    cos_a, sin_a = np.cos(best_angle), np.sin(best_angle)
    center_x = best_x_center * cos_a - best_y_center * sin_a
    center_y = best_x_center * sin_a + best_y_center * cos_a
    center_z = (zmax + zmin) / 2
    
    # 5. Créer l'OBB avec les bonnes dimensions
    obb = Bnd_OBB()
    center = gp_Pnt(center_x, center_y, center_z)
    
    z_dir = gp_Dir(0, 0, 1)
    x_dir = gp_Dir(cos_a, sin_a, 0)
    y_dir = gp_Dir(-sin_a, cos_a, 0)
    
    obb.SetCenter(center)
    obb.SetXComponent(x_dir, best_x_range / 2)
    obb.SetYComponent(y_dir, best_y_range / 2)
    obb.SetZComponent(z_dir, (zmax - zmin) / 2)  # Hauteur complète
    
    return obb



def Extend_Cube(obb:Bnd_OBB):


    #@todo Find a way to expand the OBB in order to configure and expanded bouding box. 
    



    print("")