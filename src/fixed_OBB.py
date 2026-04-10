from OCC.Core.Bnd import Bnd_Box, Bnd_OBB
from OCC.Core.BRepBndLib 
from OCC.Core.BRepBndLib import brepbndlib
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.gp import gp_Ax3, gp_Pnt, gp_Dir, gp_Trsf, gp_XYZ,gp_Vec
from OCC.Core.BRepExtrema import BRepExtrema_DistShapeShape
import numpy as np
from OCC.Core.BRepExtrema import BRepExtrema_DistShapeShape


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
    min_area = float("inf")
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

    #@todo For inclined objects and extrude, fixed Z will be incoherent. 

    return obb


class Custum_OBB(Bnd_OBB):
    def __init__(self):
        super().__init__()


def get_min_corner(OBB:Bnd_OBB)->float:
    center=OBB.Center()
    x_comp=OBB.XDirection().Multiplied(OBB.XHSize())
    y_comp=OBB.YDirection().Multiplied(OBB.YHSize())
    Z_comp=OBB.ZDirection().Multiplied(OBB.ZHSize())

    mincorner=center-(x_comp+y_comp+Z_comp)
    return mincorner
def get_max_corner(OBB:Bnd_OBB)->float:
    center=OBB.Center()
    x_comp=OBB.XDirection().Multiplied(OBB.XHSize())
    y_comp=OBB.YDirection().Multiplied(OBB.YHSize())
    Z_comp=OBB.ZDirection().Multiplied(OBB.ZHSize())
    mincorner=center+(x_comp+y_comp+Z_comp)
    return mincorner


def Extend_Cube(OBB: Bnd_OBB) -> list[Bnd_OBB]:
    def extrude_top(OBB: Bnd_OBB, change) -> Bnd_OBB:
        center = OBB.Center()
        theHZSize = OBB.ZHSize()

        if type(change) is str:
            change = change.replace("%", "")
            change = float(change)
            change = change / 100
            new_theHZSize = theHZSize + (theHZSize * change) / 2
            new_center = gp_Pnt(
                center.X(), center.Y(), center.Z() + (theHZSize * change) / 2
            )
        else:
            new_theHZSize = theHZSize + change / 2
            new_center = gp_Pnt(center.X(), center.Y(), center.Z() + change / 2)
        OBB.SetCenter(new_center)
        OBB.SetZComponent(gp_Dir(OBB.ZDirection()), new_theHZSize)

        return OBB

    def extrude_bottom(OBB: Bnd_OBB, change) -> Bnd_OBB:
        center = OBB.Center()
        theHZSize = OBB.ZHSize()

        if type(change) is str:
            change = change.replace("%", "")
            change = float(change)
            change = change / 100
            new_theHZSize = theHZSize + (theHZSize * change) / 2
            new_center = gp_Pnt(
                center.X(), center.Y(), center.Z() - (theHZSize * change) / 2
            )
        else:
            new_theHZSize = theHZSize + change / 2
            new_center = gp_Pnt(center.X(), center.Y(), center.Z() - change / 2)
        OBB.SetCenter(new_center)
        OBB.SetZComponent(gp_Dir(OBB.ZDirection()), new_theHZSize)

        return OBB

    def extrude_side(OBB: Bnd_OBB, change) -> Bnd_OBB:
        center = OBB.Center()
        theHXSize = OBB.XHSize()
        theHYSize = OBB.YHSize()
        theHZSize = OBB.ZHSize()
        new_theHXSize = theHXSize
        new_theHYSize = theHYSize

        if type(change) is str:
            change = change.replace("%", "")
            change = float(change)
            change = change / 100
            new_theHXSize = theHXSize + (theHXSize * change) / 2
            new_theHYSize = theHYSize + (theHYSize * change) / 2

        else:
            new_theHXSize = theHZSize + change / 2
            new_theHYSize = theHZSize + change / 2

        OBB.SetXComponent(gp_Dir(OBB.XDirection()), new_theHXSize)
        OBB.SetYComponent(gp_Dir(OBB.YDirection()), new_theHYSize)

        return OBB
    
    def extrude_front(OBB: Bnd_OBB, change) -> Bnd_OBB:
        center = OBB.Center()
        theHXSize = OBB.XHSize()
        theHYSize = OBB.YHSize()
        theHZSize = OBB.ZHSize()
        new_theHXSize = theHXSize
        new_theHYSize = theHYSize

        if type(change) is str:
            change = change.replace("%", "")
            change = float(change)
            change = change / 100
            new_theHXSize = theHXSize + (theHXSize * change) / 2
            new_theHYSize = theHYSize + (theHYSize * change) / 2

        else:
            new_theHXSize = theHZSize + change / 2
            new_theHYSize = theHZSize + change / 2

        OBB.SetXComponent(gp_Dir(OBB.XDirection()), new_theHXSize)
        OBB.SetYComponent(gp_Dir(OBB.YDirection()), new_theHYSize)

        return OBB

    def detach_top_by_extrude(OBB: Bnd_OBB, change) -> Bnd_OBB:
        if type(change) is str:
            change = change.replace("%", "")
            change = float(change)
            change = change / 100

        center = gp_Pnt(OBB.Center() + gp_XYZ(0, 0, OBB.ZHSize() + change / 2))
        x_dir = gp_Dir(OBB.XDirection())
        y_dir = gp_Dir(OBB.YDirection())
        z_dir = gp_Dir(OBB.ZDirection())
        x_h = OBB.XHSize()
        y_h = OBB.YHSize()
        z_h = change / 2

        OBB = Bnd_OBB(center, x_dir, y_dir, z_dir, x_h, y_h, z_h)

        return OBB

    def detach_bottom_by_extrude(OBB: Bnd_OBB, change) -> Bnd_OBB:
        if type(change) is str:
            change = change.replace("%", "")
            change = float(change)
            change = change / 100

        center = gp_Pnt(OBB.Center() + gp_XYZ(0, 0, -OBB.ZHSize() - change / 2))
        x_dir = gp_Dir(OBB.XDirection())
        y_dir = gp_Dir(OBB.YDirection())
        z_dir = gp_Dir(OBB.ZDirection())
        x_h = OBB.XHSize()
        y_h = OBB.YHSize()
        z_h = change / 2

        OBB = Bnd_OBB(center, x_dir, y_dir, z_dir, x_h, y_h, z_h)

        return OBB

    # @todo Find a way to expand the OBB in order to configure and expanded bouding box.
    #
    # Reduce Top,Bottom,Side,FrontAndBack,
    # Reduce

    # OBB.Enlarge(2), it create a new "box" around
    OBB = extrude_bottom(OBB, "+10%")

    print("After OBB", OBB.DumpJson())

    return 10


"""
Faire une fonction qui vérifie une liste de bouding box. 
De cette manière, on pourrait creer des formes complexes avec une liste de bouding box et vérifier cette liste. 


Pour les poutres, il faut déterminer l'axe de la poutre. Perpendiculairement à cet axe, on peut faire 4 boites, une en bas et deux sur les côtés.

Pour les extrusions, il faut suivre la normal. 
Pour les extrusions, on peut aussi faire des relations entre les propriétés de l'objet. 

@todo Check how to deal with inclined geometry. 
Attention, pour les objets inclinés. 
On pourrait vérifier le IfcAxis2Placement3D et détecter les objets qui sont modélisés inclinés. Le Z ne serait pas (0,0,1)



"""

if __name__ == "__main__":
    center = gp_Pnt(5, 5, 5)
    x_dir = gp_Dir(1, 1, 0)
    y_dir = gp_Dir(-1, 1, 0)
    z_dir = gp_Dir(0, 0, 1)
    x_h = 5
    y_h = 5
    z_h = 5


    OBB = Bnd_OBB(center, x_dir, y_dir, z_dir, x_h, y_h, z_h)
    # OBB=Bnd_OBB(*dict)

    center = gp_Pnt(0, -5, 0)
    OBB_2 = Bnd_OBB(center, x_dir, y_dir, z_dir, x_h, y_h, z_h)

    result = OBB.IsOut(OBB_2)
    result = OBB.Distance(OBB_2)

    print(dist_tool)


