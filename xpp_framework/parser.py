import json

from .AS_property.action_set_property import ActionSetProperty
from .LTL_property.LTL_property import LTLProperty

# typeObjectMap maps from a type to a list of objects which have this type
def parse(path, typeObjectMap):

    reader = open(path, "r")
    lines = reader.readlines()
    reader.close()

    actionSets = {}
    AS_properties = []
    LTL_properties = []

    json_encoding = json.loads(lines)
    for p_json in json_encoding["properties"]:
        if json_encoding["typ"] == 'AS':
            property = ActionSetProperty.fromJSON(p_json, typeObjectMap)
            AS_properties.append(property)
        elif json_encoding["typ"] == 'LTL':
            property = LTLProperty.fromJSON(p_json, typeObjectMap)
            LTL_properties.append(property)
        else:
            assert False, "Unknown property type: " + json_encoding["typ"]
        for set in property.get_action_sets():
            actionSets[set.name] = set


    return (actionSets, AS_properties, LTL_properties)
