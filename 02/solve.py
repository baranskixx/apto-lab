from dimacs import loadGraph, isVC, edgeList, saveSolution
from queue import PriorityQueue
import multiprocessing
import glob
from os import remove

class Solver:
    def __init__(self, relational_path : str):
        self.approaches = [
            'approx_2',
            'approx_log'
        ]
        
        self.remove_solutions(relational_path)
        self.load_graphs(relational_path)
    
    def remove_solutions(self, relational_path : str):
        sol_files = glob.glob(pathname = relational_path + '/*.sol', recursive=False)

        for sol in sol_files:
            remove(sol)

    def load_graphs(self, relational_path : str):
        graph_files = glob.glob(pathname = relational_path + '/*', recursive=False)
        self.graphs = {}

        for graph_file in graph_files:
            graph_name = graph_file[graph_file.rfind('/') + 1 : ]
            self.graphs[graph_name] = loadGraph(graph_file)

    def run_for_all_graphs(self, approach, time_limit = 5):
        if approach not in self.approaches:
            raise ValueError('Not valid approach name!')
        
        func = globals()[approach]
        queue = multiprocessing.Queue()
        for graph_name, G in self.graphs.items():
            p = multiprocessing.Process(target=func, name="function", args=(queue, G))

            p.start()
            p.join(timeout=time_limit)

            if p.is_alive():
                print("Przekroczono czas na obliczenia dla grafu {}".format(graph_name))
                p.terminate()
            else:
                print("Obliczenia ukończone dla {}".format(graph_name))
                result = queue.get()

                result = set() if result is None else result

                saveSolution(name='graph/' + graph_name + '.sol', C=result)
                print("Wynik : {}".format(result))
            

def approx_2(queue, G):
    E = edgeList(G)

    C = set()

    while len(E) > 0:
        u, v = E.pop()
        C |= {u, v}

        E = [e for e in E if u not in e and v not in e]

    queue.put(C)
    return C

def approx_log(queue, G):
    V = len(G)
    E = edgeList(G)
    C = set()
    

    while len(E) > 0:
        D = [0] * V

        for e in E:
            D[e[0]] += 1
        
        max_value = max(D)
        u = D.index(max_value)

        E = [e for e in E if u not in e]
        C |= {u}
        

    queue.put(C)
    return C


def main():
    solver = Solver('./graph')
    solver.run_for_all_graphs('approx_log', time_limit=10)

if __name__ == '__main__':
    main()