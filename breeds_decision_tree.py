"""A decision Tree implementation of dogs based off of their
characteristics ranking from the American Kennel Club"""
from __future__ import annotations
from typing import Any, Optional
import csv
from dataclasses import dataclass
from python_ta.contracts import check_contracts


class Tree:
    """A decision tree class that gives results based on the
    user criterion"""
    root: Any
    subtrees: list[Tree]

    def __init__(self, root: Optional[Any], subtrees: list[Tree]) -> None:
        self._root = root
        self._subtrees = subtrees

    def insert_sequence(self, items: list) -> None:
        """Insert the sequence into this tree"""
        if not items:
            return
        exist = self.contain_num(items[0])
        if exist:
            exist.insert_sequence(items[1:])
        else:
            new_subtree = Tree(items[0], [])
            self._subtrees.append(new_subtree)
            new_subtree.insert_sequence(items[1:])

    def contain_num(self, item: Any) -> Tree | bool:
        """A helper function to check if the tree already has the first item in list"""
        for subtree in self._subtrees:
            if subtree._root == item:
                return subtree
        return False

    def decision_tree_method(self, choices: list[int]) -> list[str]:
        """
        return the list of dog breeds based off of the choices the user made.
        """
        current_tree = self
        for value in choices:
            if value in [subtree._root for subtree in current_tree._subtrees]:
                current_tree = [current_tree._subtrees[i] for i in range(len(current_tree._subtrees))
                                if current_tree._subtrees[i]._root == value][0]
            else:
                return []
        return [subtree._root for subtree in current_tree._subtrees]


def build_decision_tree(file: str) -> Tree:
    """Build a decision tree storing the animal data from the given file.

    Preconditions:
        - file is the path to a csv file in the format of the provided animals.csv
    """
    tree = Tree('', [])  # The start of a decision tree

    with open(file) as csv_file:
        reader = csv.reader(csv_file)
        next(reader)  # skip the header row

        for row in reader:
            # row is a list[str] containing the data in the file.
            # Your task is to process this list so that you can insert it into tree.
            # Note: if PyCharm gives you a warning about mixing bool and str types in a list,
            # you can safely ignore the warning.
            insert = []
            bool_values = row[1:]
            for value in bool_values:
                insert.append(value)
            insert.append(row[0])
            tree.insert_sequence(insert)
    return tree


def get_user_input(questions: list[str]) -> list[int]:
    """Return the user's answers to a list of Yes/No questions."""
    answers_so_far = []
    for question in questions:
        print(question)
        s = int(input('score from 1-5: '))
        answers_so_far.append(s)  # Any other input is interpreted as False
    return answers_so_far


QUESTIONS = [
    'affectionate_w_family',
    'good_w_young_children',
    'good_w_other_dog',
    'shedding_level',
    'openness_to_strangers',
    'playfulness',
    'protective_nature',
    'adaptability',
    'trainability',
    'energy',
    'barking',
    'stimulation_needs'
]


def run_dog_recommender(file: str) -> None:
    """runs the dog recommender"""
    decision_tree = build_decision_tree(file)
    user_input = get_user_input(QUESTIONS)
    result = decision_tree.decision_tree_method(user_input)
    if len(result) == 0:
        print("Sorry, we didn't find any dog breed matching your description.")
    else:
        for item in result:
            print(item)


if __name__ == '__main__':
    run_dog_recommender("data/breed_traits.csv")
