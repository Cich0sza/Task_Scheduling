import os
import pickle

import requests
from bs4 import BeautifulSoup


class UpperBound:
    def __init__(self, n, k, h, v, o=False):
        self.n = n
        self.k = k
        self.h = h
        self.value = v
        self.optimal = o

    def get_key(self):
        return self.n, self.k, self.h

    def calculate_diff(self, value):
        return ((value - self.value) / self.value) * 100


class Parser:
    def __init__(self):
        self._url = 'http://people.brunel.ac.uk/~mastjjb/jeb/orlib/schinfo.html'
        self._current_n = 0
        self._current_k = 0
        self._h = [0.2, 0.4, 0.6, 0.8]
        self._data = {}

    def parse(self):
        if os.path.exists('upper_bound'):
            self._load_data()
        else:
            data = self._download_data()
            self._parse_data(data)
            self._save_ub()
        return self._data

    def _download_data(self):
        page = requests.get(self._url, allow_redirects=True)
        soup = BeautifulSoup(page.content, 'html.parser')
        return soup.find_all('pre')[0].text.strip()

    def _parse_data(self, data):
        for line in data.split('\r\n'):
            line = ' '.join(line.split())
            if line.startswith('n='):
                self._handle_n_line(line)
            elif line.startswith('k'):
                self._handle_k_line(line)
            # else:
            #     print('Warning! Different line')

    def _handle_n_line(self, line):
        n = line.split()[0].split('=')[1]
        self._current_n = int(float(n))

    def _handle_k_line(self, line):
        data = line.split()
        self._current_k = int(float(data[2]))
        if len(data) == 8:
            self._handle_value(data[4:])
        else:
            self._handle_value(data[3:])

    def _handle_value(self, data):
        for i, d in enumerate(data):
            optimal = False
            d = ''.join(d.split(','))
            if d[-1] == '*':
                optimal = True
                d = d[:-1]
            d = int(float(d))
            u_b = UpperBound(self._current_n, self._current_k, self._h[i], d, optimal)
            self._data[u_b.get_key()] = u_b

    def _save_ub(self):
        with open('upper_bound', 'wb+') as file:
            pickle.dump(self._data, file)

    def _load_data(self):
        with open('upper_bound', 'rb') as file:
            self._data = pickle.load(file)



# if __name__ == '__main__':
#     parser = Parser()
#     data = parser.parse()
#     # print(len(data))
