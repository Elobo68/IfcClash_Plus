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