"""
Module for serializing and deserializing IfcClash_Plus rules to/from XML files.
This allows saving and reloading rule configurations for later use.
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Union, Optional
import ifcopenshell

# ======================
# MAPPING DES CLASSES
# ======================
# Dictionnaire pour mapper les noms de classes XML aux classes Python
RULE_CLASS_MAP = {}

# Dictionnaire pour mapper les types de Facet
FACET_TYPE_MAP = {}


def register_rule_class(rule_name: str, rule_class: type) -> None:
    """Register a rule class for serialization/deserialization."""
    RULE_CLASS_MAP[rule_name] = rule_class


def register_facet_type(facet_name: str, facet_class: type) -> None:
    """Register a facet type for serialization/deserialization."""
    FACET_TYPE_MAP[facet_name] = facet_class


# ======================
# FONCTIONS DE SÉRIALISATION
# ======================

def serialize_facet(facet) -> ET.Element:
    """Sérialise un objet Facet (Entity, Property, etc.) en XML."""
    facet_type = facet.__class__.__name__
    if facet_type not in FACET_TYPE_MAP:
        raise ValueError(f"Unsupported facet type: {facet_type}")
    
    elem = ET.Element("Facet", type=facet_type)
    
    if facet_type == "Entity":
        ET.SubElement(elem, "name").text = facet.name
    elif facet_type == "Property":
        ET.SubElement(elem, "propertySet").text = facet.propertySet
        ET.SubElement(elem, "baseName").text = facet.baseName
        ET.SubElement(elem, "value").text = str(facet.value) if facet.value else ""
    elif facet_type == "Attribute":
        ET.SubElement(elem, "name").text = facet.name
        ET.SubElement(elem, "value").text = str(facet.value) if facet.value else ""
    elif facet_type == "Classification":
        ET.SubElement(elem, "name").text = facet.name
        ET.SubElement(elem, "value").text = str(facet.value) if facet.value else ""
    elif facet_type == "PartOf":
        ET.SubElement(elem, "name").text = facet.name
    elif facet_type == "Material":
        ET.SubElement(elem, "name").text = facet.name
    else:
        raise ValueError(f"Unsupported facet type: {facet_type}")
    
    return elem


def deserialize_facet(facet_elem: ET.Element):
    """Désérialise un élément XML en objet Facet."""
    facet_type = facet_elem.get("type")
    if facet_type not in FACET_TYPE_MAP:
        raise ValueError(f"Unknown facet type: {facet_type}")

    facet_class = FACET_TYPE_MAP[facet_type]
    kwargs = {}

    if facet_type == "Entity":
        kwargs["name"] = facet_elem.find("name").text
    elif facet_type == "Property":
        kwargs["propertySet"] = facet_elem.find("propertySet").text
        kwargs["baseName"] = facet_elem.find("baseName").text
        value_elem = facet_elem.find("value")
        kwargs["value"] = value_elem.text if value_elem is not None else None
    elif facet_type == "Attribute":
        kwargs["name"] = facet_elem.find("name").text
        value_elem = facet_elem.find("value")
        kwargs["value"] = value_elem.text if value_elem is not None else None
    elif facet_type == "Classification":
        kwargs["name"] = facet_elem.find("name").text
        value_elem = facet_elem.find("value")
        kwargs["value"] = value_elem.text if value_elem is not None else None
    elif facet_type == "PartOf":
        kwargs["name"] = facet_elem.find("name").text
    elif facet_type == "Material":
        kwargs["name"] = facet_elem.find("name").text

    return facet_class(**kwargs)


def serialize_select(select) -> ET.Element:
    """Sérialise un objet Select (SelectFacet ou SelectRule) en XML."""
    select_type = select.__class__.__name__
    
    if select_type == "SelectFacet":
        elem = ET.Element("Select", type="SelectFacet")
        ET.SubElement(elem, "classification_name").text = select.classification_name
        ET.SubElement(elem, "type").text = select.type
        applicability_elem = ET.SubElement(elem, "applicability")
        for facet in select.applicability:
            applicability_elem.append(serialize_facet(facet))
    elif select_type == "SelectRule":
        elem = ET.Element("Select", type="SelectRule")
        ET.SubElement(elem, "action_type").text = str(select.action_type)
        # Sérialiser la règle associée (si elle existe)
        if hasattr(select, "rule") and select.rule:
            rule_elem = serialize_rule(select.rule)
            elem.append(rule_elem)
    else:
        raise ValueError(f"Unsupported Select type: {select_type}")
    
    return elem


def deserialize_select(select_elem: ET.Element, file_paths: List[str] = None):
    """Désérialise un élément XML en objet Select."""
    select_type = select_elem.get("type")
    
    if select_type == "SelectFacet":
        from RuleClass import SelectFacet
        select = SelectFacet()
        classification_elem = select_elem.find("classification_name")
        if classification_elem is not None:
            select.classification_name = classification_elem.text
        type_elem = select_elem.find("type")
        if type_elem is not None:
            select.type = type_elem.text
        applicability_elem = select_elem.find("applicability")
        if applicability_elem is not None:
            select.applicability = [
                deserialize_facet(facet_elem)
                for facet_elem in applicability_elem.findall("Facet")
            ]
        return select
    elif select_type == "SelectRule":
        from RuleClass import SelectRule
        select = SelectRule()
        action_type_elem = select_elem.find("action_type")
        if action_type_elem is not None:
            select.action_type = int(action_type_elem.text)
        rule_elem = select_elem.find("Rule")
        if rule_elem is not None:
            select.rule = deserialize_rule(rule_elem, file_paths)
        return select
    else:
        raise ValueError(f"Unknown Select type: {select_type}")


def serialize_rule(rule) -> ET.Element:
    """Sérialise une règle (RuleCheck) en XML."""
    rule_class_name = rule.__class__.__name__
    elem = ET.Element("Rule", type=rule_class_name)

    # Ajouter les attributs communs
    ET.SubElement(elem, "id").text = rule.id if rule.id else ""

    # Ajouter les paramètres spécifiques à la règle
    if hasattr(rule, "volume_min"):
        ET.SubElement(elem, "volume_min").text = str(rule.volume_min)
    if hasattr(rule, "volume_max"):
        ET.SubElement(elem, "volume_max").text = str(rule.volume_max)
    if hasattr(rule, "area_min"):
        ET.SubElement(elem, "area_min").text = str(rule.area_min)
    if hasattr(rule, "area_max"):
        ET.SubElement(elem, "area_max").text = str(rule.area_max)
    if hasattr(rule, "tolerance"):
        ET.SubElement(elem, "tolerance").text = str(rule.tolerance)
    if hasattr(rule, "target_direction"):
        ET.SubElement(elem, "target_direction").text = str(rule.target_direction)
    if hasattr(rule, "height"):
        ET.SubElement(elem, "height").text = str(rule.height)
    if hasattr(rule, "direction"):
        ET.SubElement(elem, "direction").text = str(rule.direction)

    # Sérialiser select_source et select_target (si applicable)
    if hasattr(rule, "select_source") and rule.select_source:
        source_elem = ET.SubElement(elem, "select_source")
        source_elem.append(serialize_select(rule.select_source))

    if hasattr(rule, "select_target") and rule.select_target:
        target_elem = ET.SubElement(elem, "select_target")
        target_elem.append(serialize_select(rule.select_target))

    # Sérialiser les options de grouping, criticity, actor, etc.
    if hasattr(rule, "select_grouping") and rule.select_grouping:
        grouping_elem = ET.SubElement(elem, "select_grouping")
        grouping_elem.append(serialize_select(rule.select_grouping))

    if hasattr(rule, "select_criticity") and rule.select_criticity:
        criticity_elem = ET.SubElement(elem, "select_criticity")
        for crit in rule.select_criticity:
            criticity_elem.append(serialize_select(crit))

    if hasattr(rule, "select_actor") and rule.select_actor:
        actor_elem = ET.SubElement(elem, "select_actor")
        for actor in rule.select_actor:
            actor_elem.append(serialize_select(actor))

    if hasattr(rule, "abs_or_rel_check") and rule.abs_or_rel_check:
        abs_rel_elem = ET.SubElement(elem, "abs_or_rel_check")
        abs_rel_elem.append(serialize_abs_or_rel(rule.abs_or_rel_check))

    if hasattr(rule, "select_exception") and rule.select_exception:
        exception_elem = ET.SubElement(elem, "select_exception")
        for exc in rule.select_exception:
            exception_elem.append(serialize_select(exc))

    return elem


def deserialize_rule(rule_elem: ET.Element, file_paths: List[str] = None):
    """Désérialise un élément XML en objet Rule."""
    rule_type = rule_elem.get("type")
    if rule_type not in RULE_CLASS_MAP:
        raise ValueError(f"Unknown rule type: {rule_type}")

    rule_class = RULE_CLASS_MAP[rule_type]
    kwargs = {}

    # Extraire les paramètres spécifiques
    for param in ["volume_min", "volume_max", "area_min", "area_max", "tolerance", "height"]:
        param_elem = rule_elem.find(param)
        if param_elem is not None:
            kwargs[param] = float(param_elem.text)

    for param in ["target_direction", "direction"]:
        param_elem = rule_elem.find(param)
        if param_elem is not None:
            kwargs[param] = param_elem.text

    # Créer l'instance de la règle (sans source/target pour l'instant)
    # On utilise un Select vide temporairement
    from RuleClass import SelectFacet
    temp_source = SelectFacet()
    
    # Check if it's a two-object rule
    is_two_object_rule = any(
        base.__name__ == "RuleCheckTwoObjects" 
        for base in rule_class.__bases__
    )
    
    if is_two_object_rule:
        temp_target = SelectFacet()
        rule = rule_class(temp_source, temp_target, **kwargs)
    else:
        rule = rule_class(temp_source, **kwargs)

    # Désérialiser select_source et select_target
    source_elem = rule_elem.find("select_source")
    if source_elem is not None and len(source_elem) > 0:
        rule.select_source = deserialize_select(source_elem[0], file_paths)

    target_elem = rule_elem.find("select_target")
    if target_elem is not None and len(target_elem) > 0:
        rule.select_target = deserialize_select(target_elem[0], file_paths)

    # Désérialiser les autres options
    grouping_elem = rule_elem.find("select_grouping")
    if grouping_elem is not None and len(grouping_elem) > 0:
        rule.select_grouping = deserialize_select(grouping_elem[0], file_paths)

    criticity_elem = rule_elem.find("select_criticity")
    if criticity_elem is not None:
        rule.select_criticity = [
            deserialize_select(crit_elem, file_paths)
            for crit_elem in criticity_elem.findall("Select")
        ]

    actor_elem = rule_elem.find("select_actor")
    if actor_elem is not None:
        rule.select_actor = [
            deserialize_select(actor_elem, file_paths)
            for actor_elem in actor_elem.findall("Select")
        ]

    abs_rel_elem = rule_elem.find("abs_or_rel_check")
    if abs_rel_elem is not None and len(abs_rel_elem) > 0:
        rule.abs_or_rel_check = deserialize_abs_or_rel(abs_rel_elem[0])

    exception_elem = rule_elem.find("select_exception")
    if exception_elem is not None:
        rule.select_exception = [
            deserialize_select(exc_elem, file_paths)
            for exc_elem in exception_elem.findall("Select")
        ]

    return rule


def serialize_abs_or_rel(abs_or_rel) -> ET.Element:
    """Sérialise un objet AbsoluteChecking ou RelativeChecking en XML."""
    elem = ET.Element("AbsoluteOrRelativeChecking", type=abs_or_rel.__class__.__name__)
    ET.SubElement(elem, "type").text = abs_or_rel.type
    ET.SubElement(elem, "groupby_method").text = abs_or_rel.groupby_method

    if abs_or_rel.__class__.__name__ == "AbsoluteChecking":
        ET.SubElement(elem, "focus").text = abs_or_rel.focus
        ET.SubElement(elem, "operation").text = abs_or_rel.operation
        ET.SubElement(elem, "aim").text = str(abs_or_rel.aim)
        if hasattr(abs_or_rel, "quantity_pset") and abs_or_rel.quantity_pset:
            ET.SubElement(elem, "quantity_pset").text = abs_or_rel.quantity_pset
        if hasattr(abs_or_rel, "quantity_prop") and abs_or_rel.quantity_prop:
            ET.SubElement(elem, "quantity_prop").text = abs_or_rel.quantity_prop
    elif abs_or_rel.__class__.__name__ == "RelativeChecking":
        ET.SubElement(elem, "source_operation").text = abs_or_rel.source_operation
        ET.SubElement(elem, "operation").text = abs_or_rel.operation
        ET.SubElement(elem, "target_operation").text = abs_or_rel.target_operation
        if hasattr(abs_or_rel, "quantity_pset") and abs_or_rel.quantity_pset:
            ET.SubElement(elem, "quantity_pset").text = abs_or_rel.quantity_pset
        if hasattr(abs_or_rel, "quantity_prop") and abs_or_rel.quantity_prop:
            ET.SubElement(elem, "quantity_prop").text = abs_or_rel.quantity_prop

    return elem


def deserialize_abs_or_rel(abs_or_rel_elem: ET.Element):
    """Désérialise un élément XML en objet AbsoluteChecking ou RelativeChecking."""
    abs_or_rel_type = abs_or_rel_elem.get("type")
    
    if abs_or_rel_type == "AbsoluteChecking":
        from RuleClass import AbsoluteChecking
        abs_or_rel = AbsoluteChecking(type=abs_or_rel_elem.find("type").text)
        abs_or_rel.groupby_method = abs_or_rel_elem.find("groupby_method").text
        focus_elem = abs_or_rel_elem.find("focus")
        if focus_elem is not None:
            abs_or_rel.focus = focus_elem.text
        operation_elem = abs_or_rel_elem.find("operation")
        if operation_elem is not None:
            abs_or_rel.operation = operation_elem.text
        aim_elem = abs_or_rel_elem.find("aim")
        if aim_elem is not None:
            abs_or_rel.aim = float(aim_elem.text)
        quantity_pset_elem = abs_or_rel_elem.find("quantity_pset")
        if quantity_pset_elem is not None:
            abs_or_rel.quantity_pset = quantity_pset_elem.text
        quantity_prop_elem = abs_or_rel_elem.find("quantity_prop")
        if quantity_prop_elem is not None:
            abs_or_rel.quantity_prop = quantity_prop_elem.text
        return abs_or_rel
    elif abs_or_rel_type == "RelativeChecking":
        from RuleClass import RelativeChecking
        abs_or_rel = RelativeChecking(type=abs_or_rel_elem.find("type").text)
        abs_or_rel.groupby_method = abs_or_rel_elem.find("groupby_method").text
        source_op_elem = abs_or_rel_elem.find("source_operation")
        if source_op_elem is not None:
            abs_or_rel.source_operation = source_op_elem.text
        operation_elem = abs_or_rel_elem.find("operation")
        if operation_elem is not None:
            abs_or_rel.operation = operation_elem.text
        target_op_elem = abs_or_rel_elem.find("target_operation")
        if target_op_elem is not None:
            abs_or_rel.target_operation = target_op_elem.text
        quantity_pset_elem = abs_or_rel_elem.find("quantity_pset")
        if quantity_pset_elem is not None:
            abs_or_rel.quantity_pset = quantity_pset_elem.text
        quantity_prop_elem = abs_or_rel_elem.find("quantity_prop")
        if quantity_prop_elem is not None:
            abs_or_rel.quantity_prop = quantity_prop_elem.text
        return abs_or_rel
    else:
        raise ValueError(f"Unknown AbsoluteOrRelativeChecking type: {abs_or_rel_type}")


def serialize_rule_file(rule_file) -> ET.Element:
    """Sérialise un RuleFile complet en XML."""
    root = ET.Element("IfcClashPlus_RuleFile")

    # Ajouter les chemins des fichiers IFC
    ifc_paths_elem = ET.SubElement(root, "ifc_paths")
    for path in rule_file.list_ifc_path:
        ET.SubElement(ifc_paths_elem, "path").text = path

    # Ajouter les règles et dossiers
    contains_elem = ET.SubElement(root, "contains")
    for item in rule_file.contains:
        if item.__class__.__name__ == "RuleFolder":
            contains_elem.append(serialize_rule_folder(item))
        elif hasattr(item, "type") and "RuleCheck" in str(type(item)):
            contains_elem.append(serialize_rule(item))
        else:
            raise ValueError(f"Unsupported item type in RuleFile: {type(item)}")

    return root


def serialize_rule_folder(folder) -> ET.Element:
    """Sérialise un RuleFolder en XML."""
    elem = ET.Element("RuleFolder")
    ET.SubElement(elem, "id").text = folder.id if folder.id else ""
    ET.SubElement(elem, "activation_rule").text = str(folder.activation_rule)
    ET.SubElement(elem, "activation_case").text = folder.activation_case if folder.activation_case else ""

    contains_elem = ET.SubElement(elem, "contains")
    for item in folder.contains:
        if item.__class__.__name__ == "RuleFolder":
            contains_elem.append(serialize_rule_folder(item))
        elif hasattr(item, "type") and "RuleCheck" in str(type(item)):
            contains_elem.append(serialize_rule(item))
        else:
            raise ValueError(f"Unsupported item type in RuleFolder: {type(item)}")

    return elem


def deserialize_rule_folder(folder_elem: ET.Element, file_paths: List[str] = None):
    """Désérialise un élément XML en objet RuleFolder."""
    from RuleClass import RuleFolder
    folder = RuleFolder()
    id_elem = folder_elem.find("id")
    if id_elem is not None:
        folder.id = id_elem.text
    activation_rule_elem = folder_elem.find("activation_rule")
    if activation_rule_elem is not None:
        folder.activation_rule = activation_rule_elem.text.lower() == "true"
    activation_case_elem = folder_elem.find("activation_case")
    if activation_case_elem is not None:
        folder.activation_case = activation_case_elem.text

    contains_elem = folder_elem.find("contains")
    if contains_elem is not None:
        for item_elem in contains_elem:
            if item_elem.tag == "RuleFolder":
                folder.contains.append(deserialize_rule_folder(item_elem, file_paths))
            elif item_elem.tag == "Rule":
                folder.contains.append(deserialize_rule(item_elem, file_paths))

    return folder


# ======================
# FONCTIONS PRINCIPALES
# ======================

def save_to_xml(rule_file, filepath: str) -> None:
    """
    Sauvegarde un RuleFile dans un fichier XML.
    
    Args:
        rule_file: L'objet RuleFile à sauvegarder.
        filepath: Chemin du fichier XML de destination.
    """
    root = serialize_rule_file(rule_file)
    tree = ET.ElementTree(root)
    tree.write(filepath, encoding="utf-8", xml_declaration=True)


def load_from_xml(filepath: str):
    """
    Charge un RuleFile depuis un fichier XML.
    
    Args:
        filepath: Chemin du fichier XML à charger.
    
    Returns:
        Un objet RuleFile reconstitué.
    """
    from RuleClass import RuleFile
    tree = ET.parse(filepath)
    root = tree.getroot()

    rule_file = RuleFile()

    # Charger les chemins des fichiers IFC
    ifc_paths_elem = root.find("ifc_paths")
    if ifc_paths_elem is not None:
        rule_file.list_ifc_path = [path_elem.text for path_elem in ifc_paths_elem.findall("path")]

    # Charger les règles et dossiers
    contains_elem = root.find("contains")
    if contains_elem is not None:
        for item_elem in contains_elem:
            if item_elem.tag == "RuleFolder":
                rule_file.contains.append(deserialize_rule_folder(item_elem, rule_file.list_ifc_path))
            elif item_elem.tag == "Rule":
                rule_file.contains.append(deserialize_rule(item_elem, rule_file.list_ifc_path))

    return rule_file


# ======================
# ENREGISTREMENT DES CLASSES
# ======================
# Enregistrer les classes de règles et facets disponibles

def register_all_classes():
    """Enregistre toutes les classes de règles et facets disponibles."""
    from RuleClass import (
        RuleFile,
        RuleFolder,
        Select,
        SelectFacet,
        SelectRule,
        RuleCheckOneObject,
        RuleCheckTwoObjects,
        ClashResult,
        GroupResult,
        AbsoluteChecking,
        RelativeChecking,
    )
    from ifctester.facet import (
        Entity,
        Property,
        Attribute,
        Classification,
        PartOf,
        Material,
    )
    
    # Enregistrer les facets
    register_facet_type("Entity", Entity)
    register_facet_type("Property", Property)
    register_facet_type("Attribute", Attribute)
    register_facet_type("Classification", Classification)
    register_facet_type("PartOf", PartOf)
    register_facet_type("Material", Material)


# Appeler l'enregistrement au chargement du module
register_all_classes()
