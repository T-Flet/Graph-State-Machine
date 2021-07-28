from typing import *
Score = Callable[[List[str], List[str]], float]
    # Functions which compare two lists of nodes (e.g. the state and a given node's neighbours) and produce a numerical
    # score representing how similar/different they are.
    # IMPORTANT NOTES:
    #   - The framework treats higher values as better
    #   - The by_score Scanner constructor uses these scores with the state list in the first argument and the candidate list as the second
    #   - These functions take lists (while the provided ones convert them to sets) because for some cases order and duplicates might be of interest


# Continuous scorers

def jaccard_similarity(a: List, b: List) -> float: return len((s1 := set(a)).intersection((s2 := set(b)))) / len(s1.union(s2))

def presence_score(a: List, b: List) -> float: return len(set(a).intersection(set(b))) / len(a)

def reverse_presence_score(a: List, b: List) -> float: return len(set(a).intersection(set(b))) / len(b)



# Discrete scorers

def perfect_match(a: List, b: List) -> int: return int(set(a) == set(b))

def all_left_match(a: List, b: List) -> int: return int(set(a).issubset(set(b)))

def all_right_match(a: List, b: List) -> int: return int(set(b).issubset(set(a)))


