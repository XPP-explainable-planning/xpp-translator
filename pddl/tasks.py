from __future__ import print_function

from . import axioms
from . import predicates
from . import conditions
from . import effects
from . import actions


class Task(object):
    def __init__(self, domain_name, task_name, requirements,
                 types, objects, predicates, functions, init, goal,
                 actions, axioms, use_metric):
        self.domain_name = domain_name
        self.task_name = task_name
        self.requirements = requirements
        self.types = types
        self.objects = objects
        self.predicates = predicates
        self.functions = functions
        self.init = init
        self.goal = goal
        self.actions = actions
        self.axioms = axioms
        self.axiom_counter = 0
        self.use_min_cost_metric = use_metric

    def add_axiom(self, parameters, condition):
        name = "new-axiom@%d" % self.axiom_counter
        self.axiom_counter += 1
        axiom = axioms.Axiom(name, parameters, len(parameters), condition)
        self.predicates.append(predicates.Predicate(name, parameters))
        self.axioms.append(axiom)
        return axiom

    def add_relax_action(self, fact_order):

        for i in range(len(fact_order) - 1):
            fact0 = fact_order[i]
            fact1 = fact_order[i + 1]
            precondition = conditions.Atom(fact0[0], fact0[1:])
            eff_set = conditions.Atom(fact1[0], fact1[1:])
            eff_unset = conditions.NegatedAtom(fact0[0], fact0[1:])
            effs = [effects.Effect([], conditions.Truth(), eff_set),
                    effects.Effect([], conditions.Truth(), eff_unset)]

            action = actions.Action('relax_' + str(i), [], 0, precondition, effs, 0)
            self.actions.append(action)

    def dump(self):
        print("Problem %s: %s [%s]" % (
            self.domain_name, self.task_name, self.requirements))
        print("Types:")
        for type in self.types:
            print("  %s" % type)
        print("Objects:")
        for obj in self.objects:
            print("  %s" % obj)
        print("Predicates:")
        for pred in self.predicates:
            print("  %s" % pred)
        print("Functions:")
        for func in self.functions:
            print("  %s" % func)
        print("Init:")
        for fact in self.init:
            print("  %s" % fact)
        print("Goal:")
        self.goal.dump()
        print("Actions:")
        for action in self.actions:
            action.dump()
        if self.axioms:
            print("Axioms:")
            for axiom in self.axioms:
                axiom.dump()

    def to_json(self, stream):
        print("{", file=stream)
        print("\"types\": [\t", file=stream)
        print("\t" + ", ".join(["\"" + t.name + "\"" for t in self.types]), file=stream)
        print("],", file=stream)

        print("\"objects\": [", file=stream)
        obj_json = []
        for ob in self.objects:
            s = "\t{"
            s += "\t\t\"name\": \"" + ob.name + "\",\n"
            s += "\t\t\"type\": \"" + ob.type_name + "\"\n"
            s += "\t}\n"
            obj_json.append(s)
        print(", ".join(obj_json), file=stream)
        print("],", file=stream)

        print("\"predicates\": [", file=stream)
        print(",\n".join([pred.to_json() for pred in self.predicates]), file=stream)
        print("],", file=stream)

        print("\"init\": [", file=stream)
        print(",".join(["\"" + a.to_JSON() + "\"" for a in self.init]), file=stream)
        print("],", file=stream)

        print("\"goal\": " + self.goal.to_JSON() + ",", file=stream)

        print("\"actions\": [", file=stream)
        print(",\n".join([a.to_json() for a in self.actions]), file=stream)
        print("]", file=stream)
        print("}", file=stream)


class Requirements(object):
    def __init__(self, requirements):
        self.requirements = requirements
        for req in requirements:
            assert req in (
                ":strips", ":adl", ":typing", ":negation", ":equality",
                ":negative-preconditions", ":disjunctive-preconditions",
                ":existential-preconditions", ":universal-preconditions",
                ":quantified-preconditions", ":conditional-effects",
                ":derived-predicates", ":action-costs"), req

    def __str__(self):
        return ", ".join(self.requirements)
