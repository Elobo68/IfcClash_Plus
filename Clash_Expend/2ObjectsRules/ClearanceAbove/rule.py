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
from Clash_Expend.Rule_Utils import Get_Verts,Get_Faces,Get_Norms,Get_Max_Z,Get_Min_Z,angle_between,Ugly_MinimalDistance_faces,CreationTriangle
import ifcopenshell.util.element


def faces_share_surface_shapely(faceA,FaceB):
    ...

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
    path = "Ifc_Model/Ifc2x3_Duplex_Architecture.ifc"
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






