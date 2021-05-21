from . import AS_property
from . import action_sets as action_set_comp
from . import LTL_property
from . import G_property
from .parser import parse
from .general import question
from .general import ExplanationSetting
from .general.special_goals import set_goals

# global setting
EXPSET = ExplanationSetting()


def run(options, task, sas_task):
    properties_path = options.plan_property
    print("----------------------------------------------------------------------------------------------")

    if properties_path != "None" and properties_path != "PROPERTY":
        print("Compile properties")
        
        #build typeObjectMap
        typeObjectMap = {}
        for o in task.objects:
            if not o.type_name in typeObjectMap:
                typeObjectMap[o.type_name] = []

            typeObjectMap[o.type_name].append(o.name)

        #print("++++++++++ typeObjectMap ++++++++++")
        #print(typeObjectMap)

        parse(properties_path, typeObjectMap, EXPSET)

        for name, s in EXPSET.action_sets.items():
            action_set_comp.compileActionSet(sas_task, s)

        AS_property.compileActionSetProperties(sas_task, EXPSET.get_action_set_properties(), EXPSET.action_sets)

        LTL_property.compileLTLProperties(options.only_add_LTL_prop_to_SAS, sas_task, EXPSET.get_ltl_properties(), EXPSET.action_sets)

        G_property.compileGoalProperties(sas_task, EXPSET.get_goal_properties())

        set_goals(sas_task, EXPSET)

        EXPSET.constraint.add_to_task(sas_task)
        return True
    else:
        return False





