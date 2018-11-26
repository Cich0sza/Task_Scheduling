import configparser
import math
import time
from collections import defaultdict

from tqdm import tqdm

from functions import load_file, save_as_latex_table, save_to_validate
from htmlparser import Parser
from rhrm import RHRM
from selfevolution import SelfEvolution
from supportclass import Result


def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    config = config['DEFAULT']

    n = config.getint('n')
    _n = math.floor(math.sqrt(n))
    h = config.getfloat('h')
    iteration = config.getint('Iteration')
    strad = config.getboolean('Straddling function')
    if 'File name' in config:
        file_name = config.get('File name')
    else:
        file_name = f'sch{n}'

    problems = load_file(file_name)
    up = Parser().parse()
    results = defaultdict(list)
    times = [0 for _ in range(iteration + 1)]

    for _ in tqdm(range(iteration)):
        for i, p in enumerate(problems):
            start_time = time.time()
            s = RHRM(p, h, 5, 10, strad)
            solution = s.solve()
            se = SelfEvolution(p, solution, 5, 10 * _n, 3 * _n)
            solution = se.start()
            results[i + 1].append(Result(solution, time.time() - start_time, n, h, i + 1))
            times[i + 1] += time.time() - start_time

    save_as_latex_table(up, n, results, times)
    save_to_validate(file_name, results, h)


if __name__ == "__main__":
    main()
