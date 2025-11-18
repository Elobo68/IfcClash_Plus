from RuleClass import RuleCheckOneObject,RuleCheckTwoObjects,SelectFacet,ClashResultOneObject,ClashResultTwoObjects,SelectRule
import ifcopenshell
from ifctester import ids
import multiprocessing
from clash_utils import get_extreme_faces
import shapely
from ifcopenshell.util.shape import get_vertices,get_faces,get_edges,get_normals,get_footprint_area
import clash_utils


#===========One Object Rule
class Volume(RuleCheckOneObject):
    from ifcopenshell.util.shape import get_volume
    def __init__(self,source,volume_min,volume_max):
        self.type="Volume"
        self.volume_max:float = volume_max
        self.volume_min:float = volume_min
        self.select_source = source
        self.geom_settings = ifcopenshell.geom.settings()

    def run(self,state="Final"):
        self.tree = ifcopenshell.geom.tree()
        self.select_source.run()

        for ifc_file in self.select_source.dict_elements.keys():
            iterator = ifcopenshell.geom.iterator(self.geom_settings, ifc_file, multiprocessing.cpu_count(),include=self.select_source.dict_elements[ifc_file])

            if iterator.initialize():
                while True:
                    shape = iterator.get()
                    geom=shape.geometry
                    volume=ifcopenshell.util.shape.get_volume(geom)
                    entity=ifc_file.by_id(shape.id)
                    if self.volume_min<volume<self.volume_max:
                        result=ClashResultOneObject(source=entity,state=True)
                        self.result.append(result)
                    else:
                        result=ClashResultOneObject(source=entity,state=False)
                        self.result.append(result)
                    if not iterator.next():
                        break
        
        
        if state=="Final":       
            self.manage_result()
        else:
            self.produce_select()
        
class Area(RuleCheckOneObject):
    from ifcopenshell.util.shape import get_area
    def __init__(self,source,volume_min,volume_max):
        self.type="Volume"
        self.volume_max:float = volume_max
        self.volume_min:float = volume_min
        self.select_source = source
        self.geom_settings = ifcopenshell.geom.settings()

    def run(self,state="Final"):
        self.tree = ifcopenshell.geom.tree()
        self.select_source.run()

        for ifc_file in self.select_source.dict_elements.keys():
            iterator = ifcopenshell.geom.iterator(self.geom_settings, ifc_file, multiprocessing.cpu_count(),include=self.select_source.dict_elements[ifc_file])

            if iterator.initialize():
                while True:
                    shape = iterator.get()
                    geom=shape.geometry
                    area=ifcopenshell.util.shape.get_area(geom)
                    entity=ifc_file.by_id(shape.id)
                    if self.volume_min<area<self.volume_max:                       
                        result=ClashResultOneObject(source=entity,state=True)
                        self.result.append(result)
                    else:
                        result=ClashResultOneObject(source=entity,state=False)
                        self.result.append(result)
                    if not iterator.next():
                        break
        
        if state=="Final":       
            self.manage_result()
        else:
            self.produce_select()

class TopSurface(RuleCheckOneObject):

    def __init__(self,source,surface_min,surface_max):
        self.type="Volume"
        self.surface_max:float = surface_max
        self.surface_min:float = surface_min
        self.select_source = source
        self.geom_settings = ifcopenshell.geom.settings()

    def run(self,state="Final",top_or_bot="top"):

        if top_or_bot=="top":
            direction=(0.0,0.0,1)
        if top_or_bot=="bot":
            direction=(0.0,0.0,-1)

        self.tree = ifcopenshell.geom.tree()
        self.select_source.run()

        for ifc_file in self.select_source.dict_elements.keys():
            iterator = ifcopenshell.geom.iterator(self.geom_settings, ifc_file, multiprocessing.cpu_count(),include=self.select_source.dict_elements[ifc_file])

            if iterator.initialize():
                while True:
                    shape = iterator.get()
                    geom=shape.geometry
                    entity=ifc_file.by_id(geom.id)
                    vertices=get_vertices(geom)
                    faces=get_extreme_faces(geometry=geom,direction=direction)
                    polygons = [shapely.Polygon(vertices[face]) for face in faces]
                    unioned_polygon = shapely.ops.unary_union(polygons)

                    if self.surface_min<unioned_polygon.area<self.surface_max:
                        result=ClashResultOneObject(source=entity,state=True)
                        self.result.append(result)
                    else:
                        result=ClashResultOneObject(source=entity,state=False)
                        self.result.append(result)

                    
                    if not iterator.next():
                        break
        

        
        if state=="Final":       
            self.manage_result()
        else:
            self.produce_select()



#====== Two Objects Rule
class Intersection(RuleCheckTwoObjects):
    def __init__(self,source,target,tolerance=0.1):
        super().__init__()
        
        self.type="Intersection"
        self.tolerance:float = tolerance
        self.select_source = source
        self.select_target = target
        self.geom_settings = ifcopenshell.geom.settings()

    def run(self,state="Final"):
        self.tree = ifcopenshell.geom.tree()

        source_elements=[]
        target_elements=[]


        if state=="Final":
            self.select_source.run()
            self.select_target.run()
            self.add_to_tree(self.select_source,"BVH")
            self.add_to_tree(self.select_target,"BVH")

            for file in self.select_source.dict_elements.keys():
                list=self.select_source.dict_elements[file]
                for element in list:
                    source_elements.append(element)


            for file in self.select_target.dict_elements.keys():
                list=self.select_target.dict_elements[file]
                for element in list:
                    target_elements.append(element)

        if state=="Exception":
            self.add_OneObject_to_tree(self.select_source,"BVH")
            self.add_OneObject_to_tree(self.select_target,"BVH")
            source_elements.append(self.select_source)
            target_elements.append(self.select_target)


        temp_result= self.tree.clash_intersection_many(
            source_elements,
            target_elements,
            tolerance=self.tolerance,
            check_all=True,
        )

        list_result=[] #I need to do that to avoid reusing the same result result in the different intersection.


        #@todo make a proper integration, how to deal with extra data ? (Point of entry, distance, etc...)
        for result in temp_result:
            source_file=ifcopenshell.file.from_pointer(result.a.file_pointer())
            source_object=source_file.by_id(result.a.id_)

            target_file=ifcopenshell.file.from_pointer(result.b.file_pointer())
            target_object=target_file.by_id(result.b.id_)


            list_result.append(ClashResultTwoObjects(source=source_object,target=target_object,state=True))

        self.result=list_result

        if state=="Final":       
            self.manage_result()
        
        if state=="Select":       
            self.produce_select()

        
class Clearance(RuleCheckTwoObjects):
    def __init__(self,source,target,clearance=0.05):
        self.type="Clearance"
        self.select_source = source
        self.select_target = target
        self.geom_settings = ifcopenshell.geom.settings()
        self.clearance: float = 0.05
        self.check_all: bool = False

    def run(self,state="Final"):
        self.tree = ifcopenshell.geom.tree()
        self.select_source.run()
        self.select_target.run()

        self.add_to_tree(self.select_source,"BVH")
        self.add_to_tree(self.select_target,"BVH")

        self.results = self.tree.clash_clearance_many(
            self.select_source.elements,
            self.select_target.elements,
            clearance=self.clearance,
            check_all=self.check_all,
        )

        self.Result_Management(state)

class Collision(RuleCheckTwoObjects):
    def __init__(self,source,target,tolerance=0):
        self.type="Collision"
        self.allow_touching = False
        self.select_source = source
        self.select_target = target
        self.geom_settings = ifcopenshell.geom.settings()

    def run(self,state="Final"):
        self.tree = ifcopenshell.geom.tree()
        self.select_source.run()
        self.select_target.run()

        self.add_to_tree(self.select_source,"BVH")
        self.add_to_tree(self.select_target,"BVH")

        self.results = self.tree.clash_collision_many(
            self.select_source.elements,
            self.select_target.elements,
            allow_touching=self.allow_touching
        )


        self.Result_Management(state)

class Ray_Check(RuleCheckTwoObjects):
    def __init__(self,source,target,context):
        self.type="RayCheck"

        self.select_source = source
        self.select_target = target
        self.Select_Context_Element=context
        self.length:float=5.
        self.geom_settings = ifcopenshell.geom.settings()


    def run(self,state="Final"):
        self.tree = ifcopenshell.geom.tree()
        self.select_source.run()
        self.select_target.run()

        self.add_to_tree(self.select_source,"UB")
        self.add_to_tree(self.select_target,"UB")
        self.add_to_tree(self.Select_Context_Element)

        print("Not working, must be defined")

    def Coherence_Check(self):

        #@todo delete this function, but keep the logic of raycheck.

        #I do not respect the parameter consistency, Select should contains a list of object, but here it's only one element.

        self.tree = ifcopenshell.geom.tree()
        #self.geom_settings=ifcopenshell.geom.settings(USE_WORLD_COORDS=True)
        self.Select_Context_Element.run()

        self.add_OneObject_to_tree(self.Select_Source,"UB")
        self.add_OneObject_to_tree(self.Select_Target,"UB")

        self.add_to_tree(self.Select_Context_Element,"UB")

        def get_XYZ_placement(Object):
            Origin = ifcopenshell.util.placement.get_local_placement(Object.ObjectPlacement)
            Origin = Origin[:, 3][:3]
            Origin = (float(Origin[0]), float(Origin[1]), float(Origin[2]))
            return Origin

        source_position=get_XYZ_placement(self.Select_Source)
        target_position=get_XYZ_placement(self.Select_Target)
        source_array = np.array(source_position)
        target_array = np.array(target_position)

        direction= target_array - source_array
        distance=np.linalg.norm(direction)
        direction=tuple(direction.flatten())
        direction=(float(direction[0]/distance),float(direction[1]/distance),float(direction[2]/distance))

        results = self.tree.select_ray(source_position, direction, length=distance)
        """
        distance: Any
        dot_product: Any
        instance: Any
        normal: Any
        position: Any
        ray_distance: Any
        style_index: Any
        """

        for result in results:
            Object=result.instance.file_.by_id(result.instance.id())

            if Object==self.Select_Source:
                continue

            if Object==self.Select_Target:
                print("OK")
                return True

            if Object!=self.Select_Target:
                print("Error",Object)
                return False

class Above(RuleCheckTwoObjects):
    def __init__(self,source,target,tolerance=0.1):
        self.type="Above"
        self.tolerance:float = tolerance
        self.select_source = source
        self.select_target = target
        self.geom_settings = ifcopenshell.geom.settings()

    def run(self,state="Final"):
        self.tree = ifcopenshell.geom.tree()
        self.select_source.run()
        self.select_target.run()

        self.add_to_tree(self.select_source,"BVH")
        self.add_to_tree(self.select_target,"BVH")

        self.results = self.tree.clash_intersection_many(
            self.select_source.elements,
            self.select_target.elements,
            tolerance=self.tolerance,
            check_all=True,
        )


        self.manage_result()



#===== Complex Rule




 
