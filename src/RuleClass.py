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
from copy import deepcopy, copy
from ifcopenshell.util.element import get_pset


class RuleFile:
    def __init__(self):
        self.id: str = ""
        self.list_ifc_path: list[str] = []
        self.list_ifc_file: list[ifcopenshell.file] = []
        self.contains: list = []  # Union of folder or Rule

        self.path_to_save: str = None

    def run(self):
        self.load_file()
        self.update_file_info()

        for rulecheck_or_folder in self.contains:
            rulecheck_or_folder.run()

    def update_file_info(self):
        for rule_or_file in self.contains:
            rule_or_file.update_file_info(self.list_ifc_path, self.list_ifc_file)

    def load_file(self):
        for path in self.list_ifc_path:
            self.list_ifc_file.append(ifcopenshell.open(path))

    def to_xml(self, filepath="output.xml"):
        print("to_xml() is not working")
        # @todo to_xml function


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

    def update_file_info(self, files_path, files):
        for rule_or_file in self.contains:
            rule_or_file.update_file_info(files_path, files)


class Select:
    def __init__(self):
        self.id: str = "AZE"
        self.list_ifc_path: list[str] = []
        self.list_ifc_file: list[ifcopenshell.file] = []
        self.dict_elements: dict = {}
        self.list_of_elements: list[ifcopenshell.entity_instance] = []

    def run(self):
        pass

    def initialize_dict(self):
        Dict = dict()
        for onefile in self.list_ifc_file:
            Dict[onefile] = None
        self.dict_elements = Dict

    def create_list_of_element(self):
        for onefile in self.list_ifc_file:
            self.list_of_elements = self.dict_elements[onefile] + self.list_of_elements





class SelectFacet(Select):
    def __init__(self, ClassificationType="Facet"):
        super().__init__()
        self.type: str = ClassificationType
        self.applicability: List[Facet] = []
        self.classification_name: str = ""

    def run(self):
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

    def update_file_info(self, files_path, files):
        self.list_ifc_path = files_path
        self.list_ifc_file = files


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

    def run(self, state="Select"):
        self.rule.run(state)
        self.produce_select()

    def produce_select(self):
        self.dict_elements = {}
        for result in self.rule.result:
            if result.source.file in self.dict_elements.keys():
                if self.dict_elements[result.source.file] is None:
                    self.dict_elements[result.source.file] = [result.source]
                else:
                    self.dict_elements[result.source.file].append(result.source)
            else:
                self.dict_elements[result.source.file] = [result.source]

    def update_file_info(self, files_path, files):
        self.list_ifc_path = files_path
        self.list_ifc_file = files
        self.rule.update_file_info(files_path,files)


@abstractmethod
class RuleCheck:
    def __init__(self, source):
        self.id: str = None
        self.type: str = None

        self.tree: list = None  # @todo Determine the exact position of this parameter

        self.result: list[ClashResult] = []

        self.select_source: Select = source
        self.select_grouping: SelectFacet = None
        self.select_criticity: list[SelectFacet] = []
        self.select_actor: list[SelectFacet] = []
        self.abs_or_rel_check: AbsoluteOrRelativeChecking = None

        self.grouped_result: list[GroupResult] = []

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
    def __init__(self, source):
        super().__init__(source)
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
        # @todo Should i stick to ids for these selection, it may be a bad idea
        # grouping by source and select is not relevant here

        def grouping_by_entity(self):
            group_dict = {}
            for result in self.result:
                unique_value = result.source.is_a()
                if unique_value not in group_dict:
                    thegroupresult = GroupResult()
                    thegroupresult.add_source(result)
                    group_dict[unique_value] = thegroupresult
                else:
                    group_dict[unique_value].add_source(result)

            for key in group_dict:
                self.grouped_result.append(group_dict[key])

        def grouping_by_property(self):
            group_dict = {}
            for result in self.result:
                unique_value = get_pset(
                    result.source,
                    name=self.select_grouping.propertySet,
                    prop=self.select_grouping.baseName,
                )
                unique_value = str(unique_value)
                print(unique_value)
                if unique_value not in group_dict:
                    thegroupresult = GroupResult()
                    thegroupresult.add_source(result)
                    group_dict[unique_value] = thegroupresult
                else:
                    group_dict[unique_value].add_source(result)

            for key in group_dict:
                self.grouped_result.append(group_dict[key])

        def grouping_by_attribute(self):
            group_dict = {}
            for result in self.result:
                unique_value = result.source.get_info()
                unique_value = unique_value[self.select_grouping.name]
                unique_value = str(unique_value)
                print(unique_value)
                if unique_value not in group_dict:
                    thegroupresult = GroupResult()
                    thegroupresult.add_source(result)
                    group_dict[unique_value] = thegroupresult
                else:
                    group_dict[unique_value].add_source(result)

            for key in group_dict:
                self.grouped_result.append(group_dict[key])

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

    def run_criticity(self):
        if self.select_criticity == []:
            return None

        for one_criticity in self.select_criticity:
            one_criticity.run()
            one_criticity.create_list_of_element()

        for oneresult in self.result:
            for one_criticity in self.select_criticity:
                if oneresult.source in one_criticity.list_of_elements:
                    oneresult.criticity.append(one_criticity.classification_name)

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


    def run_abs_or_rel(self):
        if self.abs_or_rel_check is None:
            return None
        
        self.abs_or_rel_check.run()

        return True


    def manage_result(self):
        
        self.run_criticity()
        self.run_actor()

        # Only one is possible, it either grouping or must. Not both of them
        if self.run_abs_or_rel() is None:
            self.run_grouping()


    def update_file_info(self, files_path, files):
        self.select_source.update_file_info(files_path, files)

        for one_select_criticity in self.select_criticity:
            one_select_criticity.update_file_info(files_path, files)

        for one_select_actor in self.select_actor:
            one_select_actor.update_file_info(files_path, files)


class RuleCheckTwoObjects(RuleCheck):
    def __init__(self, source, target):
        super().__init__(source)
        self.select_target: Select = target
        self.select_exception: list[SelectRule] = []

    def produce_select(self):
        # @todo pass the fail or success element.
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
            group_dict = {}
            for result in self.result:
                # Source grouping
                unique_value = result.source.is_a()
                if unique_value not in group_dict:
                    thegroupresult = GroupResult()
                    thegroupresult.add_source(result)
                    group_dict[unique_value] = thegroupresult
                else:
                    group_dict[unique_value].add_source(result)

                # Target grouping
                unique_value = result.target.is_a()
                if unique_value not in group_dict:
                    thegroupresult = GroupResult()
                    thegroupresult.add_target(result)
                    group_dict[unique_value] = thegroupresult
                else:
                    group_dict[unique_value].add_target(result)

            for key in group_dict:
                self.grouped_result.append(group_dict[key])

        def grouping_by_property(self):
            group_dict = {}
            for result in self.result:
                # Source grouping
                unique_value = get_pset(
                    result.source,
                    name=self.select_grouping.propertySet,
                    prop=self.select_grouping.baseName,
                )
                unique_value = str(unique_value)
                print(unique_value)
                if unique_value not in group_dict:
                    thegroupresult = GroupResult()
                    thegroupresult.add_source(result)
                    group_dict[unique_value] = thegroupresult
                else:
                    group_dict[unique_value].add_source(result)

                # Target grouping
                unique_value = get_pset(
                    result.target,
                    name=self.select_grouping.propertySet,
                    prop=self.select_grouping.baseName,
                )
                unique_value = str(unique_value)
                print(unique_value)
                if unique_value not in group_dict:
                    thegroupresult = GroupResult()
                    thegroupresult.add_target(result)
                    group_dict[unique_value] = thegroupresult
                else:
                    group_dict[unique_value].add_target(result)

            for key in group_dict:
                self.grouped_result.append(group_dict[key])

        def grouping_by_attribute(self):
            group_dict = {}
            for result in self.result:
                # Source
                unique_value = result.source.get_info()
                unique_value = unique_value[self.select_grouping.name]
                unique_value = str(unique_value)
                print(unique_value)
                if unique_value not in group_dict:
                    thegroupresult = GroupResult()
                    thegroupresult.add_source(result)
                    group_dict[unique_value] = thegroupresult
                else:
                    group_dict[unique_value].add_source(result)

                # Target
                unique_value = result.target.get_info()
                unique_value = unique_value[self.select_grouping.name]
                unique_value = str(unique_value)
                print(unique_value)
                if unique_value not in group_dict:
                    thegroupresult = GroupResult()
                    thegroupresult.add_target(result)
                    group_dict[unique_value] = thegroupresult
                else:
                    group_dict[unique_value].add_target(result)

            for key in group_dict:
                self.grouped_result.append(group_dict[key])
            ...

        def grouping_by_part_of(self):
            print("TODO")
            # @todo Grouping by part of for 2 objects rules
            ...

        def grouping_by_material(self):
            print("TODO")
            # @todo Grouping by material for 2 objects rules

        def grouping_by_classification(self):
            print("TODO CLASSIFICATION")
            ...

        def grouping_by_closeness(self):
            print("TODO")
            # @todo Grouping by closeness for 2 objects rules, reuse IfcClash

        def grouping_by_object(self,source_or_target):
            group_dict = {}
            for result in self.result:

                if source_or_target=="source":
                    unique_value = result.source
                if source_or_target=="target":
                    unique_value = result.target
                
                if unique_value not in group_dict:
                    thegroupresult = GroupResult()
                    thegroupresult.add_source_and_target(result)
                    group_dict[unique_value] = thegroupresult
                else:
                    group_dict[unique_value].add_source_and_target(result)

            for key in group_dict:
                self.grouped_result.append(group_dict[key])

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

    def run_criticity(self):
        if self.select_criticity == []:
            return None

        for one_criticity in self.select_criticity:
            one_criticity.run()
            one_criticity.create_list_of_element()

        for oneresult in self.result:
            for one_criticity in self.select_criticity:
                if oneresult.source in one_criticity.list_of_elements:
                    oneresult.criticity.append(one_criticity.classification_name)
                if oneresult.target in one_criticity.list_of_elements:
                    oneresult.criticity.append(one_criticity.classification_name)

    def run_actor(self):
        if self.select_actor == []:
            return None

        for one_actor in self.select_actor:
            one_actor.run()
            one_actor.create_list_of_element()

        for oneresult in self.result:
            for one_actor in self.select_actor:
                if oneresult.source in one_actor.list_of_elements:
                    oneresult.actor.append(one_actor.classification_name)
                if oneresult.target in one_actor.list_of_elements:
                    oneresult.actor.append(one_actor.classification_name)

    def run_exception(self):
        for one_rule_result in self.result:
            for exception_rule in self.select_exception:
                exception_rule.rule.select_source = one_rule_result.source
                exception_rule.rule.select_target = one_rule_result.target

                exception_rule.rule.run(state="Exception")

                if exception_rule.rule.result == []:
                    one_rule_result.state = False
                    break
                else:
                    if exception_rule.rule.result[0].status:
                        continue
                    else:
                        one_rule_result.state = False
                        break

    def run_abs_or_rel(self):
        if self.abs_or_rel_check is None:
            return None
        

        self.run_grouping(self.abs_or_rel_check.groupby_method)
        
        
        self.abs_or_rel_check.run(self.grouped_result)

        return True


    def update_file_info(self, files_path, files):
        self.select_source.update_file_info(files_path, files)
        self.select_target.update_file_info(files_path, files)

        for one_select_criticity in self.select_criticity:
            one_select_criticity.update_file_info(files_path, files)

        for one_select_actor in self.select_actor:
            one_select_actor.update_file_info(files_path, files)

        for one_select_exception in self.select_exception:
            one_select_exception.update_file_info(files_path, files)

    def manage_result(self):
        self.run_exception()

        self.run_criticity()
        self.run_actor()

        # Only one is possible, it either grouping or must. Not both of them
        if self.run_abs_or_rel() is None:
            self.run_grouping()


class RuleCheckComplex(RuleCheck):
    def __init__(self):
        super().__init__()
        select_target: Select = None
        select_context_A: Select = None
        select_context_B: Select = None
        select_context_C: Select = None


####======= Absolute or Relative Checking
ABSOLUTEORRELATIVECHECK_TYPE = Literal[
    "Absolute_Number", "Relative_Quantity", "Absolute_Quantity", "Relative_Number"
]


@abstractmethod
class AbsoluteOrRelativeChecking:
    def __init__(self, type: ABSOLUTEORRELATIVECHECK_TYPE):
        self.type = type
        self.groupby_method: str = (
            "source"  # In futur, it could be grouped by different means
        )

    def run(self, list_of_result: list[GroupResult]):
        for onegroupresult in list_of_result:
            self.eval_check(onegroupresult)


class AbsoluteChecking(AbsoluteOrRelativeChecking):
    def __init__(self, type: ABSOLUTEORRELATIVECHECK_TYPE):
        super().__init__(self, type)
        self.type = type

        self.focus: str = "source"  # source or target
        self.element_number = None
        self.operation: str = ""
        self.aim: float = 0

        self.quantity_pset: str = None
        self.quantity_prop: str = None

    def number(self, groupresult: GroupResult):
        if self.focus == "source":
            self.element_number = len(groupresult.source_set)
        else:
            self.element_number = len(groupresult.target_set)

    def quantity(self, groupresult: GroupResult):
        if self.focus == "source":
            list = list(groupresult.source_set)
        else:
            list = list(groupresult.sourcetarget_set_set)

        for entity in list:
            # @todo Finish properly the property extraction with all the edge case, we must have at the end a working float to be compared
            value = get_pset(entity, name=self.quantity_pset, prop=self.quantity_prop)
            self.element_number = +value

    def eval_check(self, groupresult: GroupResult):
        if "Quantity" in self.type:
            self.quantity()
        if "Number" in self.type:
            self.number()

        operation_string = (
            str(self.element_number) + str(self.operation) + str(self.aim)
        )

        groupresult.abs_or_rel_check = eval(operation_string)

        return groupresult


class RelativeChecking(AbsoluteOrRelativeChecking):
    def __init__(self, type: ABSOLUTEORRELATIVECHECK_TYPE):
        super().__init__(self, type)
        self.type = type
        self.source_operation: str = ""
        self.operation: str = ""
        self.target_operation: str = ""

    def number(self, groupresult: GroupResult):
        self.source_number = len(groupresult.source_set)
        self.target_number = len(groupresult.target_set)

    def quantity(self, groupresult: GroupResult):
        source_list = list(groupresult.source_set)
        target_list = list(groupresult.target_set)

        for entity in source_list:
            # @todo Finish properly the property extraction with all the edge case, we must have at the end a working float to be compared
            value = get_pset(entity, name=self.quantity_pset, prop=self.quantity_prop)
            self.source_number = +value

        for entity in target_list:
            # @todo Finish properly the property extraction with all the edge case, we must have at the end a working float to be compared
            value = get_pset(entity, name=self.quantity_pset, prop=self.quantity_prop)
            self.target_number = +value

    def eval_check(self, groupresult: GroupResult):
        if "Quantity" in self.type:
            self.quantity()
        if "Number" in self.type:
            self.number()

        source_string = str(groupresult.number_of_source) + self.source_operation
        target_string = str(groupresult.number_of_target) + self.target_operation

        source_quantity = eval(source_string)
        target_quantity = eval(target_string)

        operation_string = str(source_quantity) + self.operation + str(target_quantity)

        groupresult.abs_or_rel_check = eval(operation_string)

        return groupresult


# ==== Clash Result
class ClashResult:
    def __init__(self, source, state, type="OneObjectResult"):
        self.id: str
        self.type: str = type
        self.source: ifcopenshell.entity_instance = source

        self.status: bool = state
        self.criticity: list[str] = []
        self.actor: list[str] = []


        self.point1 : tuple() #@todo Validate the info to export from the clash
        self.point2 : tuple() #To validate, list of point


class ClashResultOneObject(ClashResult):
    def __init__(self, source, state):
        super().__init__(source, state)


class ClashResultTwoObjects(ClashResult):
    def __init__(self, source, target, state, type="TwoObjectsResult"):
        super().__init__(source, state, type)
        self.target: ifcopenshell.entity_instance = target


class ClashResultComplex(ClashResult):
    def __init__(self):
        super().__init__()
        self.target: ifcopenshell.entity_instance = None
        self.context: ifcopenshell.entity_instance = None


# ====== Group Result
class GroupResult:
    def __init__(self, type="GroupResult"):
        self.id: str
        self.type: str = type
        self.result_group: list[ClashResult] = []
        self.source_set: set(ifcopenshell.entity_instance) = set()
        self.target_set: set(ifcopenshell.entity_instance) = set()
        self.abs_or_rel_check = None

    def add_source(self, clash_result: ClashResult):
        self.result_group.append(clash_result)
        self.source_set.add(clash_result.source)

    def add_target(self, clash_result: ClashResult):
        self.result_group.append(clash_result)
        self.target_set.add(clash_result.target)

    def add_source_and_target(self, clash_result: ClashResult):
        self.result_group.append(clash_result)
        self.target_set.add(clash_result.target)
        self.source_set.add(clash_result.source)
