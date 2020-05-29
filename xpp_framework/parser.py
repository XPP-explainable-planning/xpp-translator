import json

from .AS_property.action_set_property import ActionSetProperty
from .LTL_property.LTL_property import LTLProperty
from xpp_framework.general.special_goals import Goal

# typeObjectMap maps from a type to a list of objects which have this type
def parse(path, typeObjectMap, EXPSET):

    with open(path, encoding='utf-8') as fh:
        json_encoding = json.load(fh)

    for p_json in json_encoding["plan_properties"]:
        if p_json['type'] == 'AS':
            property = ActionSetProperty.fromJSON(p_json, typeObjectMap)
            EXPSET.add_action_set_property(property)
        elif p_json['type'] == 'LTL':
            property = LTLProperty.fromJSON(p_json, typeObjectMap)
            EXPSET.add_ltl_property(property)
        else:
            assert False, "Unknown property type: " + p_json['type']
        for set in property.get_action_sets():
            oldName = set.name
            EXPSET.add_action_set(set)
            # print("Replace constant name: " + oldName + " " + set.name)
            property.update_action_set_name(oldName, set.name)

    if "hard_goals" in json_encoding and "soft_goals" in json_encoding:
        EXPSET.add_hard_goals(Goal.fromJSON(json_encoding["hard_goals"], EXPSET))
        EXPSET.add_soft_goals(Goal.fromJSON(json_encoding["soft_goals"], EXPSET))
