import copy
import math

import numpy as np

from supportclass import Task, Solution, StraddlingVShape, ImproverG


class RHRM:
    def __init__(self, problem, h, la, mi, strad=True):
        self.problem = problem
        self.problem_size = len(problem.tasks)
        self.set_a: list = copy.deepcopy(problem.tasks)  # Set of jobs to be allocated
        self.g = 0  # Idle time before the starting of the first job in a schedule
        self.set_e = []  # Set of jobs completed at or before due date
        self.set_t = []  # Set of jobs completed after due date
        self.h = h  # The parameter to set due date
        self.H = problem.calculate_total_processing_time()  # The sum of total job processing time
        self.d = math.floor(self.h * self.H)  # The due date, which is set to be h*H
        self.e_space = 0  # The space available for inserting jobs before due date
        self.t_space = 0  # The space available for inserting jobs after due date
        self.j_e: Task = None  # Candidate to be inserted into sE
        self.j_t: Task = None  # Candidate to be inserted into sT

        self.solution = None
        self.best_solution = None
        self.best_solution_penalty = 0

        # Control
        self.strad = strad
        self.la = 0
        self.mi = 0
        self.la_max = la
        self.mi_max = mi

    def solve(self):
        while self.la != self.la_max:
            if self.mi == self.mi_max:
                break
            self._step_1()
            self._step_2()
            assert len(self.set_t) + len(self.set_e) == len(self.problem.tasks)
            self._step_5()
            self._step_6()
            self._step_7()
            self._reset()
        return self.best_solution

    # --------------------------------------------------------------------------
    # - Step 1
    # --------------------------------------------------------------------------

    def _step_1(self):
        self._calculate_g()
        self._calculate_space()

    def _calculate_g(self):
        if self.h <= 0.4:
            self.g = 0
        elif self.h <= 0.6:
            self.g = np.random.randint(0, math.floor(self.H * 0.2))
        else:
            self.g = np.random.randint(math.floor(self.H * 0.05), math.floor(self.H * 0.4))

    def _calculate_space(self):
        self.e_space = self.d - self.g
        self.t_space = self.g + self.H - self.d

    # --------------------------------------------------------------------------
    # - Step 2
    # --------------------------------------------------------------------------

    def _step_2(self):
        while len(self.set_a) > 0:
            if self.e_space > self.t_space:
                self.j_e = self._select_task(lambda x: x.p_a)
                self._step_3()
            else:
                self.j_t = self._select_task(lambda x: x.p_b)
                self._step_4()
            self.j_t = None
            self.j_e = None

    def _select_task(self, key):
        if len(self.set_a) > 1:
            candidate_1, candidate_2 = self._select_2_candidates(key)
            return self._random(candidate_1, candidate_2)
        else:
            return self._select_1_candidate(key)

    def _select_2_candidates(self, key):
        candidate_1 = self._select_1_candidate(key)
        candidate_2 = self._select_1_candidate(key)
        return candidate_1, candidate_2

    def _select_1_candidate(self, key):
        candidate = max(self.set_a, key=key)
        self.set_a.remove(candidate)
        return candidate

    def _random(self, first, second):
        if np.random.random() > 0.5:
            result = first
            self.set_a.append(second)
        else:
            result = second
            self.set_a.append(first)
        return result

    # --------------------------------------------------------------------------
    # - Step 3
    # --------------------------------------------------------------------------

    def _step_3(self):
        if self.e_space - self.j_e.p >= 0:
            self.e_space = self._assign_j_s_to_set(self.j_e, self.set_e, self.e_space)
        else:
            self.t_space = self._assign_j_s_to_set(self.j_e, self.set_t, self.t_space)

    @staticmethod
    def _assign_j_s_to_set(j_s: Task, set_s: list, space_s: int):
        set_s.append(j_s)
        return space_s - j_s.p

    # --------------------------------------------------------------------------
    # - Step 4, uses the functions of step 3
    # --------------------------------------------------------------------------

    def _step_4(self):
        self.t_space = self._assign_j_s_to_set(self.j_t, self.set_t, self.t_space)

    # --------------------------------------------------------------------------
    # - Step 5
    # --------------------------------------------------------------------------

    def _step_5(self):
        self.set_t.sort(key=lambda x: x.p_b, reverse=False)
        self._check_set_t()
        self.set_e.sort(key=lambda x: x.p_a, reverse=True)

    def _check_set_t(self):
        processing_time = self.g + sum([t.p for t in self.set_e])
        assert processing_time <= self.d
        for t in self.set_t:
            if processing_time + t.p <= self.d:
                self._change_set(t)
                processing_time += t.p
            else:
                break

    def _change_set(self, task):
        self.set_e.append(task)
        self.set_t.remove(task)
        assert len(self.set_t) + len(self.set_e) == self.problem_size

    # --------------------------------------------------------------------------
    # - Step 6
    # --------------------------------------------------------------------------

    def _step_6(self):
        self._try_improve_g()
        if self.strad:
            self._try_to_create_straddling_solution()

    def _try_improve_g(self):
        solution = self._save_state()
        old_penalty = solution.calculate_penalty()
        improver = ImproverG(solution)
        new_solution: Solution = improver.improve()
        new_penalty = new_solution.calculate_penalty()

        if new_penalty < old_penalty:
            self.solution = new_solution
            self._load_state(new_solution)
        else:
            self.solution = solution

    def _try_to_create_straddling_solution(self):
        solution = self.solution
        old_penalty = solution.calculate_penalty()
        svs = StraddlingVShape(solution)
        new_solution: Solution = svs.create()
        new_penalty = new_solution.calculate_penalty()

        if new_penalty < old_penalty:
            self.solution = new_solution
            self._load_state(new_solution)

    # --------------------------------------------------------------------------
    # - Step 7
    # --------------------------------------------------------------------------

    def _step_7(self):
        if self.best_solution is None:
            self.best_solution = self.solution
            self.best_solution_penalty = self.solution.calculate_penalty()
        else:
            penalty = self.solution.calculate_penalty()
            if self.best_solution_penalty > penalty:
                self.best_solution = self.solution
                self.best_solution_penalty = penalty
                self.la += 1
                self.mi = 0
            else:
                self.mi += 1

    # --------------------------------------------------------------------------
    # - Other functions
    # --------------------------------------------------------------------------

    def _save_state(self):
        return Solution(self.set_e, self.set_t, self.g, self.d)

    def _load_state(self, solution: Solution):
        self.set_e = solution.set_e
        self.set_t = solution.set_t
        self.g = solution.g
        self.d = solution.d

    def _reset(self):
        self.set_a: list = copy.deepcopy(self.problem.tasks)
        self.g = 0
        self.set_e = []
        self.set_t = []
        self.e_space = 0
        self.t_space = 0
        self.j_e: Task = None
        self.j_t: Task = None
        self.solution = None

    # --------------------------------------------------------------------------
    # - Class functions
    # --------------------------------------------------------------------------

    @staticmethod
    def _calculate_total_penalty(set_e, set_t, d, g):
        current_time = g
        penalty = 0
        task_set = set_e + set_t
        for t in task_set:
            current_time += t.p
            if d >= current_time:
                penalty += t.a * max(0, d - current_time)
            else:
                penalty += t.b * max(current_time - d, 0)
        return penalty
