from __future__ import annotations

from typing import List

import ifcopenshell
from ifctester import ids
from ifctester.facet import Facet
from typing import Literal, TypedDict, Union

from abc import abstractmethod

from ifctester.facet import Entity,Attribute
import ifcopenshell.geom
import time
from ifcclash.ifcclash import ClashSource
import multiprocessing
import numpy as np
import ifcopenshell.util.placement


class Select:
    def __init__(self):
        self.id: str = "AZE"
        self.list_ifc_path: list[str] = []
        self.list_ifc_file: list[ifcopenshell.file] = []
        self.dict_elements: dict = {}
        self.elements: list[ifcopenshell.entity_instance] = []

    def run(self):
        pass

    def Load_File(self):
        for path in self.list_ifc_path:
            self.list_ifc_file.append(ifcopenshell.open(path))

    def initialize_dict(self):
        Dict = dict()
        for onefile in self.list_ifc_file:
            Dict[onefile] = None
        self.dict_elements = Dict

class Select_Facet(Select):
    def __init__(self, ClassificationType="Facet"):
        super().__init__()
        self.type: str = ClassificationType
        self.applicability: List[Facet] = []
        self.classification_name: str = ""

    def Run(self):
        self.Load_File()
        print("state self", self.__dict__)
        self.initialize_dict()

        print("the list", self.list_ifc_file)

        for onefile in self.list_ifc_file:
            for one_applicability in self.applicability:
                if self.dict_elements[onefile] is None:
                    result = one_applicability.filter(onefile)
                    self.dict_elements[onefile] = result
                else:
                    self.dict_elements[onefile] = one_applicability.filter(onefile, self.dict_elements[onefile])

class Select_Rule(Select):
    def __init__(self):
        super().__init__()
        from RuleClass import RuleCheck

        self.type: str = "Rule"
        self.rule: RuleCheck
        self.action_type: str = 1

        # can be
        # 1 - Select source in the list => Only one implemented
        # 2 - Select source not in the list
        # 3 - Select target in the list
        # 4 - Select target not in the list

    def Run(self):
        self.rule.Run(state="Select")
        self.Produce_Select()

    def Produce_Select(self):
        for result in self.rule.results:
            Entity_A = result.a
            GUID_Entity_A = Entity_A.get_argument(
                0
            )  # There must be a clean way to do that. From the result of the clash, i want to update the select elements.

            for OneElement in self.rule.Select_Source.elements:
                if OneElement.GlobalId == GUID_Entity_A:
                    self.elements.append(OneElement)
                    if OneElement.file in self.dict_elements:
                        self.dict_elements[OneElement.file].append(OneElement)
                    else:
                        self.dict_elements[OneElement.file] = [OneElement]

            Entity_b = result.b
            GUID_Entity_b = Entity_b.get_argument(
                0
            )  # There must be a clean way to do that

            for OneElement in self.rule.Select_Source.elements:
                if OneElement.GlobalId == GUID_Entity_b:
                    self.elements.append(OneElement)
                    if OneElement.file in self.dict_elements:
                        self.dict_elements[OneElement.file].append(OneElement)
                    else:
                        self.dict_elements[OneElement.file] = [OneElement]

        self.elements = list(set(self.elements))


@abstractmethod
class RuleCheck():

    id:str

    select_source:Select.Select=None
    
    result:list = []

    #Those select are used only if the rule is the last one.
    select_criticity: list[Select.Select] = []
    select_actor: list[Select.Select] = []


    def add_to_tree(self,Select,type_of_tree):
        for ifc_file in Select.dict_elements.keys():
            iterator = ifcopenshell.geom.iterator(self.geom_settings, ifc_file, multiprocessing.cpu_count(),include=Select.dict_elements[ifc_file])

        if iterator.initialize():
            while True:
                if type_of_tree=="BVH":
                    self.tree.add_element(iterator.get())
                if type_of_tree=="UB":
                    self.tree.add_element(iterator.get_native())

                shape = iterator.get()
                if not iterator.next():
                    break

    def add_OneObject_to_tree(self,Object,type_of_tree):

        iterator = ifcopenshell.geom.iterator(self.geom_settings, Object.file, multiprocessing.cpu_count(),include=[Object])

        assert iterator.initialize()
        while True:
            if type_of_tree == "BVH":
                self.tree.add_element(iterator.get())
            if type_of_tree == "UB":
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

class RuleCheckOneObject(RuleCheck):
    def __init__(self):
        super().__init__()

class RuleCheckTwoObject(RuleCheck):
    def __init__(self):
        super().__init__()
        select_target:Select.Select=None

class RuleCheckComplex(RuleCheck):
    def __init__(self):
        super().__init__()
        select_target:Select.Select=None


class Clash_Result():
    id:str
    source:list[ifcopenshell.entity_instance]=[]
    
    status:str=None
    criticity:str=None
    actor:str=None

class Clash_Result_One_Object(Clash_Result):
    def __init__(self):
        super().__init__()

class Clash_Result_Two_Objects(Clash_Result):
    def __init__(self):
        super().__init__()
        target:list[ifcopenshell.entity_instance]=[]
        context:list[ifcopenshell.entity_instance]=[]


class Clash_Result_Complex(Clash_Result):
    def __init__(self):
        super().__init__()
        target:list[ifcopenshell.entity_instance]=[]
        context:list[ifcopenshell.entity_instance]=[]

if __name__ == "__main__":
    Chemin = "Ifc_Model/Ifc2x3_Duplex_Architecture.ifc"
    OneSelect_Facet = Select_Facet()
    Wall_Facet = ids.Entity(name="IFCWALL")
    OneSelect_Facet.applicability = [Wall_Facet]

    OneSelect_Facet.list_ifc_path = [Chemin]


