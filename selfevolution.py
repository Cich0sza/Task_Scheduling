import random

from tqdm import tqdm

from supportclass import Solution, Problem, StraddlingVShapeNew, ImproverGNew


class SelfEvolution:
    def __init__(self, problem: Problem, solution: Solution, g_times, j_max, i_max):
        self.problem = problem
        self.g = solution.g
        self.d = solution.d
        self.g_times = g_times
        self.j_max = j_max
        self.i_max = i_max
        self.original_set_e = [t.task_id for t in solution.set_e]
        self.original_set_t = [t.task_id for t in solution.set_t]
        self.best_set_e = [t.task_id for t in solution.set_e]
        self.best_set_t = [t.task_id for t in solution.set_t]
        self.best_g = 0
        self.best_penalty = self._calculate_penalty(self.best_set_e, self.best_set_t, self.best_g)
        self.set_e = []
        self.set_t = []

    def start(self):
        for j in range(self.j_max):
            self._local_evolution()
            if j % self.g_times == 0:
                self._g_improve()
        return Solution(self.best_set_e, self.best_set_t, self.best_g, self.d, self.best_penalty)

    def _g_improve(self):
        improver = ImproverGNew(self.problem, self.set_e, self.set_t, self.d, self.g)
        new_g = improver.improve()
        new_penalty = self._calculate_penalty(self.set_e, self.set_t, new_g)

        if new_penalty < self.best_penalty:
            self.g = new_g

    def _local_evolution(self):
        for i in range(self.i_max):
            self.set_e = [i for i in self.original_set_e]
            self.set_t = [i for i in self.original_set_t]
            self._step_1()
            self._step_2()

    def _step_1(self):
        self._swap_task()
        self._pure_v()
        new_penalty = self._calculate_penalty(self.set_e, self.set_t, self.g)
        if new_penalty < self.best_penalty:
            self.best_set_e = [t for t in self.set_e]
            self.best_set_t = [t for t in self.set_t]
            self.best_g = self.g
            self.best_penalty = new_penalty

    def _swap_task(self):
        task_1 = self._take_task(self.set_e)
        task_2 = self._take_task(self.set_t)
        self.set_e.append(task_2)
        self.set_t.append(task_1)

    @staticmethod
    def _take_task(set_s):
        task = random.choice(set_s)
        set_s.remove(task)
        return task

    def _pure_v(self):
        time_e = self.g + sum([self.problem.tasks[t].p for t in self.set_e])
        self.set_e = [x for _, x in sorted([(self.problem.tasks[i].p_b, i) for i in self.set_e],
                                           key=lambda x: x[0], reverse=True)]
        while time_e > self.d:
            task = self.set_e.pop()
            self.set_t.append(task)
            t = self.problem.tasks[task]
            time_e -= t.p

        self.set_t = [x for _, x in sorted([(self.problem.tasks[i].p_b, i) for i in self.set_t],
                                           key=lambda x: x[0], reverse=False)]
        self.set_e = [x for _, x in sorted([(self.problem.tasks[i].p_a, i) for i in self.set_e],
                                           key=lambda x: x[0], reverse=True)]

    def _step_2(self):
        svs = StraddlingVShapeNew(self.problem, self.set_e, self.set_t, self.d, self.g)
        new_set_e, new_set_t = svs.create()
        new_penalty = self._calculate_penalty(new_set_e, new_set_t, self.g)

        if new_penalty < self.best_penalty:
            self.best_set_e = [t for t in new_set_e]
            self.best_set_t = [t for t in new_set_t]
            self.best_g = self.g
            self.best_penalty = new_penalty

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
