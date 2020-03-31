import abc


class PlanProperty(abc.ABC):

    def __init__(self, name, formula):
        self.name = name
        self.formula = formula
        self.actionSets = []
        # names of the set names that are used in the property
        self.constants = []
        # id of the sat variable in the SAS encoding
        self.var_id = None

    def add_action_set(self, s):
        self.actionSets.append(s)

    def add_constant(self, c):
        self.constants.append(c)

    def __repr__(self):
        s = self.name + ":\n\t" + str(self.formula)
        return s