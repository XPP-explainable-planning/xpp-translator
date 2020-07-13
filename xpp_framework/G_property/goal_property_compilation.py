from xpp_framework.general.utils import literalVarValue

def compileGoalProperties(sas_task, properties):
    for prop in properties:
        var, value = literalVarValue(sas_task, prop.formula)
        prop.var_id = var
        prop.var_sat_goal_value = value