from RuleClass import (
    RuleCheckOneObject,
    RuleCheckTwoObjects,
    ClashResultOneObject,
    ClashResultTwoObjects,
)
import ifcopenshell
import multiprocessing
from clash_utils import get_extreme_faces
import shapely
from ifcopenshell.util.shape import (
    get_vertices,
)
import clash_utils
import numpy as np
from typing import Literal
from CustomOBB import create_obb_from_TopoDs_Shape_via_pca
from OCC.Core.BRepExtrema import BRepExtrema_DistShapeShape
from RuleClass import Select
import ifcopenshell.util.placement

# ===========One Object Rule
class Volume(RuleCheckOneObject):
    from ifcopenshell.util.shape import get_volume

    def __init__(self, source, volume_min, volume_max):
        super().__init__(source)
        self.type = "Volume"
        self.volume_max: float = volume_max
        self.volume_min: float = volume_min
        self.geom_settings = ifcopenshell.geom.settings()

    def run(self, state="Final"):
        self.tree = ifcopenshell.geom.tree()
        self.select_source.run()

        for ifc_file in self.select_source.dict_elements.keys():
            iterator = ifcopenshell.geom.iterator(
                self.geom_settings,
                ifc_file,
                multiprocessing.cpu_count(),
                include=self.select_source.dict_elements[ifc_file],
            )

            if iterator.initialize():
                while True:
                    shape = iterator.get()
                    geom = shape.geometry
                    volume = ifcopenshell.util.shape.get_volume(geom)
                    entity = ifc_file.by_id(shape.id)
                    if self.volume_min < volume < self.volume_max:
                        result = ClashResultOneObject(source=entity, state=True)
                        self.result.append(result)
                    else:
                        result = ClashResultOneObject(source=entity, state=False)
                        self.result.append(result)
                    if not iterator.next():
                        break

        if state == "Final":
            self.manage_result()
        else:
            self.produce_select()


class Area(RuleCheckOneObject):
    from ifcopenshell.util.shape import get_area

    def __init__(self, source, volume_min, volume_max):
        super().__init__(source)
        self.type = "Volume"
        self.volume_max: float = volume_max
        self.volume_min: float = volume_min
        self.select_source = source
        self.geom_settings = ifcopenshell.geom.settings()

    def run(self, state="Final"):
        self.tree = ifcopenshell.geom.tree()
        self.select_source.run()

        for ifc_file in self.select_source.dict_elements.keys():
            iterator = ifcopenshell.geom.iterator(
                self.geom_settings,
                ifc_file,
                multiprocessing.cpu_count(),
                include=self.select_source.dict_elements[ifc_file],
            )

            if iterator.initialize():
                while True:
                    shape = iterator.get()
                    geom = shape.geometry
                    area = ifcopenshell.util.shape.get_area(geom)
                    entity = ifc_file.by_id(shape.id)
                    if self.volume_min < area < self.volume_max:
                        result = ClashResultOneObject(source=entity, state=True)
                        self.result.append(result)
                    else:
                        result = ClashResultOneObject(source=entity, state=False)
                        self.result.append(result)
                    if not iterator.next():
                        break

        if state == "Final":
            self.manage_result()
        else:
            self.produce_select()


class TopSurface(RuleCheckOneObject):
    def __init__(self, source, surface_min, surface_max):
        super().__init__(source)
        self.type = "Volume"
        self.surface_max: float = surface_max
        self.surface_min: float = surface_min
        self.select_source = source
        self.geom_settings = ifcopenshell.geom.settings()

    def run(self, state="Final", top_or_bot="top"):
        if top_or_bot == "top":
            direction = (0.0, 0.0, 1)
        if top_or_bot == "bot":
            direction = (0.0, 0.0, -1)

        self.tree = ifcopenshell.geom.tree()
        self.select_source.run()

        for ifc_file in self.select_source.dict_elements.keys():
            iterator = ifcopenshell.geom.iterator(
                self.geom_settings,
                ifc_file,
                multiprocessing.cpu_count(),
                include=self.select_source.dict_elements[ifc_file],
            )

            if iterator.initialize():
                while True:
                    shape = iterator.get()
                    geom = shape.geometry
                    entity = ifc_file.by_id(geom.id)
                    vertices = get_vertices(geom)
                    faces = get_extreme_faces(geometry=geom, direction=direction)
                    polygons = [shapely.Polygon(vertices[face]) for face in faces]
                    unioned_polygon = shapely.ops.unary_union(polygons)

                    if self.surface_min < unioned_polygon.area < self.surface_max:
                        result = ClashResultOneObject(source=entity, state=True)
                        self.result.append(result)
                    else:
                        result = ClashResultOneObject(source=entity, state=False)
                        self.result.append(result)

                    if not iterator.next():
                        break

        if state == "Final":
            self.manage_result()
        else:
            self.produce_select()


# ====== Two Objects Rule
class Intersection(RuleCheckTwoObjects):
    def __init__(self, source, target, tolerance=0.1):
        super().__init__(source, target)
        self.type = "Intersection"
        self.tolerance: float = tolerance
        self.geom_settings = ifcopenshell.geom.settings()

    def run(self, state="Final"):
        self.tree = ifcopenshell.geom.tree()

        source_elements = []
        target_elements = []

        if state == "Final" or state == "Select":
            self.select_source.run()
            self.select_target.run()

            self.add_to_tree(self.select_source, "BVH")
            self.add_to_tree(self.select_target, "BVH")

            for file in self.select_source.dict_elements.keys():
                list = self.select_source.dict_elements[file]
                for element in list:
                    source_elements.append(element)

            for file in self.select_target.dict_elements.keys():
                list = self.select_target.dict_elements[file]
                for element in list:
                    target_elements.append(element)

        if state == "Exception":
            self.add_OneObject_to_tree(self.select_source, "BVH")
            self.add_OneObject_to_tree(self.select_target, "BVH")
            source_elements.append(self.select_source)
            target_elements.append(self.select_target)

        temp_result = self.tree.clash_intersection_many(
            source_elements,
            target_elements,
            tolerance=self.tolerance,
            check_all=True,
        )

        list_result = []  # I need to do that to avoid reusing the same result result in the different intersection.

        # @todo make a proper integration, how to deal with extra data ? (Point of entry, distance, etc...)
        for result in temp_result:
            a_file = ifcopenshell.file.from_pointer(result.a.file_pointer())
            a__object = a_file.by_id(result.a.id_)

            b__file = ifcopenshell.file.from_pointer(result.b.file_pointer())
            b_object = b__file.by_id(result.b.id_)

            # source and target are mixed up.
            if a__object in source_elements:
                source_object = a__object
                target_object = b_object
            else:
                source_object = b_object
                target_object = a__object

            list_result.append(
                ClashResultTwoObjects(
                    source=source_object, target=target_object, state=True
                )
            )

        self.result = list_result

        if state == "Final":
            self.manage_result()

        if state == "Select":
            self.produce_select()

class Clearance(RuleCheckTwoObjects):
    def __init__(self, source, target, clearance=0.05):
        super().__init__(source, target)

        self.type = "Clearance"
        self.geom_settings = ifcopenshell.geom.settings()
        self.clearance: float = 0.05
        self.check_all: bool = False

    def run(self, state="Final"):
        self.tree = ifcopenshell.geom.tree()
        self.select_source.run()
        self.select_target.run()

        source_elements = []
        target_elements = []

        # @todo update this script
        for file in self.select_source.dict_elements.keys():
            list = self.select_source.dict_elements[file]
            for element in list:
                source_elements.append(element)

        for file in self.select_target.dict_elements.keys():
            list = self.select_target.dict_elements[file]
            for element in list:
                target_elements.append(element)

        self.add_to_tree(self.select_source, "BVH")
        self.add_to_tree(self.select_target, "BVH")

        temp_result = self.tree.clash_clearance_many(
            source_elements,
            target_elements,
            clearance=self.clearance,
            check_all=self.check_all,
        )

        list_result = []  # I need to do that to avoid reusing the same result result in the different intersection.

        # @todo make a proper integration, how to deal with extra data ? (Point of entry, distance, etc...)
        for result in temp_result:
            a_file = ifcopenshell.file.from_pointer(result.a.file_pointer())
            a__object = a_file.by_id(result.a.id_)

            b__file = ifcopenshell.file.from_pointer(result.b.file_pointer())
            b_object = b__file.by_id(result.b.id_)

            # source and target are mixed up.
            if a__object in source_elements:
                source_object = a__object
                target_object = b_object
            else:
                source_object = b_object
                target_object = a__object

            self.result.append(
                ClashResultTwoObjects(
                    source=source_object, target=target_object, state=True
                )
            )

        if state == "Final":
            self.manage_result()

        if state == "Select":
            self.produce_select()


class Collision(RuleCheckTwoObjects):
    def __init__(self, source, target, tolerance=0):
        super().__init__(source, target)
        self.type = "Collision"
        self.allow_touching = False
        self.geom_settings = ifcopenshell.geom.settings()

    def run(self, state="Final"):
        self.tree = ifcopenshell.geom.tree()
        self.select_source.run()
        self.select_target.run()

        self.add_to_tree(self.select_source, "BVH")
        self.add_to_tree(self.select_target, "BVH")

        temp_result = self.tree.clash_collision_many(
            self.select_source.list_of_elements,
            self.select_target.list_of_elements,
            allow_touching=self.allow_touching,
        )

        for result in temp_result:
            a_file = ifcopenshell.file.from_pointer(result.a.file_pointer())
            a__object = a_file.by_id(result.a.id_)

            b__file = ifcopenshell.file.from_pointer(result.b.file_pointer())
            b_object = b__file.by_id(result.b.id_)

            # source and target are mixed up.
            if a__object in self.select_source.list_of_elements:
                source_object = a__object
                target_object = b_object
            else:
                source_object = b_object
                target_object = a__object

            self.result.append(
                ClashResultTwoObjects(
                    source=source_object, target=target_object, state=True
                )
            )

        if state == "Final":
            self.manage_result()

        if state == "Select":
            self.produce_select()


class Ray_Check(RuleCheckTwoObjects):
    def __init__(self, source, target, context,max_ray_length):
        super().__init__(source, target)
        self.type = "RayCheck"
        self.select_context: Select = context
        self.max_ray_length: float = max_ray_length
        self.geom_settings = ifcopenshell.geom.settings()
        #self.geom_settings=ifcopenshell.geom.settings(USE_WORLD_COORDS=True)

    def run(self, state="Final"):
        self.tree = ifcopenshell.geom.tree()
        self.select_source.run()
        self.select_target.run()


        #Watch out, we need to manually store the file info in the contect. It's not done when the RuleFile begin.
        #@todo improve this in order to update every select in every rule
        self.select_context.list_ifc_path=self.select_source.list_ifc_path
        self.select_context.list_ifc_file=self.select_source.list_ifc_file
        self.select_context.run()


        self.add_to_tree(self.select_context,"UB")
        #self.add_to_tree(self.select_source, "UB")
        #self.add_to_tree(self.select_target, "UB")
        
        self.select_source.create_list_of_element()
        self.select_target.create_list_of_element()
        self.select_context.create_list_of_element()

        for source in self.select_source.list_of_elements:
            for target in self.select_target.list_of_elements:

                source_position=clash_utils.get_XYZ_placement(source)
                target_position=clash_utils.get_XYZ_placement(target)
                source_array = np.array(source_position)
                target_array = np.array(target_position)
                        
                direction = target_array - source_array


                distance = np.linalg.norm(direction)
                if distance==0:
                    #It's the same object
                    continue

                direction = tuple(direction.flatten())
                direction = (
                    float(direction[0] / distance),
                    float(direction[1] / distance),
                    float(direction[2] / distance),
                )



                results = self.tree.select_ray(source_position, direction, length=distance)
                
                number=0
                for result in results:
                    """
                    distance: Any
                    dot_product: Any
                    instance: Any
                    normal: Any
                    position: Any
                    ray_distance: Any
                    style_index: Any
                    """
                    result_object = result.instance.file_.by_id(result.instance.id())
                    #the ray is not working properly. Something is off.
                    

                    #The clash will append when we can detect two object that are in direct view.


                    #print(result_object,target)
                    if result_object==target:
                        print(target)
                





        #self.tree.select_ray()
        # @todo Finish Ray Check
        print("Not working, must be defined")

    def Coherence_Check(self):
        # @todo delete this function, but keep the logic of raycheck.

        # I do not respect the parameter consistency, Select should contains a list of object, but here it's only one element.

        self.tree = ifcopenshell.geom.tree()
        # self.geom_settings=ifcopenshell.geom.settings(USE_WORLD_COORDS=True)
        self.Select_Context_Element.run()

        self.add_OneObject_to_tree(self.Select_Source, "UB")
        self.add_OneObject_to_tree(self.Select_Target, "UB")

        self.add_to_tree(self.Select_Context_Element, "UB")



        source_position = clash_utils.get_XYZ_placement(self.Select_Source)
        target_position = clash_utils.get_XYZ_placement(self.Select_Target)
        source_array = np.array(source_position)
        target_array = np.array(target_position)

        direction = target_array - source_array
        distance = np.linalg.norm(direction)
        direction = tuple(direction.flatten())
        direction = (
            float(direction[0] / distance),
            float(direction[1] / distance),
            float(direction[2] / distance),
        )

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
            Object = result.instance.file_.by_id(result.instance.id())

            if Object == self.Select_Source:
                continue

            if Object == self.Select_Target:
                print("OK")
                return True

            if Object != self.Select_Target:
                print("Error", Object)
                return False


ABOVE_TYPE = Literal[
    "Above_MinToMax", "Above_MinToMin", "Above_MaxToMin", "Above_MaxToMax"
]

BELOW_TYPE = Literal[
    "Below_MinToMax", "Below_MinToMin", "Below_MaxToMin", "Below_MaxToMax"
]


class Above(RuleCheckTwoObjects):
    def __init__(self, source, target, above_type: ABOVE_TYPE, tolerance=0.1):
        super().__init__(source, target)
        self.type = above_type
        self.tolerance: float = tolerance
        self.geom_settings = ifcopenshell.geom.settings(USE_WORLD_COORDS=True)

    def run(self, state="Final"):
        self.tree = ifcopenshell.geom.tree()
        self.select_source.run()
        self.select_target.run()

        sources_faces = []
        targets_faces = []

        if "MinTo" in self.type:
            source_direction = (0.0, 0.0, -1.0)
        else:
            source_direction = (0.0, 0.0, 1.0)

        if "ToMin" in self.type:
            target_direction = (0.0, 0.0, -1.0)
        else:
            target_direction = (0.0, 0.0, 1.0)

        # Check the extrem face of the source
        for ifc_file in self.select_source.dict_elements.keys():
            iterator = ifcopenshell.geom.iterator(
                self.geom_settings,
                ifc_file,
                multiprocessing.cpu_count(),
                include=self.select_source.dict_elements[ifc_file],
            )

            if iterator.initialize():
                while True:
                    shape = iterator.get()
                    geom = shape.geometry
                    extrem_faces = clash_utils.get_extreme_faces(
                        geometry=geom, direction=source_direction
                    )
                    vertices = get_vertices(geom)
                    dict = {
                        "entity": ifc_file.by_id(shape.id),
                        "vertices": vertices,
                        "extrem_faces": extrem_faces,
                    }
                    sources_faces.append(dict)

                    if not iterator.next():
                        break

        # Check the extrem face of the target
        for ifc_file in self.select_target.dict_elements.keys():
            iterator = ifcopenshell.geom.iterator(
                self.geom_settings,
                ifc_file,
                multiprocessing.cpu_count(),
                include=self.select_target.dict_elements[ifc_file],
            )

            if iterator.initialize():
                while True:
                    shape = iterator.get()
                    geom = shape.geometry
                    extrem_faces = clash_utils.get_extreme_faces(
                        geometry=geom, direction=target_direction
                    )
                    vertices = get_vertices(geom)
                    dict = {
                        "entity": ifc_file.by_id(shape.id),
                        "vertices": vertices,
                        "extrem_faces": extrem_faces,
                    }
                    targets_faces.append(dict)

                    if not iterator.next():
                        break

        list_result = []

        # Check if part of extrem faces are close to each other
        for source_faces in sources_faces:
            for target_faces in targets_faces:
                for source_face in source_faces["extrem_faces"]:
                    s0 = source_faces["vertices"][source_face[0]]
                    s1 = source_faces["vertices"][source_face[1]]
                    s2 = source_faces["vertices"][source_face[2]]
                    source_center = (s0 + s1 + s2) / 3
                    s = [s0, s1, s2]

                    min_distance_found = None
                    selected_result = None

                    for taget_face in target_faces["extrem_faces"]:
                        t0 = target_faces["vertices"][taget_face[0]]
                        t1 = target_faces["vertices"][taget_face[1]]
                        t2 = target_faces["vertices"][taget_face[2]]
                        target_center = (t0 + t1 + t2) / 3

                        t = [t0, t1, t2]

                        dist = clash_utils.min_distance_two_faces(s, t)

                        # The target face must be above the source.
                        check_above = (source_center - target_center)[2]
                        if check_above > 0:
                            continue

                        # @todo If the object is above but with an offset in x or y, it will be detected as well.

                        # we only select the worst case scenario.
                        if dist["distance"] < self.tolerance:
                            if min_distance_found is None:
                                min_distance_found = dist["distance"]
                                selected_result = {
                                    "source": source_faces["entity"],
                                    "target": target_faces["entity"],
                                }
                                continue
                            if min_distance_found < dist["distance"]:
                                min_distance_found = dist["distance"]
                                selected_result = {
                                    "source": source_faces["entity"],
                                    "target": target_faces["entity"],
                                }

                    if selected_result is not None:
                        list_result.append(
                            ClashResultTwoObjects(
                                source=selected_result["source"],
                                target=selected_result["target"],
                                state=True,
                            )
                        )

        self.result = list_result

        if state == "Final":
            self.manage_result()

        if state == "Select":
            self.produce_select()

class Below(RuleCheckTwoObjects): #@todo Check this rule
    def __init__(self, source, target, above_type: BELOW_TYPE, tolerance=0.1):
        super().__init__(source, target)
        self.type = above_type
        self.tolerance: float = tolerance
        self.geom_settings = ifcopenshell.geom.settings(USE_WORLD_COORDS=True)

    def run(self, state="Final"):
        self.tree = ifcopenshell.geom.tree()
        self.select_source.run()
        self.select_target.run()

        sources_faces = []
        targets_faces = []

        if "MinTo" in self.type:
            source_direction = (0.0, 0.0, -1.0)
        else:
            source_direction = (0.0, 0.0, 1.0)

        if "ToMin" in self.type:
            target_direction = (0.0, 0.0, -1.0)
        else:
            target_direction = (0.0, 0.0, 1.0)

        # Check the extrem face of the source
        for ifc_file in self.select_source.dict_elements.keys():
            iterator = ifcopenshell.geom.iterator(
                self.geom_settings,
                ifc_file,
                multiprocessing.cpu_count(),
                include=self.select_source.dict_elements[ifc_file],
            )

            if iterator.initialize():
                while True:
                    shape = iterator.get()
                    geom = shape.geometry
                    extrem_faces = clash_utils.get_extreme_faces(
                        geometry=geom, direction=source_direction
                    )
                    vertices = get_vertices(geom)
                    dict = {
                        "entity": ifc_file.by_id(shape.id),
                        "vertices": vertices,
                        "extrem_faces": extrem_faces,
                    }
                    sources_faces.append(dict)

                    if not iterator.next():
                        break

        # Check the extrem face of the target
        for ifc_file in self.select_target.dict_elements.keys():
            iterator = ifcopenshell.geom.iterator(
                self.geom_settings,
                ifc_file,
                multiprocessing.cpu_count(),
                include=self.select_target.dict_elements[ifc_file],
            )

            if iterator.initialize():
                while True:
                    shape = iterator.get()
                    geom = shape.geometry
                    extrem_faces = clash_utils.get_extreme_faces(
                        geometry=geom, direction=target_direction
                    )
                    vertices = get_vertices(geom)
                    dict = {
                        "entity": ifc_file.by_id(shape.id),
                        "vertices": vertices,
                        "extrem_faces": extrem_faces,
                    }
                    targets_faces.append(dict)

                    if not iterator.next():
                        break

        list_result = []

        # Check if part of extrem faces are close to each other
        for source_faces in sources_faces:
            for target_faces in targets_faces:
                for source_face in source_faces["extrem_faces"]:
                    s0 = source_faces["vertices"][source_face[0]]
                    s1 = source_faces["vertices"][source_face[1]]
                    s2 = source_faces["vertices"][source_face[2]]
                    source_center = (s0 + s1 + s2) / 3
                    s = [s0, s1, s2]

                    min_distance_found = None
                    selected_result = None

                    for taget_face in target_faces["extrem_faces"]:
                        t0 = target_faces["vertices"][taget_face[0]]
                        t1 = target_faces["vertices"][taget_face[1]]
                        t2 = target_faces["vertices"][taget_face[2]]
                        target_center = (t0 + t1 + t2) / 3

                        t = [t0, t1, t2]

                        dist = clash_utils.min_distance_two_faces(s, t)

                        # The target face must be below the source.
                        check_below = (source_center - target_center)[2]
                        if check_below < 0:
                            continue

                        # @todo If the object is above but with an offset in x or y, it will be detected as well.

                        # we only select the worst case scenario.
                        if dist["distance"] < self.tolerance:
                            if min_distance_found is None:
                                min_distance_found = dist["distance"]
                                selected_result = {
                                    "source": source_faces["entity"],
                                    "target": target_faces["entity"],
                                }
                                continue
                            if min_distance_found < dist["distance"]:
                                min_distance_found = dist["distance"]
                                selected_result = {
                                    "source": source_faces["entity"],
                                    "target": target_faces["entity"],
                                }

                    if selected_result is not None:
                        list_result.append(
                            ClashResultTwoObjects(
                                source=selected_result["source"],
                                target=selected_result["target"],
                                state=True,
                            )
                        )

        self.result = list_result

        if state == "Final":
            self.manage_result()

        if state == "Select":
            self.produce_select()

class Template(RuleCheckTwoObjects):
    def __init__(self, source, target, tolerance=0.1):
        super().__init__(source, target)
        self.tolerance: float = tolerance
        self.geom_settings = ifcopenshell.geom.settings(USE_WORLD_COORDS=False)

    def run(self, state="Final"):

        if state == "Final":
            self.manage_result()

        if state == "Select":
            self.produce_select()


class OBB_Above(RuleCheckTwoObjects):
    def __init__(self, source, target, tolerance):
        super().__init__(source, target)
        self.tolerance: float = tolerance
        self.geom_settings = ifcopenshell.geom.settings()
        self.geom_settings.set(self.geom_settings.USE_PYTHON_OPENCASCADE, True)

    def run(self, state="Final"):
        self.tree = ifcopenshell.geom.tree()
        self.select_source.run()
        self.select_target.run()

        # Create OBBs for source objects (these serve as detection zones)
        source_obbs = []
        for ifc_file in self.select_source.dict_elements.keys():
            iterator = ifcopenshell.geom.iterator(
                self.geom_settings,
                ifc_file,
                multiprocessing.cpu_count(),
                include=self.select_source.dict_elements[ifc_file],
            )

            if iterator.initialize():
                while True:
                    shape = iterator.get()
                    geom = shape.geometry
                    entity = ifc_file.by_id(shape.data.id)

                    # Create OBB for the source object (detection zone)
                    obb = create_obb_from_TopoDs_Shape_via_pca(geom)
                    clash_obb = obb.detach_top_by_extrude(self.tolerance)
                    compound = clash_obb.to_TopoDS_Compound()
                    source_obbs.append({"entity": entity, "geom": compound})

                    if not iterator.next():
                        break

        # Get target geometries
        target_geoms = []
        for ifc_file in self.select_target.dict_elements.keys():
            # self.geom_settings.set(self.geom_settings.USE_PYTHON_OPENCASCADE,True)
            iterator = ifcopenshell.geom.iterator(
                self.geom_settings,
                ifc_file,
                multiprocessing.cpu_count(),
                include=self.select_target.dict_elements[ifc_file],
            )

            if iterator.initialize():
                while True:
                    shape = iterator.get()
                    geom = shape.geometry
                    entity = ifc_file.by_id(shape.data.id)

                    target_geoms.append({"entity": entity, "geom": geom})

                    if not iterator.next():
                        break

        # Check for clashes between source OBBs (detection zones) and target geometries
        for source_data in source_obbs:
            for target_data in target_geoms:
                source_geom = source_data["geom"]
                target_geom = target_data["geom"]

                # Calculate distance between OBB and geometry
                dist_tool = BRepExtrema_DistShapeShape()
                dist_tool.LoadS1(source_geom)
                dist_tool.LoadS2(target_geom)
                dist_tool.Perform()
                distance = dist_tool.Value()

                # If they touch (distance <= tolerance) and target is above source, it's a clash
                if distance <= 1e-6:
                    result = ClashResultTwoObjects(
                        source=source_data["entity"],
                        target=target_data["entity"],
                        state=False,
                    )
                    self.result.append(result)

        if state == "Final":
            self.manage_result()

        if state == "Select":
            self.produce_select()

    def _display_specific(self):
        from OCC.Core.AIS import AIS_Shape
        from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
        
        settings = ifcopenshell.geom.settings()
        settings.set("USE_WORLD_COORDS", True)
        #settings.set("use-python-opencascade", True)

        # Check the extrem face of the source
        for ifc_file in self.select_source.dict_elements.keys():
            iterator = ifcopenshell.geom.iterator(
                self.geom_settings,
                ifc_file,
                multiprocessing.cpu_count(),
                include=self.select_source.dict_elements[ifc_file],
            )

            if iterator.initialize():
                while True:
                    shape = iterator.get()
                    geom = shape.geometry


                    obb = create_obb_from_TopoDs_Shape_via_pca(geom)
                    clash_obb = obb.detach_top_by_extrude(self.tolerance)
                    compound = clash_obb.to_TopoDS_Compound()
                    ais_shape=AIS_Shape(compound)
                    green_color = Quantity_Color(0.0, 1.0, 0.0, Quantity_TOC_RGB)
                    ais_shape.SetColor(green_color)
                    ais_shape.SetTransparency(0.2)
                    self.display.Context.Display(ais_shape, True)


                    if not iterator.next():
                        break

class OBB_Below(RuleCheckTwoObjects):
    def __init__(self, source, target, tolerance):
        super().__init__(source, target)
        self.tolerance: float = tolerance
        self.geom_settings = ifcopenshell.geom.settings()
        self.geom_settings.set(self.geom_settings.USE_PYTHON_OPENCASCADE, True)

    def run(self, state="Final"):
        self.tree = ifcopenshell.geom.tree()
        self.select_source.run()
        self.select_target.run()

        # Create OBBs for source objects (these serve as detection zones)
        source_obbs = []
        for ifc_file in self.select_source.dict_elements.keys():
            iterator = ifcopenshell.geom.iterator(
                self.geom_settings,
                ifc_file,
                multiprocessing.cpu_count(),
                include=self.select_source.dict_elements[ifc_file],
            )

            if iterator.initialize():
                while True:
                    shape = iterator.get()
                    geom = shape.geometry
                    entity = ifc_file.by_id(shape.data.id)

                    # Create OBB for the source object (detection zone)
                    obb = create_obb_from_TopoDs_Shape_via_pca(geom)
                    clash_obb = obb.detach_bottom_by_extrude(self.tolerance)
                    compound = clash_obb.to_compound()
                    source_obbs.append({"entity": entity, "geom": compound})

                    if not iterator.next():
                        break

        # Get target geometries
        target_geoms = []
        for ifc_file in self.select_target.dict_elements.keys():
            # self.geom_settings.set(self.geom_settings.USE_PYTHON_OPENCASCADE,True)
            iterator = ifcopenshell.geom.iterator(
                self.geom_settings,
                ifc_file,
                multiprocessing.cpu_count(),
                include=self.select_target.dict_elements[ifc_file],
            )

            if iterator.initialize():
                while True:
                    shape = iterator.get()
                    geom = shape.geometry
                    entity = ifc_file.by_id(shape.data.id)

                    target_geoms.append({"entity": entity, "geom": geom})

                    if not iterator.next():
                        break

        # Check for clashes between source OBBs (detection zones) and target geometries
        for source_data in source_obbs:
            for target_data in target_geoms:
                source_geom = source_data["geom"]
                target_geom = target_data["geom"]

                # Calculate distance between OBB and geometry
                dist_tool = BRepExtrema_DistShapeShape()
                dist_tool.LoadS1(source_geom)
                dist_tool.LoadS2(target_geom)
                dist_tool.Perform()
                distance = dist_tool.Value()

                # If they touch (distance <= tolerance) and target is above source, it's a clash
                if distance <= 1e-6:
                    result = ClashResultTwoObjects(
                        source=source_data["entity"],
                        target=target_data["entity"],
                        state=False,
                    )
                    self.result.append(result)

        if state == "Final":
            self.manage_result()

        if state == "Select":
            self.produce_select()

DIRECTION_METHOD = Literal[
    "Wide", "Narrow"]

class OBB_Front_And_Back(RuleCheckTwoObjects):
    def __init__(self, source, target, tolerance,method:DIRECTION_METHOD):
        super().__init__(source, target)
        self.tolerance: float = tolerance
        self.geom_settings = ifcopenshell.geom.settings()
        self.geom_settings.set(self.geom_settings.USE_PYTHON_OPENCASCADE, True)
        self.direction_method=method

    def run(self, state="Final"):
        self.tree = ifcopenshell.geom.tree()
        self.select_source.run()
        self.select_target.run()

        # Create OBBs for source objects (these serve as detection zones)
        source_obbs = []
        for ifc_file in self.select_source.dict_elements.keys():
            iterator = ifcopenshell.geom.iterator(
                self.geom_settings,
                ifc_file,
                multiprocessing.cpu_count(),
                include=self.select_source.dict_elements[ifc_file],
            )

            if iterator.initialize():
                while True:
                    shape = iterator.get()
                    geom = shape.geometry
                    entity = ifc_file.by_id(shape.data.id)

                    # Create OBB for the source object (detection zone)
                    obb = create_obb_from_TopoDs_Shape_via_pca(geom)
                    main_directions=obb.get_two_main_direction_OBB_shape(self.direction_method)
                    clash_obb_1=obb.detach_side_by_extrude(main_directions[0],self.tolerance)
                    clash_obb_2=obb.detach_side_by_extrude(main_directions[0],self.tolerance)

                    compound_1 = clash_obb_1.to_compound()
                    compound_2 = clash_obb_2.to_compound()
                    source_obbs.append({"entity": entity, "geom": compound_1})
                    source_obbs.append({"entity": entity, "geom": compound_2})

                    if not iterator.next():
                        break

        # Get target geometries
        target_geoms = []
        for ifc_file in self.select_target.dict_elements.keys():
            # self.geom_settings.set(self.geom_settings.USE_PYTHON_OPENCASCADE,True)
            iterator = ifcopenshell.geom.iterator(
                self.geom_settings,
                ifc_file,
                multiprocessing.cpu_count(),
                include=self.select_target.dict_elements[ifc_file],
            )

            if iterator.initialize():
                while True:
                    shape = iterator.get()
                    geom = shape.geometry
                    entity = ifc_file.by_id(shape.data.id)

                    target_geoms.append({"entity": entity, "geom": geom})

                    if not iterator.next():
                        break

        # Check for clashes between source OBBs (detection zones) and target geometries
        for source_data in source_obbs:
            for target_data in target_geoms:
                source_geom = source_data["geom"]
                target_geom = target_data["geom"]

                # Calculate distance between OBB and geometry
                dist_tool = BRepExtrema_DistShapeShape()
                dist_tool.LoadS1(source_geom)
                dist_tool.LoadS2(target_geom)
                dist_tool.Perform()
                distance = dist_tool.Value()

                # If they touch (distance <= tolerance) and target is above source, it's a clash
                if distance <= 1e-6:
                    result = ClashResultTwoObjects(
                        source=source_data["entity"],
                        target=target_data["entity"],
                        state=False,
                    )
                    self.result.append(result)

        if state == "Final":
            self.manage_result()

        if state == "Select":
            self.produce_select()


# ===== Complex Rule
