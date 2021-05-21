import re

class OspConstraint:

    def __init__(self, name, predicate, domain_objects_index_map):
        self.name = name
        self.predicate = predicate
        self.init_value = None
        self.value_relaxation_order = None
        self.domain_objects_index_map = domain_objects_index_map
        self.variable_index = None


    @staticmethod
    def parse(json_def, typeObjectMap):
        name = json_def['name'] # e.g. some name
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

        newConstraint = OspConstraint(name, predicate, domain_objects_index_map)
        return newConstraint


    def to_value_name(self, fact_name):
        predicate_parts = self.predicate.split('?')
        assert len(predicate_parts) == 2
        return fact_name.replace('Atom ' + predicate_parts[0], ''). \
            replace(predicate_parts[1], '')

    def add_to_task(self, sas_task):

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

        print("init value name: " + init_value_name)
        print("init value pos: " + str(self.domain_objects_index_map[init_value_name]))

        fact_names_and_index = [(fn, self.domain_objects_index_map[self.to_value_name(fn)], i) for i, fn in enumerate(variables[variable_index])]
        fact_names_and_index.sort(key=lambda e: e[1])

        print("Fact names and index:")
        print(fact_names_and_index)

        relaxation_ordering = []
        order_index = 0
        for fact_name, pos_index, value_index  in fact_names_and_index:
            if pos_index < self.domain_objects_index_map[init_value_name]:
                continue
            relaxation_ordering.append((value_index, order_index))
            order_index += 1

        print(relaxation_ordering)

        sas_task.set_osp_constraint(self.name, variable_index, relaxation_ordering)
