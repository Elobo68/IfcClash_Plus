import ifcopenshell
import ifcopenshell.util.selector
import ifcopenshell.geom
import time
from ifcclash.ifcclash import ClashSource
import multiprocessing
import numpy as np
import ifcopenshell.util.placement
import ifcopenshell.util.shape
import numpy as np
from shapely.geometry import Polygon, Point
import bpy


def CreationTriangle(Face):
   
    mesh = bpy.data.meshes.new('Triforce')
    mesh.from_pydata(
    [Face], # vertices
    [], # edges are inferred from face
    [(0, 1, 2)] # face
   )

    triangle = bpy.data.objects.new(mesh.name, mesh)
    coll = bpy.data.scenes['Scene'].collection
    coll.objects.link(triangle)

def faces_share_surface_shapely(face1_vertices, face2_vertices, tolerance=1e-6):
    """
    Check if two coplanar 3D faces share a common surface using Shapely.
    face1_vertices, face2_vertices: List of (x, y, z) tuples.
    tolerance: Tolerance for intersection.
    """
    def project_to_2d(vertices_3d):
        """Project 3D vertices to 2D (XY plane)."""
        return [(x, y) for x, y, z in vertices_3d]

    # Project to 2D
    poly1 = Polygon(project_to_2d(face1_vertices))
    poly2 = Polygon(project_to_2d(face2_vertices))

    is_touching=poly1.touches(poly2)
    if is_touching:
        return False

    # Check if the polygons intersect
    return poly1.buffer(tolerance).intersects(poly2.buffer(tolerance))
def Get_Verts(IfcOpenShell_Object):
    settings = ifcopenshell.geom.settings(USE_WORLD_COORDS=True)
    #settings.set("use-python-opencascade", True)
    shape=ifcopenshell.geom.create_shape(settings,IfcOpenShell_Object)
    grouped=ifcopenshell.util.shape.get_vertices(shape.geometry)
    return  grouped

def Get_Faces(IfcOpenShell_Object):
    settings = ifcopenshell.geom.settings(USE_WORLD_COORDS=True)
    shape = ifcopenshell.geom.create_shape(settings, IfcOpenShell_Object)
    grouped = ifcopenshell.util.shape.get_faces(shape.geometry)
    return grouped

def Get_Norms(IfcOpenShell_Object):
    settings = ifcopenshell.geom.settings()
    settings.set("weld-vertices", False)
    shape = ifcopenshell.geom.create_shape(settings, IfcOpenShell_Object)
    grouped = ifcopenshell.util.shape.get_normals(shape.geometry)
    return grouped

def Get_Property(IfcOpenShell_Object):
    settings = ifcopenshell.geom.settings(USE_WORLD_COORDS=True)
    shape = ifcopenshell.geom.create_shape(settings, IfcOpenShell_Object)
    Max = ifcopenshell.util.shape.get_max_xyz(shape.geometry)
    Max2=ifcopenshell.util.shape.get_shape_top_elevation(shape,shape.geometry)


    print(Max2)

    return None

def Get_Max_Z(IfcOpenShell_Object):
    settings = ifcopenshell.geom.settings(USE_WORLD_COORDS=True)
    shape = ifcopenshell.geom.create_shape(settings, IfcOpenShell_Object)
    grouped = ifcopenshell.util.shape.get_vertices(shape.geometry)
    SetMax=set()
    for vert in grouped:
        SetMax.add(vert[2])

    return max(SetMax)

def Get_Min_Z(IfcOpenShell_Object):
    settings = ifcopenshell.geom.settings(USE_WORLD_COORDS=True)
    shape = ifcopenshell.geom.create_shape(settings, IfcOpenShell_Object)
    grouped = ifcopenshell.util.shape.get_vertices(shape.geometry)
    SetMax=set()
    for vert in grouped:
        SetMax.add(vert[2])

    return min(SetMax)


def Ugly_MinimalDistance_faces(face_a,face_b):

    def Average_Of_Face(face):
        x_avg=0
        y_avg=0
        z_avg=0
        i=0

        for vert in face:
            x_avg += vert[0]
            y_avg += vert[1]
            z_avg += vert[2]
            i +=1


        x_avg = float(x_avg / i)
        y_avg = float(y_avg / i)
        z_avg = float(z_avg / i)

        return np.array([x_avg,y_avg,z_avg])


    face_a = Average_Of_Face(face_a)
    face_b = Average_Of_Face(face_b)

    distance=np.linalg.norm(face_a-face_b)

    return distance

def Ugly_MinimalDistance_faces_ON_XY(face_a,face_b):

    def Average_Of_Face(face):
        x_avg=0
        y_avg=0
        z_avg=0
        i=0

        for vert in face:
            x_avg += vert[0]
            y_avg += vert[1]
            z_avg += vert[2]
            i +=1


        x_avg = float(x_avg / i)
        y_avg = float(y_avg / i)
        z_avg = float(z_avg / i)

        return np.array([x_avg,y_avg])


    face_a = Average_Of_Face(face_a)
    face_b = Average_Of_Face(face_b)

    distance=np.linalg.norm(face_a-face_b)

    return distance


def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    def unit_vector(vector):
        """ Returns the unit vector of the vector.  """
        return vector / np.linalg.norm(vector)

    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

def clash_get_Upper(ta,tb,check_all,min_clearance,max_clearance,type="MaxToMin"):

    BHV_Check=True
    if BHV_Check==False:
        return None

    verts_a = Get_Verts(ta)
    verts_b = Get_Verts(tb)

    faces_a = Get_Faces(ta)
    faces_b = Get_Faces(tb)

    norms_a = Get_Norms(ta)
    norms_b = Get_Norms(tb)

    max_a_z=Get_Max_Z(ta)
    min_a_z=Get_Min_Z(ta)

    max_b_z=Get_Max_Z(tb)
    min_b_z=Get_Min_Z(tb)

    a_reference=None
    b_reference=None

    if type == "MinToMin":
        a_reference = min_a_z
        b_reference = min_b_z
        z_axis_a = (0.0, 0.0, -1.0)
        z_axis_b = (0.0, 0.0, -1.0)

    if type == "MaxToMin":
        a_reference = max_a_z
        b_reference = min_b_z
        z_axis_a = (0.0, 0.0, 1.0)
        z_axis_b = (0.0, 0.0, -1.0)

    if type == "MaxToMax":
        a_reference = max_a_z
        b_reference = max_b_z
        z_axis_a = (0.0, 0.0, 1.0)
        z_axis_b = (0.0, 0.0, 1.0)

    if type == "MinToMax":
        a_reference = min_a_z
        b_reference = max_b_z
        z_axis_a = (0.0, 0.0, -1.0)
        z_axis_b = (0.0, 0.0, 1.0)

    a_reference_minClearance=a_reference+min_clearance
    a_reference_maxclearance=a_reference+max_clearance

    #We check with min and max, this check is additionnal to BVH check. It
    if a_reference_maxclearance<b_reference<a_reference_minClearance:
        #The check can not be true, but it still may be false.
        return "False"



    Tolerance_Top_Bottom_Selection = 0.1
    Tolerance_XY = 0.01

    if check_all==False:
        #In the model, we can assume that a majority of element are cubic like. If we check only faces close to max or min, it will quickly find a solution.
        for a_number,face_a in enumerate(faces_a):
            face_a_value = (verts_a[face_a[0]], verts_a[face_a[1]], verts_a[face_a[2]])
            norms_a_value = norms_a[a_number]
            Angle_A_To_Z=angle_between(norms_a_value,z_axis_a)

            if not 0<=Angle_A_To_Z<=0.785:
                #We check if the angle is at 45 degres
                continue

            for b_number,face_b in enumerate(faces_b):

                face_b_value = (verts_b[face_b[0]], verts_b[face_b[1]], verts_b[face_b[2]])
                norms_b_value = norms_b[b_number]
                Angle_b_To_Z = angle_between(norms_b_value, z_axis_b)

                if not 0 <= Angle_b_To_Z <= 0.785:
                    # We check if the angle is at 45 degres
                    continue
                # @todo il faut vérifier que la surface qui regarde vers le haut n'est pas en dessous d'une autre surface. Il faut dans tous les cas de figure itérer une première fois sur l'objet en question.

                #For cubic like element, we can check only the face that are close to the top.

                if not (ifcopenshell.util.shape.is_x(face_a_value[0][2],a_reference,Tolerance_Top_Bottom_Selection) or ifcopenshell.util.shape.is_x(face_a_value[1][2],a_reference,Tolerance_Top_Bottom_Selection) or ifcopenshell.util.shape.is_x(face_a_value[1][2],a_reference,Tolerance_Top_Bottom_Selection)):
                    continue
                if not (ifcopenshell.util.shape.is_x(face_b_value[0][2], b_reference,Tolerance_Top_Bottom_Selection) or ifcopenshell.util.shape.is_x(face_b_value[1][2],b_reference,Tolerance_Top_Bottom_Selection) or ifcopenshell.util.shape.is_x(face_b_value[1][2], b_reference, Tolerance_Top_Bottom_Selection)):
                    continue
                #If the face is not in the top or bottom of the geometry, it's not usefull to test. It could be better to avoid them with the BVH.


                Result_Shared_Surface = faces_share_surface_shapely(face_a_value, face_b_value)
                #@todo Il faut que la partie a de cette fonction reprenne la totalité de la surface supérieure de l'objet et non pas unique une face. Ca resrtreint trop les cas de figure.
                if Result_Shared_Surface==False:
                    continue

                #We check only the faces that are on top of each other.
                distance = Ugly_MinimalDistance_faces(face_a_value, face_b_value)
                print(verts_a[face_a][0])

                CreationTriangle(verts_a[face_a])

                if min_clearance < distance and distance < max_clearance:
                    print(distance,face_a_value,face_b_value)





"""
                        print("a_reference:", a_reference, "b_reference", b_reference)
                        print("a_reference_minClearance:", a_reference_minClearance, "a_reference_maxclearance:",
                              a_reference_maxclearance, "Distance:", distance)

"""


def Lancement_Test():
    path = "/home/jocelin/Documents/05 - Programmation/IfcClash_Plus/Ifc_Model/Ifc2x3_Duplex_Architecture.ifc"
    file= ifcopenshell.open(path)
    Elements = ifcopenshell.util.selector.filter_elements(file, "IfcSpace")
    Elements=list(Elements)


    Element_a = next(iter(ifcopenshell.util.selector.filter_elements(file, "IfcWall, Name=foo")))
    Element_b = next(iter(ifcopenshell.util.selector.filter_elements(file, "IfcWall, Name=bar")))

    print(Element_a)
    print(Element_b)


    clash_get_Upper(Element_a,Element_b,min_clearance=0.1,max_clearance=6,type="MaxToMin",check_all=False)


if __name__ == "__main__":
   print("Hello World: run from Blender Text Editor")
else:
   print("Hello World: run from VSCode")
   print(f"NOTE. __name__ is : {__name__}")


Lancement_Test()






