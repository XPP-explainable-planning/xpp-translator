

class Relaxation():

    def __init__(self, name, order):
        self.name = name
        self.order = [e.split(' ') for e in order]

    @staticmethod
    def parse(json_def):
        assert 'name' in json_def and 'order' in json_def
        print('Parse relaxation ...')
        return Relaxation(json_def['name'], json_def['order'])
