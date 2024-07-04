import xmltodict
import numpy as np
from pyverse import Pyverse
import aima3.search
import copy

class State:
    def __init__(self, original):
        self.original = original
        self.verses = [[]]

class Syllables(aima3.search.Problem):
    def __init__(self, initial, goal=None):
        super().__init__(State(initial),goal)

    def actions(self, state):
        """TODO"""
        actions = []
        # print(state.verses)
        length_last_verse = len(state.verses[-1])
        if length_last_verse < 8: # add to current verse if it's small enough
            actions += [len(state.verses) - 1]
        if length_last_verse >= 8: # or try a new verse if it's big enough
            actions += [len(state.verses)]
        
        # print(actions)
        return actions
        
    def result(self, old_state, action):
        state = copy.deepcopy(old_state)
        syllable = state.original[0]

        state.original = state.original[1:]

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



def get_lyrics_from_mei(input_file):
    with open(input_file) as fd:
        score = xmltodict.parse(fd.read())

        measures=score['mei']['music']['body']['mdiv']['score']['section']['measure']

        text = ''

        for measure in measures:
            for staff in measure['staff']:
                try:
                    text += staff['layer']['note']['verse']['syl']
                except Exception:
                    pass #print('something bad')
        return text

def syllables_right(poem):
    syllables=Pyverse(poem).syllables.split('-')[1:]
    problem=Syllables(syllables)
    solution_node = aima3.search.breadth_first_search(problem)
    return solution_node.state.verses if solution_node else None

def main():
    poem=get_lyrics_from_mei("grace4.mei")
    poem="en un lugar de la mancha de cuyo nombre no quiero acordarme"
    verses=syllables_right(poem)
    if poem:
        print("Poem:", verses)
    else:
        print("No solution found!")
    
if __name__ == '__main__':
    main()
