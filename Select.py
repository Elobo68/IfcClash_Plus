from __future__ import annotations
import json
import time
import numpy as np
import multiprocessing
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.selector
from logging import Logger
from typing import Literal, TypedDict, Union,List
from typing_extensions import NotRequired, assert_never
from ifctester.facet import Entity
from IfcOpenShell.src.ifctester.ifctester.facet import Facet

from abc import ABC, abstractmethod


class Select():
    def __init__(self):
        self.id:str="AZE"
        self.list_ifc_path:list[str]=[]
        self.list_ifc_file:list[ifcopenshell.file]=[]
        self.dict_elements: dict = {}
        self.elements:list[ifcopenshell.entity_instance]=[]



    def Run(self):
        pass

    def Load_File(self):
        for path in self.list_ifc_path:
            self.list_ifc_file.append(ifcopenshell.open(path))

class Select_Facet(Select):
    def __init__(self,ClassificationType="Facet"):
        super().__init__()
        self.type: str = ClassificationType
        self.applicability: List[Facet] = []
        self.classification_name: str = ""




    def Run(self):


        #Filter of facet do not work as i intended. I thought i could give me a precise filter, like ids but it's not.
        #

        #I modify to recreate the way my script is intended, but it's not good way to do
        for element in self.elements:
            ifc_file=element.file
            if ifc_file in self.dict_elements:
                self.dict_elements[ifc_file].append(element)
            else:
                self.dict_elements[ifc_file]=[element]

        for ifc_file in self.dict_elements.keys():
            self.elements=list(self.elements)+self.dict_elements[ifc_file]


        """
        self.Load_File()
        for ifc_file in self.list_ifc_file:
            for facet in self.applicability:
               if ifc_file in self.dict_elements:
                   self.dict_elements[ifc_file] = facet.filter(ifc_file, self.dict_elements[ifc_file])
               else:
                   self.dict_elements[ifc_file]=facet.filter(ifc_file, None) # To rework when there is multiple facet

        for ifc_file in self.dict_elements.keys():
            self.elements=self.elements+self.dict_elements[ifc_file]
        """



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
            Entity_A=result.a
            GUID_Entity_A=Entity_A.get_argument(0) #There must be a clean way to do that. From the result of the clash, i want to update the select elements.

            for OneElement in self.rule.Select_Source.elements:
                if OneElement.GlobalId==GUID_Entity_A:
                    self.elements.append(OneElement)
                    if OneElement.file in self.dict_elements:
                        self.dict_elements[OneElement.file].append(OneElement)
                    else:
                        self.dict_elements[OneElement.file] = [OneElement]

            Entity_b=result.b
            GUID_Entity_b=Entity_b.get_argument(0) #There must be a clean way to do that

            for OneElement in self.rule.Select_Source.elements:
                if OneElement.GlobalId==GUID_Entity_b:
                    self.elements.append(OneElement)
                    if OneElement.file in self.dict_elements:
                        self.dict_elements[OneElement.file].append(OneElement)
                    else:
                        self.dict_elements[OneElement.file] = [OneElement]

        self.elements=list(set(self.elements))



if __name__ == '__main__':
    LaSelectFacet=Select_Facet()

    CheminFichier="/home/jocelin/Documents/200 - IFC/Model_IFC/PN1801_17_EXE_MOD_000177_01_H_0810P_GEN_2x3-Finale.ifc"

    LaSelectFacet.list_ifc_path=[CheminFichier]



    LaEntite=Entity()
    LaEntite.name="IfcSpace"

    LaSelectFacet.applicability=[LaEntite]

    LaSelectFacet.Run()

    print(LaSelectFacet.elements)



