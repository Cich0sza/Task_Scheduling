import os

import requests

from htmlparser import UpperBound
from supportclass import Task, Problem, Result


def create_dir_path(dir_name='dataset'):
    dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), dir_name)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    return dir_path


def download_file(file_name, file_path):
    url = 'http://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/'
    file_name_with_extension = '.'.join((file_name, 'txt'))
    full_url = ''.join((url, file_name_with_extension))
    r = requests.get(full_url, allow_redirects=True)
    with open(file_path, 'w+') as file:
        file.write(r.content.decode('utf-8'))
        r.close()


def load_file(file_name):
    dir_path = create_dir_path()
    file_path = os.path.join(dir_path, '.'.join((file_name, 'txt')))
    if not os.path.exists(file_path):
        download_file(file_name, file_path)

    problems = []
    with open(file_path, "r") as file:
        number_of_problems = int(float(file.readline().split()[0]))
        for i in range(1, number_of_problems + 1):
            number_of_jobs = int(float(file.readline().split()[0]))
            tasks = []
            for j in range(number_of_jobs):
                tasks.append(Task.read_task_from_file(j, file.readline()))
            problems.append(Problem(number_of_jobs, i, tasks))
        return problems


def save_as_latex_table(up, n, results, times):
    dir_path = create_dir_path('latex_output')
    with open(os.path.join(dir_path, f'latex_output_n_{n}.txt'), 'w+', encoding='utf-8') as file:
        file.write('\\begin{tabular}{c|c|c|c|c}\n')
        file.write('\t\\hline\n')
        file.write('\t\tk & $$F_{ab}$$ & $$F_{a}$$ & Błąd & Czas[s] \\\\\n')
        for k, v in results.items():
            best: Result = min(v, key=lambda x: x.penalty)
            tmp_up: UpperBound = up[best.get_key()]
            file.write('\t\t{:d} & {:d} & {:d} & {:.2f}\\% & {:.2f} \\\\\n'.format(best.k, tmp_up.value, best.penalty,
                                                                                   tmp_up.calculate_diff(best.penalty),
                                                                                   best.time))
        file.write('\t\\hline\n')
        file.write('\\end{tabular}\n')


def save_to_validate(file_name, results, h):
    dir_path = create_dir_path('output')
    for k, result in results.items():
        with open(os.path.join(dir_path, f'{file_name}_{k}_{int(h * 10)}.txt'), 'w+', encoding='utf-8') as file:
            best: Result = min(result, key=lambda x: x.penalty)
            file.write(best.__str__())

