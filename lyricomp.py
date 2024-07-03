

# def extract_verse(syllables, poem):
#     return poem[:syllables], poem[syllables:]
    
# def versification_bt(poem):
#     if poem == []:
#         yield []
#     else:
#         for syllables in [8, 11, 16]:
#             if len(poem) >= syllables:
#                 current_verse, rest = extract_verse(syllables, poem)
#                 for candidate_versification in versification_bt(rest):
#                     yield [current_verse] + candidate_versification

# def versification(poem):
#     return versification_bt(list(filter(lambda x: x != '', Pyverse(poem).syllables.split('-'))))

# def beautify_poem(poem_list):
#     poem = ''
#     for verse in poem_list:
#         poem += ' '.join(verse)
#         poem += '\n'
#     return poem

# i = 1
# for candidate_versification in versification('con cien cañones por banda viento en popa a toda vela no corta el mar sino vuela'):
#     print('versification ', i)
#     i += 1
#     print(beautify_poem(candidate_versification))
#     print('-' * 15)


# https://github.com/CPJKU/partitura



# my_xml_file = pt.EXAMPLE_MEI

# score = pt.load_score(my_xml_file)



# part = score.parts[0]

# pianoroll = np.array([(n.start.t, n.end.t, n.midi_pitch) for n in part.notes])

# print(part.pretty())

# beat_map = part.beat_map

# print(beat_map(pianoroll[:, 0]))
import partitura as pt
import numpy as np
from pyverse import Pyverse
import aima3.search
import copy
# from aima3.search import backtracking_search, NQueensProblem

# aima.csp.backtracking_search(syllables)

class State:
    def __init__(self, original):
        self.original = original
        self.verses = [[]]

class Syllables(aima3.search.Problem):
    def __init__(self, initial, goal=None):
        super().__init__(State(initial),goal)

    def actions(self, state):
        # print("actions: ", [x for x in range(len(state.verses)) if len(state.verses[x]) <= 8] + [len(state.verses)])
        return [x for x in range(len(state.verses)) if len(state.verses[x]) <= 8] + [len(state.verses)]
        
    def result(self, old_state, action):
        # Return the new state after applying the action

        state = copy.deepcopy(old_state)
        syllable = state.original[0]

        state.original = state.original[1:]
        # print("-----")
        # print(state.original)
        # print(syllable)
        # print(state.verses)
        # print(action)
        if action == len(state.verses):
            state.verses.append([syllable])
        else:
            state.verses[action].append(syllable)
        return state

    def goal_test(self, state):
        # Check if the state is the goal state
        return len(state.original) == 0

    def path_cost(self, c, state1, action, state2):
        # Define the path cost function
        return c + 1  # Example: Incremental cost of 1 per step

    def value(self, state):
        # Define a value function for optimization problems
        return 0

my_xml_file = pt.EXAMPLE_MEI
score = pt.load_score(my_xml_file)
part = score.parts[0]
poem = "en un lugar de la mancha de cuyo nombre"
syllables=Pyverse(poem).syllables.split('-')[1:]
problem=Syllables(syllables)
# solution_node = aima3.search.breadth_first_search(problem)
# if solution_node:
#     print("Solution path:", solution_node.solution())
#     print("Poem:", solution_node.state.verses)
#     print("Path cost:", solution_node.path_cost)
# else:
#     print("No solution found")
