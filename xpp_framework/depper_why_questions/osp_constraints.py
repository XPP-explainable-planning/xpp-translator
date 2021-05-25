import re

class OspConstraint:

    def __init__(self, name):
        self.name = name
        self.relaxation_list = None
        self.predicate = None
        self.domain_objects_index_map = None
        self.variable_index = None
        self.init_value = None
        self.value_relaxation_order = None


    @staticmethod
    def parse(json_def, typeObjectMap):
        assert 'name' in json_def and \
               ('relaxation' in json_def or
               ('predicate' in json_def and 'type' in json_def and 'relaxation_direction' in json_def))

        name = json_def['name'] # e.g. some name

        if 'predicate' in json_def:
            predicate = json_def['predicate'] # e.g. fuel(t1, ?)
            type = json_def['type'] # e.g. fuellevel
            relaxation_direction = json_def['relaxation_direction'] # asc or desc

            domain_objects = typeObjectMap[type]
            # print(domain_objects)

            #sort domain objects according to relaxation order
            domain_objects_and_index = [(o, int(re.sub('[a-zA-Z]','', o))) for o in domain_objects]
            domain_objects_and_index.sort(key=lambda e: e[1], reverse=relaxation_direction == 'desc')

            domain_objects_index_map = {}
            for i, e in enumerate(domain_objects_and_index):
                domain_objects_index_map[e[0]] = i

            # print(domain_objects_index_map)

            newConstraint = OspConstraint(name)
            newConstraint.predicate = predicate
            newConstraint.domain_objects_index_map = domain_objects_index_map
            return newConstraint

        if 'relaxation' in json_def:

            newConstraint = OspConstraint(name)
            newConstraint.relaxation_list = json_def['relaxation']
            return newConstraint


    def to_value_name(self, fact_name):
        predicate_parts = self.predicate.split('?')
        assert len(predicate_parts) == 2
        return fact_name.replace('Atom ' + predicate_parts[0], ''). \
            replace(predicate_parts[1], '')

    def add_to_task(self, sas_task):
        if self.relaxation_list:
            return self.add_to_task_relaxation_list_definition(sas_task)

        if self.predicate:
            return self.add_to_tasked_predicate_definition(sas_task)

    def add_to_task_relaxation_list_definition(self, sas_task):
        variables = sas_task.variables.value_names

        relaxation_ordering = []
        for fact in self. relaxation_list:
            var_value_id = self.find_var_value_id(variables, fact)
            assert var_value_id, fact + " not in grounded task"
            #print(fact + ' ' + str(var_value_id))
            relaxation_ordering.append(var_value_id)

        #print(relaxation_ordering)
        sas_task.set_osp_constraint(self.name, relaxation_ordering)

    @staticmethod
    def find_var_value_id(sas_variables, fact):
        for var_id, variable in enumerate(sas_variables):
            for  value_id, value in enumerate(variable):
                # print(fact + " " + value)
                if 'Atom ' + fact == value:
                    return var_id, value_id
        return None

    def add_to_tasked_predicate_definition(self, sas_task):
        predicate_regex = re.compile("Atom " + self.predicate.replace("?", "[a-zA-Z0-9]*").replace('(','\(').replace(')','\)'))

        variables = sas_task.variables.value_names
        variable_index = None

        # find the index of the variable and check if all values are based on the given predicate
        for i, v in enumerate(variables):
            num_matches = 0
            for value in v:
                if predicate_regex.match(value):
                    num_matches += 1
            assert(num_matches == 0 or num_matches == len(v))
            if num_matches == len(v):
                variable_index = i
                break

        assert(variable_index)
        print(variables[variable_index])

        init_value_index = sas_task.init.values[variable_index]
        predicate_parts = self.predicate.split('?')
        assert len(predicate_parts) == 2
        init_value_name = self.to_value_name(variables[variable_index][init_value_index])

        #print("init value name: " + init_value_name)
        #print("init value pos: " + str(self.domain_objects_index_map[init_value_name]))

        fact_names_and_index = [(fn, self.domain_objects_index_map[self.to_value_name(fn)], i)
                                for i, fn in enumerate(variables[variable_index])]
        fact_names_and_index.sort(key=lambda e: e[1])

        #print("Fact names and index:")
        #print(fact_names_and_index)

        relaxation_ordering = []
        for fact_name, pos_index, value_index  in fact_names_and_index:
            if pos_index < self.domain_objects_index_map[init_value_name]:
                continue
            #print(fact_name + ' (' + str(variable_index) + ', ' + str(value_index) + ')')
            relaxation_ordering.append((variable_index, value_index))

        #print(relaxation_ordering)

        sas_task.set_osp_constraint(self.name, relaxation_ordering)
