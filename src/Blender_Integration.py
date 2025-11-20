import bpy
import ifcopenshell
import ifcopenshell.util.shape
import numpy as np
import ifcopenshell.util.selector



import shapely
import shapely.ops
import numpy.typing as npt
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
from ifcopenshell.geom import ShapeType
from typing import Optional, Literal
import ifcopenshell.geom

AXIS_LITERAL = Literal["X", "Y", "Z"]

VECTOR_3D = tuple[float, float, float]

MatrixType = npt.NDArray[np.float64]
"""`npt.NDArray[np.float64]`"""


def get_extreme_faces(
    vertices,
    faces,
    geometry: ShapeType,
    axis: AXIS_LITERAL = "Z",
    direction: Optional[VECTOR_3D] = None,
) -> float:
    

    from ifcopenshell.util.shape import get_vertices,get_faces

    """Calculates the total footprint (i.e. projected) surface area visible from along an axis

    This is typically useful for calculating footprint areas. For example, you
    might want to calculate the top-down footprint area of a slab, ignoring
    slopes in the slab.

    Surfaces do not need to be exactly perpendicular in the direction of the
    specified axis. A surface is counted so long as it is visible from that
    axis.

    Note that this calculates the 2D projected area, not the actual surface
    area. If you want the actual area, use :func:`get_side_area`.

    :param geometry: Geometry output calculated by IfcOpenShell
    :param axis: Either X, Y, or Z. Defaults to Z.
    :param direction: An XYZ iterable (e.g. (0., 0., 1.)). If a direction
        vector is specified, this overrides the axis argument.
    :return: The surface area.
    """
    if direction is None:
        direction = {"X": (1.0, 0.0, 0.0), "Y": (0.0, 1.0, 0.0), "Z": (0.0, 0.0, 1.0)}[axis]

    #vertices = get_vertices(geometry)
    #faces = get_faces(geometry)

    # Calculate the triangle normal vectors
    v1 = vertices[faces[:, 1]] - vertices[faces[:, 0]]
    v2 = vertices[faces[:, 2]] - vertices[faces[:, 0]]
    triangle_normals = np.cross(v1, v2)

    # Normalize the normal vectors
    triangle_normals = triangle_normals / np.linalg.norm(triangle_normals, axis=1)[:, np.newaxis]
    direction = np.array(direction) / np.linalg.norm(direction)

    # Find the faces with a normal vector pointing in the desired direction using dot product
    # normal_tol < 0 is pointing away, = 0 is perpendicular, and > 0 is pointing towards.
    normal_tol = 0.01  # Close to perpendicular, but with a fuzz for numerical tolerance
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

            if direction[2]==-1:
                if z_avg<loop_z_avg:
                    continue
            if direction[2]==1:
                if z_avg>loop_z_avg:
                    continue

            intersection=polygon.intersection(loop_polygon)
            covering_percent=intersection.area/polygon.area
            covered_area+=covering_percent
            

        #Covered area can be higher than 1 if it's covered multiple time

        if 0.99<covered_area:
            continue
        print("Face to print",z_avg,"int area",intersection.area,"covered area",covered_area)
        bottom_faces.append(face)
    
    return bottom_faces

            

def CreationTriangle(Face,Color=None):
    print(Face)
    mesh = bpy.data.meshes.new('Triforce')
    mesh.from_pydata(vertices=Face,edges=[],faces=[(1,0,2)])

    triangle = bpy.data.objects.new(mesh.name, mesh)


    if Color is not None:
        triangle.active_material = Color

    coll = bpy.data.scenes['Scene'].collection
    coll.objects.link(triangle)


def Get_Verts(IfcOpenShell_Object):
    settings = ifcopenshell.geom.settings(USE_WORLD_COORDS=False)
    # settings.set("use-python-opencascade", True)
    shape = ifcopenshell.geom.create_shape(settings, IfcOpenShell_Object)
    grouped = ifcopenshell.util.shape.get_vertices(shape.geometry)
    return grouped


def Get_Faces(IfcOpenShell_Object):
    settings = ifcopenshell.geom.settings(USE_WORLD_COORDS=False)
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


def Get_Verts(IfcOpenShell_Object):
    settings = ifcopenshell.geom.settings(USE_WORLD_COORDS=False)
    # settings.set("use-python-opencascade", True)
    shape = ifcopenshell.geom.create_shape(settings, IfcOpenShell_Object)
    grouped = ifcopenshell.util.shape.get_vertices(shape.geometry)
    return grouped


def Read_IFC_Model():
    file=ifcopenshell.open("Ifc_Model/Ifc2x3_Duplex_Architecture_with_suzanne.ifc")

    Element_a = next(iter(ifcopenshell.util.selector.filter_elements(file, "Name=Suzanne")))
    print(Element_a)


    matg = bpy.data.materials.new("Green")
    matg.use_nodes = True
    tree = matg.node_tree
    nodes = tree.nodes
    bsdf = nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0, 1, 0, 0.8)
    matg.diffuse_color = (0, 1, 0, 0.8)
    


    Faces=Get_Faces(Element_a)
    Verts=Get_Verts(Element_a)
    Norms=Get_Norms(Element_a)
    print(Norms)
    


    Faces=get_extreme_faces(geometry=Element_a,vertices=Verts,faces=Faces,direction=(0.0, 0.0, -1.0))


    for face in Faces:
        FaceToPrint=list()
        for count,OneVertPointer in enumerate(face):
            Point=Verts[OneVertPointer].tolist()
            Point=tuple(Point)
            FaceToPrint.append(Point)
        CreationTriangle(FaceToPrint,matg)


def CreateBaseTriangle():
    List1=(0,0,0)
    List2=(0,1,0)
    List3=(1,0,0)
    FaceToPrint=[List1,List2,List3]
    print(FaceToPrint)
    CreationTriangle(FaceToPrint)



if __name__ == "__main__":
   print("Hello World: run from Blender Text Editor")
else:
   print("Hello World: run from VSCode")
   print(f"NOTE. __name__ is : {__name__}")


Read_IFC_Model()



