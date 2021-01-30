from typing import *
Score = Callable[[List[str], List[str]], float]
    # Functions which compare two lists of nodes (e.g. the state and a given node's neighbours) and produce a numerical
    # score representing how similar/different they are. The framework treats higher values as better.


def jaccard_similarity(a: List, b: List) -> float: return len((s1 := set(a)).intersection((s2 := set(b)))) / len(s1.union(s2))

def presence_score(a: List, b: List) -> float: return len(set(a).intersection(set(b))) / len(a)



# Discrete scorers
# def perfect_match(a: List, b: List): return # 0,1
#
# def all_left_match(a: List, b: List): return # 0,1
#
# def all_right_match(a: List, b: List): return # 0,1


