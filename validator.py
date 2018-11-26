import configparser
import os

from functions import load_file, create_dir_path
from supportclass import Problem


class Validate:

    def __init__(self, penalty, g, order):
        self.penalty = int(float(penalty))
        self.g = int(float(g))
        self.order = [int(float(o)) for o in order]

    def change_order(self, problem: Problem):
        tasks = problem.tasks
        new_tasks = [tasks[i] for i in self.order]
        problem.tasks = new_tasks

    @staticmethod
    def load_file_to_validate(file_name):
        with open(os.path.join(create_dir_path('output'), file_name), 'r') as file:
            lines = file.readlines()
            assert len(lines) == 1
            data = lines[0].split()
            return Validate(data[0], data[1], data[2:])

    def calculate_total_penalty(self, problem_to_validate: Problem, d):
        current_time = self.g
        penalty = 0
        for t in problem_to_validate.tasks:
            current_time += t.p
            if d >= current_time:
                penalty += t.a * max(0, d - current_time)
            else:
                penalty += t.b * max(current_time - d, 0)

        assert penalty == self.penalty
        return penalty

    def validate(self, problem: Problem, h):
        self.change_order(problem)
        return self.calculate_total_penalty(problem, problem.calculate_d(h))


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    config = config['VALIDATE']

    problem_file = config.get('Problem file')
    validate_file = config.get('Validate file')
    k = config.getint('k')
    h = config.getfloat('h')

    problems = load_file(problem_file)
    validator = Validate.load_file_to_validate(validate_file)
    validator.validate(problems[k-1], h)
