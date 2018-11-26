import copy
import math


class Problem:
    def __init__(self, n, k, tasks):
        self.n = n
        self.k = k
        self.tasks = tasks

    def calculate_total_processing_time(self):
        return sum([t.p for t in self.tasks])

    def __str__(self):
        return '{' + ', '.join([t.__str__() for t in self.tasks]) + '}'

    def calculate_d(self, h):
        return math.floor(self.calculate_total_processing_time() * h)


class Task:
    def __init__(self, taks_id, p, a, b):
        self.task_id = int(float(taks_id))
        self.p = int(float(p))
        self.a = int(float(a))
        self.b = int(float(b))
        self.p_a = self.p / self.a
        self.p_b = self.p / self.b

    @staticmethod
    def read_task_from_file(i, line):
        p, a, b = line.split()
        return Task(i, p, a, b)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'{self.task_id}'


class Solution:
    def __init__(self, set_e, set_t, g, d, penalty=0):
        self.set_e: list = set_e
        self.set_t: list = set_t
        self.g = g
        self.d = d
        self.penalty = penalty

    def calculate_penalty(self):
        current_time = self.g
        penalty = 0
        task_set = self.set_e + self.set_t
        for t in task_set:
            try:
                current_time += t.p
            except AttributeError:
                print(task_set)
            if self.d >= current_time:
                penalty += t.a * max(0, self.d - current_time)
            else:
                penalty += t.b * max(current_time - self.d, 0)
        return penalty

    def __str__(self) -> str:
        return 'Solution { ' + \
               f'penalty: {self.penalty}, g: {self.g}, set_t: {self.set_t}, set_e: {self.set_e}, d: {self.d}' + \
               ' }'

    def __repr__(self) -> str:
        return self.__str__()

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.d = self.d
        result.g = self.g
        result.penalty = self.penalty
        result.set_t = [t for t in self.set_t]
        result.set_e = [t for t in self.set_e]
        return result


class Result:
    def __init__(self, solution: Solution, _time, n, h, k):
        self.solution = solution
        self.penalty = solution.penalty
        self.g = solution.g
        self.tasks = solution.set_e + solution.set_t
        self.time = _time
        self.n = n
        self.h = h
        self.k = k

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'{self.penalty} {self.g} ' + ' '.join([str(x) for x in self.tasks])

    def get_key(self):
        return self.n, self.k, self.h


class ImproverG:
    def __init__(self, solution):
        self.new_solution = copy.copy(solution)
        self.set_t: list = self.new_solution.set_t
        self.set_e: list = self.new_solution.set_e
        self.d = self.new_solution.d
        self.g = self.new_solution.g
        self.start_penalty = solution.calculate_penalty()

    def improve(self):
        self._improvement_g()
        return self.new_solution

    def _improvement_g(self):
        processing_time = sum([t.p for t in self.set_e])
        self.new_solution.g = self.d - processing_time
        second_penalty = self.new_solution.calculate_penalty()
        if self.start_penalty >= second_penalty:
            self._improvement_g_step_1(-1, second_penalty)
        else:
            self._improvement_g_step_2(0, second_penalty)

    def _improvement_g_step_1(self, i, last_penalty):
        if abs(i) > len(self.set_e):
            return
        self.new_solution.g += self.set_e[i].p
        new_penalty = self.new_solution.calculate_penalty()
        if new_penalty > last_penalty:
            return
        else:
            return self._improvement_g_step_1(i - 1, new_penalty)

    def _improvement_g_step_2(self, i, last_penalty):
        if abs(i) == len(self.set_t):
            return
        self.new_solution.g = max(0, self.new_solution.g - self.set_t[i].p)
        new_penalty = self.new_solution.calculate_penalty()
        if new_penalty > last_penalty:
            return
        elif self.new_solution.g == 0:
            return
        else:
            return self._improvement_g_step_2(i + 1, new_penalty)


class StraddlingVShape:
    def __init__(self, solution):
        self.tmp_solution = copy.deepcopy(solution)
        self.set_t: list = self.tmp_solution.set_t
        self.set_e: list = self.tmp_solution.set_e
        self.d = self.tmp_solution.d
        self.pt_t = sum(x.p for x in self.set_t)
        self.pt_e = self.tmp_solution.g + sum(x.p for x in self.set_e)
        self.stradJob: Task = None

    def create(self):
        for task in self.set_t:
            if self.stradJob is None:
                self._check_task(task)
            else:
                break
        self._create_v_shape()
        return self.tmp_solution

    def _check_task(self, task):
        for _ in range(1, len(self.set_e)):
            time = self.pt_e - self.set_e[-1].p
            if time + task.p > self.d:
                self._set_strad_job(task)
                self._swap_last_task()
                self.pt_e = time
            else:
                break

    def _set_strad_job(self, task):
        if self.stradJob is None:
            self.set_t.remove(task)
            self.stradJob = task

    def _swap_last_task(self):
        task = self.set_e.pop()
        self.set_t.insert(0, task)

    def _create_v_shape(self):
        self.set_e.sort(key=lambda x: x.p_a, reverse=True)
        self.set_t.sort(key=lambda x: x.p_b, reverse=False)
        if self.stradJob is not None:
            self.set_t.insert(0, self.stradJob)

    def _prepare_solution(self):
        self.tmp_solution.set_e = self.set_e
        return self.tmp_solution


class StraddlingVShapeNew:
    def __init__(self, problem, set_e, set_t, d, g):
        self.problem = problem
        self.set_t: list = set_t
        self.set_e: list = set_e
        self.d = d
        self.pt_t = sum([self.problem.tasks[x].p for x in self.set_t])
        self.pt_e = g + sum([self.problem.tasks[x].p for x in self.set_e])
        self.stradJob = -1

    def create(self):
        for task in self.set_t:
            if self.stradJob == -1:
                self._check_task(task)
            else:
                break
        self._create_v_shape()
        return self.set_e, self.set_t

    def _check_task(self, task):
        for _ in range(1, len(self.set_e)):
            time = self.pt_e - self.problem.tasks[self.set_e[-1]].p
            if time + self.problem.tasks[task].p > self.d:
                self._set_strad_job(task)
                self._swap_last_task()
                self.pt_e = time
            else:
                break

    def _set_strad_job(self, task):
        if self.stradJob == -1:
            self.set_t.remove(task)
            self.stradJob = task

    def _swap_last_task(self):
        task = self.set_e.pop()
        self.set_t.insert(0, task)

    def _create_v_shape(self):
        self.set_t = [x for _, x in sorted([(self.problem.tasks[i].p_b, i) for i in self.set_t],
                                           key=lambda x: x[0], reverse=False)]
        self.set_e = [x for _, x in sorted([(self.problem.tasks[i].p_a, i) for i in self.set_e],
                                           key=lambda x: x[0], reverse=True)]
        if self.stradJob != -1:
            self.set_t.insert(0, self.stradJob)


class ImproverGNew:
    def __init__(self, problem, set_e, set_t, d, g):
        self.problem = problem
        self.set_t: list = set_t
        self.set_e: list = set_e
        self.d = d
        self.g = g
        self.start_penalty = self._calculate_penalty(set_e, set_t, g)

    def improve(self):
        self._improvement_g()
        return self.g

    def _improvement_g(self):
        processing_time = sum([self.problem.tasks[t].p for t in self.set_e])
        self.g = self.d - processing_time
        second_penalty = self._calculate_penalty(self.set_e, self.set_t, self.g)
        if self.start_penalty >= second_penalty:
            self._improvement_g_step_1(-1, second_penalty)
        else:
            self._improvement_g_step_2(0, second_penalty)

    def _improvement_g_step_1(self, i, last_penalty):
        if abs(i) > len(self.set_e):
            return
        self.g += self.problem.tasks[self.set_e[i]].p
        new_penalty = self._calculate_penalty(self.set_e, self.set_t, self.g)
        if new_penalty > last_penalty:
            return
        else:
            return self._improvement_g_step_1(i - 1, new_penalty)

    def _improvement_g_step_2(self, i, last_penalty):
        if abs(i) == len(self.set_t):
            return
        self.g = max(0, self.g - self.problem.tasks[self.set_t[i]].p)
        new_penalty = self._calculate_penalty(self.set_e, self.set_t, self.g)
        if new_penalty > last_penalty:
            return
        elif self.g == 0:
            return
        else:
            return self._improvement_g_step_2(i + 1, new_penalty)

    def _calculate_penalty(self, set_e, set_t, g):
        current_time = g
        penalty = 0
        task_set = set_e + set_t
        for t in task_set:
            task = self.problem.tasks[t]
            current_time += task.p
            if self.d >= current_time:
                penalty += task.a * max(0, self.d - current_time)
            else:
                penalty += task.b * max(current_time - self.d, 0)
        return penalty
