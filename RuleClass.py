from typing import Literal, TypedDict, Union
import Select
from abc import abstractmethod
from IfcOpenShell.src.ifctester.ifctester.facet import Facet
from ifctester.facet import Entity,Attribute
import ifcopenshell.geom
import time
from ifcclash.ifcclash import ClashSource
import multiprocessing
import numpy as np
import ifcopenshell.util.placement


@abstractmethod
class RuleCheck():

    id:str

    Select_Source:Select.Select=None
    Select_Target:Select.Select=None

    result:list = []

    CheckCoherence:Select.Select=None

    #Those select are used only if the rule is the last one.
    Select_Criticity: list[Select.Select] = []
    Select_Actor: list[Select.Select] = []
    Select_Regroup: list[Select.Select] = []

    def add_to_tree(self,Select,TypeOfTree):
        for ifc_file in Select.dict_elements.keys():
            iterator = ifcopenshell.geom.iterator(self.geom_settings, ifc_file, multiprocessing.cpu_count(),include=Select.dict_elements[ifc_file])

        if iterator.initialize():
            while True:
                if TypeOfTree=="BVH":
                    self.tree.add_element(iterator.get())
                if TypeOfTree=="UB":
                    self.tree.add_element(iterator.get_native())

                shape = iterator.get()
                if not iterator.next():
                    break

    def add_OneObject_to_tree(self,Object,TypeOfTree):

        iterator = ifcopenshell.geom.iterator(self.geom_settings, Object.file, multiprocessing.cpu_count(),include=[Object])

        assert iterator.initialize()
        while True:
            if TypeOfTree == "BVH":
                self.tree.add_element(iterator.get())
            if TypeOfTree == "UB":
                self.tree.add_element(iterator.get_native())

            shape = iterator.get()
            if not iterator.next():
                break

    def Result_Management(self,state):
        if state == "Select":
            return True
        for select in self.Select_Criticity:
            select.Run()
            #@todo Finish the script to assign criticy to each result
            #Assign the criticity

        for select in self.Select_Actor:
            select.Run()
            # @todo Finish the script to assign an actor to each result
            #Assign an actor

    def Check_Coherence(self):

        if self.CheckCoherence is None:
            return True

class Intersection(RuleCheck):
    def __init__(self,source,target,tolerance=0.1):
        self.type="Intersection"
        self.tolerance:float = tolerance
        self.Select_Source = source
        self.Select_Target = target
        self.geom_settings = ifcopenshell.geom.settings()

    def Run(self,state="Final"):
        self.tree = ifcopenshell.geom.tree()
        self.Select_Source.Run()
        self.Select_Target.Run()

        self.add_to_tree(self.Select_Source,"BVH")
        self.add_to_tree(self.Select_Target,"BVH")

        self.results = self.tree.clash_intersection_many(
            self.Select_Source.elements,
            self.Select_Target.elements,
            tolerance=self.tolerance,
            check_all=True,
        )


        #self.Result_Management(state)

class Clearance(RuleCheck):
    def __init__(self,source,target,clearance=0.05):
        self.type="Clearance"
        self.Select_Source = source
        self.Select_Target = target
        self.geom_settings = ifcopenshell.geom.settings()
        self.clearance: float = 0.05
        self.check_all: bool = False

    def Run(self,state="Final"):
        self.tree = ifcopenshell.geom.tree()
        self.Select_Source.Run()
        self.Select_Target.Run()

        self.add_to_tree(self.Select_Source,"BVH")
        self.add_to_tree(self.Select_Target,"BVH")

        self.results = self.tree.clash_clearance_many(
            self.Select_Source.elements,
            self.Select_Target.elements,
            clearance=self.clearance,
            check_all=self.check_all,
        )

        self.Result_Management(state)

class Collision(RuleCheck):
    def __init__(self,source,target,tolerance=0):
        self.type="Collision"
        self.allow_touching = False
        self.Select_Source = source
        self.Select_Target = target
        self.geom_settings = ifcopenshell.geom.settings()

    def Run(self,state="Final"):
        self.tree = ifcopenshell.geom.tree()
        self.Select_Source.Run()
        self.Select_Target.Run()

        self.add_to_tree(self.Select_Source,"BVH")
        self.add_to_tree(self.Select_Target,"BVH")

        self.results = self.tree.clash_collision_many(
            self.Select_Source.elements,
            self.Select_Target.elements,
            allow_touching=self.allow_touching
        )


        self.Result_Management(state)

class Ray_Check(RuleCheck):
    def __init__(self,source,target,context):
        self.type="Collision"

        self.Select_Source = source
        self.Select_Target = target
        self.Select_Context_Element=context
        self.length:float=5.
        self.geom_settings = ifcopenshell.geom.settings()


    def Run(self,state="Final"):
        self.tree = ifcopenshell.geom.tree()
        self.Select_Source.Run()
        self.Select_Target.Run()
        self.Select_Context_Element.Run()

        self.add_to_tree(self.Select_Source,"UB")
        self.add_to_tree(self.Select_Target,"UB")
        self.add_to_tree(self.Select_Context_Element)

        print("Not working, must be defined")

    def Coherence_Check(self):

        #I do not respect the parameter consistency, Select should contains a list of object, but here it's only one element.

        self.tree = ifcopenshell.geom.tree()
        #self.geom_settings=ifcopenshell.geom.settings(USE_WORLD_COORDS=True)
        self.Select_Context_Element.Run()

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

if __name__ == '__main__':
    pass



