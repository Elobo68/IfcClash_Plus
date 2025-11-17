from __future__ import annotations

from typing import List

import ifcopenshell
from ifctester import ids
from ifctester.facet import (
    Facet,
    Entity,
    Property,
    Attribute,
    Classification,
    PartOf,
    Material,
)
from typing import Literal, TypedDict, Union

from abc import abstractmethod

from ifctester.facet import Entity, Attribute
import ifcopenshell.geom
import time
from ifcclash.ifcclash import ClashSource
import multiprocessing
import numpy as np
import ifcopenshell.util.placement


class RuleFile:
    def __init__(self):
        self.id: str = ""
        self.list_ifc_path: list[str] = []
        self.list_ifc_file: list[ifcopenshell.file] = []
        self.contains: list = []  # Union of folder or Rule

        self.list_of_results: list[ClashResult] = []
        self.path_to_save: str = None

    def run(self):
        for rulecheck_or_folder in self.contains:
            rulecheck_or_folder.run()


class RuleFolder:
    def __init__(self):
        self.id: str = "AZE"
        self.activation_rule: str = True
        self.activation_case: str = "ALLTRUE"
        self.contains: list = []  # Union of folder or Rule

    def check_Activation_Rule(self):
        if self.activation_rule is None:
            return True
        # @todo do the activation rule
        return True

    def run(self):
        if self.check_Activation_Rule():
            for rulecheck_or_folder in self.contains:
                rulecheck_or_folder.run()
        else:
            return False


class Select:
    def __init__(self):
        self.id: str = "AZE"
        self.list_ifc_path: list[str] = []
        self.list_ifc_file: list[ifcopenshell.file] = []
        self.dict_elements: dict = {}

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


class SelectFacet(Select):
    def __init__(self, ClassificationType="Facet"):
        super().__init__()
        self.type: str = ClassificationType
        self.applicability: List[Facet] = []
        self.classification_name: str = ""

    def run(self):
        self.Load_File()
        self.initialize_dict()

        for onefile in self.list_ifc_file:
            for one_applicability in self.applicability:
                if self.dict_elements[onefile] is None:
                    result = one_applicability.filter(onefile)
                    self.dict_elements[onefile] = result
                else:
                    self.dict_elements[onefile] = one_applicability.filter(
                        onefile, self.dict_elements[onefile]
                    )


class SelectRule(Select):
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

    def run(self,state="Select"):
        self.rule.run(state)
        self.dict_elements = self.rule.produce_select()

    def produce_select(self):
        print("Remake this whole function, not working")
        for result in self.rule.results:
            Entity_A = result.a
            GUID_Entity_A = Entity_A.get_argument(
                0
            )  # There must be a clean way to do that. From the result of the clash, i want to update the select elements.

            for OneElement in self.rule.Select_Source.elements:
                if OneElement.GlobalId == GUID_Entity_A:
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
                    if OneElement.file in self.dict_elements:
                        self.dict_elements[OneElement.file].append(OneElement)
                    else:
                        self.dict_elements[OneElement.file] = [OneElement]


@abstractmethod
class RuleCheck:
    id: str = None
    type: str = None

    tree: list = None  # @todo Determine the exact

    result: list[ClashResult] = []  

    # Those select are used only if the rule is the last one.
    select_source: Select = None
    select_grouping: SelectFacet = None
    select_criticity: list[Select] = []
    select_actor: list[Select] = []

    def add_to_tree(self, Select, type_of_tree):

        for ifc_file in Select.dict_elements.keys():
            iterator = ifcopenshell.geom.iterator(
                self.geom_settings,
                ifc_file,
                multiprocessing.cpu_count(),
                include=Select.dict_elements[ifc_file],
            )

        if iterator.initialize():
            while True:
                if type_of_tree == "BVH":
                    self.tree.add_element(iterator.get())
                if type_of_tree == "UB":
                    self.tree.add_element(iterator.get_native())

                shape = iterator.get()
                if not iterator.next():
                    break

    def add_OneObject_to_tree(self, Object, type_of_tree):
        iterator = ifcopenshell.geom.iterator(
            self.geom_settings,
            Object.file,
            multiprocessing.cpu_count(),
            include=[Object],
        )

        assert iterator.initialize()
        while True:
            if type_of_tree == "BVH":
                self.tree.add_element(iterator.get())
            if type_of_tree == "UB":
                self.tree.add_element(iterator.get_native())

            shape = iterator.get()
            if not iterator.next():
                break

    def to_bcf():
        print("Reuse Ifcopenshell")




class RuleCheckOneObject(RuleCheck):
    def __init__(self):
        super().__init__()
        # To remember exception has no need in One Object because you can chains the rule to get the same result.

    def produce_select(self):
        dict_return = {}
        for oneresult in self.result:
            if oneresult.status:  # we gave back the True value of result.
                if oneresult.source.file in dict_return:
                    dict_return[oneresult.source.file].append(oneresult.source)
                else:
                    dict_return[oneresult.source.file] = [oneresult.source]

        return dict_return

    def run_grouping(self):
        def grouping_by_entity(self):
            for oneobject in self.result:
                oneobject.source_group = oneobject.source.is_a()

        def grouping_by_property(self):
            print("TODO PROPERTY")
            ...

        def grouping_by_attribute(self):
            print("TODO ATTRIBUTE")
            ...

        def grouping_by_part_of(self):
            print("TODO PART OF")
            ...

        def grouping_by_material(self):
            print("TODO MATERIAL")
            ...

        def grouping_by_classification(self):
            print("TODO CLASSIFICATION")
            ...

        def grouping_by_closeness(self):
            print("TODO CLOSENESS")
            ...  # reuse function of IfcClash

        if self.select_grouping is None:
            return 0

        if self.select_grouping == "ENTITY":
            grouping_by_entity(self)

        if isinstance(self.select_grouping, Property):
            grouping_by_property(self)

        if isinstance(self.select_grouping, Attribute):
            grouping_by_attribute(self)

        if isinstance(self.select_grouping, PartOf):
            grouping_by_part_of(self)

        if isinstance(self.select_grouping, Material):
            grouping_by_material(self)

        if self.select_grouping == "CLOSENESS":
            grouping_by_closeness(self)

        if isinstance(self.select_grouping, Classification):
            grouping_by_classification(self)

        ...

    def run_criticity(self):
        if self.select_criticity == []:
            return None

        for result in self.result:
            filter_flag = True
            for Facet in self.select_criticity.applicability:
                ListFiltering = Facet.filter(
                    ifc_file=result.source.file, elements=result.source
                )

                if ListFiltering == []:
                    filter_flag = False
                    break

            if filter_flag:
                result.criticity.append(self.select_criticity.classification_name)

    def run_actor(self):
        if self.select_actor == []:
            return None

        for result in self.result:
            filter_flag = True
            for Facet in self.select_actor.applicability:
                ListFiltering = Facet.filter(
                    ifc_file=result.source.file, elements=result.source
                )

                if ListFiltering == []:
                    filter_flag = False
                    break

            if filter_flag:
                result.actor.append(self.select_actor.classification_name)

    def manage_result(self):
        self.run_grouping()
        self.run_criticity()
        self.run_actor()

class RuleCheckTwoObjects(RuleCheck):
    def __init__(self):
        super().__init__()
        self.select_target: Select = None
        self.select_focus_filter: Select = None
        self.select_exception: list[SelectRule] = []
        self.select_must_rule: str = None  # @todo Create the must rule for the Two Objects

    def produce_select(self):
        #@todo pass the fail or success element, 
        dict_return = {}
        for oneresult in self.result:
            if oneresult.status:  # we gave back the True value of result.
                if oneresult.source.file in dict_return:
                    dict_return[oneresult.source.file].append(oneresult.source)
                else:
                    dict_return[oneresult.source.file] = [oneresult.source]

        return dict_return

    def run_grouping(self):
        def grouping_by_entity(self):
            for oneobject in self.result:
                oneobject.source_group = oneobject.source.is_a()

        def grouping_by_property(self):
            print("TODO")
            ...

        def grouping_by_attribute(self):
            print("TODO")
            ...

        def grouping_by_part_of(self):
            print("TODO")
            ...

        def grouping_by_material(self):
            print("TODO")
            ...

        def grouping_by_closeness(self):
            print("TODO")
            ...  # reuse function of IfcClash

    def run_criticity(self):
        print("TODO ACTOR")

    def run_actor(self):
        print("TODO ACTOR")

    def run_exception(self):
        list_of_result=self.result #Poor choice of script, i have somewhere that run in a loop.
        print(len(list_of_result))
        for exception_rule in self.select_exception:

            
            for result in list_of_result:

                #i have a loop that is looping on itself.

                exception_rule.rule.select_source=Select()
                exception_rule.rule.select_source.dict_elements={result.source.file:[result.source]}
                exception_rule.rule.select_source.list_ifc_file=[result.source.file]
                exception_rule.rule.select_target=Select()
                exception_rule.rule.select_target.dict_elements={result.target.file:[result.target]}
                exception_rule.rule.select_target.list_ifc_file=[result.target.file]
                exception_rule.rule.run(state="Exception")

                print("End of one exception",exception_rule.rule.result)

                if exception_rule.rule.result[0].status:
                    continue
                else:
                    self.result.state=False
                






    def run_must(self):
        print("TODO MUST")

    def manage_result(self):
        self.run_exception()
        self.run_must()
        self.run_grouping()
        self.run_criticity()
        self.run_actor()

class RuleCheckComplex(RuleCheck):
    def __init__(self):
        super().__init__()
        select_target: Select = None
        select_context_A: Select = None
        select_context_B: Select = None
        select_context_C: Select = None


# ==== Clash Result
class ClashResult:
    def __init__(self, source, state, type="SingleResult"):
        self.id: str
        self.type: str = type
        self.source: ifcopenshell.entity_instance = source
        self.source_group: str = None

        self.status: bool = state
        self.criticity: str = []
        self.actor: str = []


class ClashResultOneObject(ClashResult):
    def __init__(self, source, state):
        super().__init__(source, state)


class ClashResultTwoObjects(ClashResult):
    def __init__(self,source,target,state,type="SingleResult"):
        super().__init__(source,state,type)
        self.target: ifcopenshell.entity_instance = target
        


class ClashResultComplex(ClashResult):
    def __init__(self):
        super().__init__()
        self.target: ifcopenshell.entity_instance = None
        self.context: ifcopenshell.entity_instance = None
