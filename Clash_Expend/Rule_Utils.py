import bpy
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util
import ifcopenshell.util.shape
import numpy as np


def CreationTriangle(Face):
    mesh = bpy.data.meshes.new('Triforce')
    mesh.from_pydata(
        [Face],  # vertices
        [],  # edges are inferred from face
        [(0, 1, 2)]  # face
    )

    triangle = bpy.data.objects.new(mesh.name, mesh)
    coll = bpy.data.scenes['Scene'].collection
    coll.objects.link(triangle)


def Get_Verts(IfcOpenShell_Object):
    settings = ifcopenshell.geom.settings(USE_WORLD_COORDS=True)
    # settings.set("use-python-opencascade", True)
    shape = ifcopenshell.geom.create_shape(settings, IfcOpenShell_Object)
    grouped = ifcopenshell.util.shape.get_vertices(shape.geometry)
    return grouped


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
    Max2 = ifcopenshell.util.shape.get_shape_top_elevation(shape, shape.geometry)

    print(Max2)

    return None


def Get_Max_Z(IfcOpenShell_Object):
    settings = ifcopenshell.geom.settings(USE_WORLD_COORDS=True)
    shape = ifcopenshell.geom.create_shape(settings, IfcOpenShell_Object)
    grouped = ifcopenshell.util.shape.get_vertices(shape.geometry)
    SetMax = set()
    for vert in grouped:
        SetMax.add(vert[2])

    return max(SetMax)


def Get_Min_Z(IfcOpenShell_Object):
    settings = ifcopenshell.geom.settings(USE_WORLD_COORDS=True)
    shape = ifcopenshell.geom.create_shape(settings, IfcOpenShell_Object)
    grouped = ifcopenshell.util.shape.get_vertices(shape.geometry)
    SetMax = set()
    for vert in grouped:
        SetMax.add(vert[2])

    return min(SetMax)


def Ugly_MinimalDistance_faces(face_a, face_b):
    def Average_Of_Face(face):
        x_avg = 0
        y_avg = 0
        z_avg = 0
        i = 0

        for vert in face:
            x_avg += vert[0]
            y_avg += vert[1]
            z_avg += vert[2]
            i += 1

        x_avg = float(x_avg / i)
        y_avg = float(y_avg / i)
        z_avg = float(z_avg / i)

        return np.array([x_avg, y_avg, z_avg])

    face_a = Average_Of_Face(face_a)
    face_b = Average_Of_Face(face_b)

    distance = np.linalg.norm(face_a - face_b)

    return distance


def Ugly_MinimalDistance_faces_ON_XY(face_a, face_b):
    def Average_Of_Face(face):
        x_avg = 0
        y_avg = 0
        z_avg = 0
        i = 0

        for vert in face:
            x_avg += vert[0]
            y_avg += vert[1]
            z_avg += vert[2]
            i += 1

        x_avg = float(x_avg / i)
        y_avg = float(y_avg / i)
        z_avg = float(z_avg / i)

        return np.array([x_avg, y_avg])

    face_a = Average_Of_Face(face_a)
    face_b = Average_Of_Face(face_b)

    distance = np.linalg.norm(face_a - face_b)

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