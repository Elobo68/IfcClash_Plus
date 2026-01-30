import ifcopenshell
import ifcopenshell.util.element as attt
import ifcopenshell.geom
import multiprocessing
from OCC.Core.Bnd import Bnd_OBB
from OCC.Core.BRepBndLib import brepbndlib
from OCC.Core.gp import gp_Dir,gp_XYZ,gp_Ax3,gp_Trsf,gp_Pnt,gp_Vec,gp_Ax1
from OCC.Display.SimpleGui import init_display
from OCC.Core.AIS import AIS_Shape
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform,BRepBuilderAPI_MakePolygon
import OCC.Core.BRepPrimAPI as br
import fixed_OBB


def OBB_To_Shape(obb:Bnd_OBB):
    TheBox=BRepPrimAPI_MakeBox(obb.XHSize()*2,obb.YHSize()*2,obb.ZHSize()*2).Shape()

    center=gp_Pnt(obb.Center())
  

    
    trans=gp_Trsf()

    trans.SetTranslation(gp_Vec(center.X()-obb.XHSize(),center.Y()-obb.XHSize(),center.Z()-obb.ZHSize()))
    gp_ax1=gp_Ax1(gp_Pnt(obb.Center()),gp_Dir(obb.ZDirection()))
    #trans.SetRotation(gp_ax1,0.0)



    TheBox=BRepBuilderAPI_Transform(TheBox,trans).Shape()


    return TheBox

def MakeBox(obb:Bnd_OBB):
    center=obb.Center()
    x_dir=obb.XDirection()
    y_dir=obb.YDirection()
    z_dir=obb.ZDirection()

    x_half=obb.XHSize()
    y_half=obb.YHSize()
    z_half=obb.ZHSize()

    vertices=[]
    polygon=BRepBuilderAPI_MakePolygon()


    for dx in [-1,1]:
        for dy in [-1,1]:
            for dz in [-1,1]:
                vertice=center+x_dir*x_half*dx+y_dir*y_half*dy+z_dir*z_half*dz
                print(dx,dy,dz,vertice.DumpJson())
                polygon.Add(gp_Pnt(vertice))
                vertices.append(gp_Pnt(vertice))
    

    polygon.Close()
    polygon.Wire()

    return polygon.Shape()



chemin="Ifc_Model/Ifc2x3_Duplex_Architecture.ifc"
file=ifcopenshell.open(chemin)

spaces=file.by_type("IFCDISTRIBUTIONCONTROLELEMENT")
#spaces=file.by_type("IFCSPACE")
#spaces=file.by_type("IFCWALL")
space=spaces[0]

settings=ifcopenshell.geom.settings()
settings.set("use-python-opencascade", True)
#shape=ifcopenshell.geom.create_shape(settings,space.Representation)


iterator = ifcopenshell.geom.iterator(
    settings,
    file,
    multiprocessing.cpu_count(),
    include=spaces,
)

display,start_display,add_menu,add_funtion=init_display()

if iterator.initialize():
    while True:
        shape = iterator.get()
        geom = shape.geometry

        obb_temp = Bnd_OBB()
        brepbndlib.AddOBB(geom,obb_temp,True,True,True)

        Suzanne_AIS=AIS_Shape(geom)
        Suzanne_AIS.SetTransparency(0.5)

        display.Context.Display(Suzanne_AIS,True)

        
        # Récupérer le centre
        center = obb_temp.Center()

        # Créer une nouvelle OBB avec Z fixé
        obb = Bnd_OBB()
        z_dir = gp_Dir(0, 0, 1)
        x_dir = gp_Dir(1, 0, 0)

        half_size_x=obb_temp.XHSize()
        half_size_y=obb_temp.YHSize()
        half_size_z=obb_temp.ZHSize()

        

        # Projeter les dimensions sur le plan XY
        obb.SetCenter(gp_Pnt(center))
        obb.SetXComponent(x_dir, half_size_x)
        obb.SetYComponent(gp_Dir(0, 1, 0), half_size_y)
        obb.SetZComponent(z_dir, half_size_z)

        #
        obb_shape=fixed_OBB.create_obb_with_fixed_z(geom)
        obb_shape=MakeBox(obb_shape)
        obb_AIS=AIS_Shape(obb_shape)
        obb_AIS.SetTransparency(0.5)
        display.Context.Display(obb_AIS,True)


        if not iterator.next():
            break

display.FitAll()
start_display()