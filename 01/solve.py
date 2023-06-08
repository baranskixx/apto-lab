from dimacs import loadGraph, isVC, edgeList
from itertools import combinations
import multiprocessing
import glob

class Solver:
    def __init__(self, relational_path : str):
        self.approaches = [
            'brute_force',
            'recursion_2k',
            'recursion_1_618k',
            'recursion_1_47k'
        ]
        self.load_graphs(relational_path)
    
    def load_graphs(self, relational_path : str):
        graph_files = glob.glob(pathname = relational_path, recursive=False)
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
            p = multiprocessing.Process(target=func, name="function", args=(queue, G, 20))

            p.start()
            p.join(timeout=time_limit)

            if p.is_alive():
                print("Przekroczono czas na obliczenia dla grafu {}".format(graph_name))
                p.terminate()
            else:
                print("Obliczenia ukończone dla {}".format(graph_name))
                result = queue.get()
                print("Wynik : {}".format(result))
            

def brute_force(queue, G, k=10):
    V = len(G)
    E = edgeList(G)
    for C in combinations(range(V+1), k):
        if isVC(E=E, C=C):
            queue.put(C)
            return C
    queue.put(None)
    return None

def recursion_2k(queue, G, k=10):
    def rec(E, k, s = set()):
        if k == 0:
            return None

        for u, v in E:
            if u not in s and v not in s:
                set1 =  rec(E, k-1, s | {u})
                set2 =  rec(E, k-1, s | {v})

                if set1:
                    return set1
                else:
                    return set2
        return s
    
    E = edgeList(G)
    result = rec(E, k)        
    queue.put(result)
    return result 

def recursion_1_618k(queue, G, k=10):
    def rec(G, k, s = set(), covered = set()):
        if k <= 0:
            return None

        for u in range(len(G)):
            if u not in covered:
                neigh = G[u]
                set1 = rec(G, k-1, s | {u}, covered | {u} | neigh)
                if set1:
                    return set1
                else:
                    new_s = (s | neigh) - s
                    return rec(G, k - len(new_s), s | neigh, covered | {u} | neigh)
        
        return s
    
    result = rec(G, k)        
    queue.put(result)
    return result 

def recursion_1_47k(queue, G, k=10):
    def rec(G, k, s = set(), covered = set()):
        if k <= 0:
            return None
        
        V = len(G)
        D = [(u, len(G[u])) for u in (set(range(V)) - covered)]

        if len(D) == 0:
            return s

        u = sorted(D, key = lambda x : x[1] * (-1))[0][0]

        neigh = G[u]
        set1 = rec(G, k-1, s | {u}, covered | {u} | neigh)
        if set1:
            return set1
        else:
            new_s = (s | neigh) - s
            return rec(G, k - len(new_s), s | neigh, covered | {u} | neigh)
    
    result = rec(G, k)        
    queue.put(result)
    return result 

def main():
    solver = Solver('./graph/*')
    solver.run_for_all_graphs('recursion_1_47k')

if __name__ == '__main__':
    main()