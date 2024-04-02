"""The class containing UI components for our project.

This is primarily the Questionnaire that sequentially asks users questions for us
to recommend dog breeds for them.

Utilizes TKinter for UI elements, and OOP for questions and such.
"""
import tkinter as tk
from typing import Callable

import data_loader
import user_demographics
import user_preference
from userdata import User
from districts import District


class Question:
    """Abstract class that represents a question in a questionnaire

    Instance Attributes:
        - prompt: The string that represents the prompt of this question
    """
    prompt: str

    def __init__(self, prompt: str):
        self.prompt = prompt

    def create_widget(self, master: tk.Tk) -> tuple[tk.Widget, Callable[[], str]]:
        """Creates a widget for displaying in TK for this question.
        Returns a tuple that contains the widget object and a callable that can retrieve the
        value inputted into the widget.
        """
        raise NotImplementedError

    def can_update(self) -> bool:
        """Determines if the current user input for this question is valid.

        By default is always true, but for NumberQuestions might require it to be within a range.
        """
        return True


class DropDownQuestion(Question):
    """Represents a drop-down question with multiple options in this questionnaire.

    Instance Attributes:
        - options: List of strings that represent options for this question. The user must pick from these.
    """
    options: list[str]

    def __init__(self, prompt: str, options: list[str]):
        super().__init__(prompt)
        self.options = options

    def create_widget(self, master: tk.Tk) -> tuple[tk.Widget, Callable[[], str]]:
        self.variable = tk.StringVar(master)
        self.variable.set(self.options[0])  # default value, first option
        return tk.OptionMenu(master, self.variable, *self.options), self.variable.get


class NumberQuestion(Question):
    """Represents a number-input question for this questionnaire.

    Instance Attributes:
        - min_val: Minimum value for this number input
        - max_val: Maximum value for this number input
    """
    min_val: int
    max_val: int

    def __init__(self, prompt: str, min_val: int, max_val: int):
        super().__init__(prompt)
        self.min_val = min_val
        self.max_val = max_val

    def create_widget(self, master: tk.Tk) -> tuple[tk.Widget, Callable[[], str]]:
        self.entry = tk.Entry(master)
        return self.entry, self.entry.get

    def can_update(self) -> bool:
        return self.entry.get().isdigit() and self.min_val <= int(self.entry.get()) <= self.max_val


class Questionnaire:
    """Represents a questionnaire in which questions are sequentially asked from the user and
    they must input their answer.
    Questions are propogated using widgets generated from the Question objects.
    After completing all questions, executes the answer_callback that will process the answers.

    Instance Attributes:
        - master: The TK object to propogate
        - questions: List of questions to use
        - current_question_index: Current index of question that we are on
        - widgets: List of TK widgets that we will propogate the window with
        - answers: User inputted answers from widgets
        - answer_callback: Function to call when user has completed all questions
        - next_button: TK button for moving to next question
        - current_question: Current question and callable for current widget to get its value
    """
    master: tk.Tk
    questions: list[Question]
    current_question_index: int
    widgets: list[tk.Widget]
    answers: list[str]
    answer_callback: Callable[[list[str]], None]
    next_button: tk.Button
    current_question: tuple[tk.Widget, Callable[[], str]]

    def __init__(self, master: tk.Tk, questions: list[Question], answer_callback: Callable[[list[str]], None]):
        self.master = master
        self.master.title("Questionnaire")

        self.questions = questions
        self.current_question_index = 0
        self.widgets = []
        self.answers = []
        self.answer_callback = answer_callback

        self.setup_ui()

    def setup_ui(self):
        """Propogate the master TK with our initial question
        """
        self.next_button = tk.Button(self.master, text="Next", command=self.next_question)
        self.next_button.pack(side=tk.BOTTOM)

        self.update_question()

    def clear_widgets(self):
        """Clear all widgets from the TK UI
        """
        for widget in self.widgets:
            widget.destroy()
        self.widgets.clear()

    def update_question(self):
        """Update the question widgets in the TK UI to represent the current question we are on.
        """
        self.clear_widgets()
        if self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]

            # Create and pack the question prompt label
            prompt_label = tk.Label(self.master, text=question.prompt, font=("Arial", 14))
            prompt_label.pack(pady=(10, 5))
            self.widgets.append(prompt_label)

            # Create the question widget and get the method to retrieve its value
            widget, widget_val = question.create_widget(self.master)
            self.current_question_widget = (question, widget_val)
            widget.pack(pady=(5, 20))
            self.widgets.append(widget)

            # Bind the Enter key to the next_question method
            # This assumes all relevant widgets can receive focus.
            self.master.bind('<Return>', lambda event=None: self.next_question())
        else:
            self.display_results()

    def next_question(self):
        """Move to the next question in the TK UI
        """
        if self.current_question_widget[0].can_update():
            self.answers.append(self.current_question_widget[1]())
            self.current_question_index += 1
            self.update_question()

    def display_results(self):
        """Perform the final callable once finishing the questions.
        """
        self.clear_widgets()
        self.next_button.pack_forget()
        self.answer_callback(self.answers)


def create_preference_questions() -> list[Question]:
    """Creates a set of questions to ask about user preference.
    """
    return [
        NumberQuestion('Affectionate with faimly? (1-5)', 1, 5),
        NumberQuestion('Importance of good with young children? (1-5)', 1, 5),
        NumberQuestion('Importance of good with other dogs? (1-5)', 1, 5),
        NumberQuestion("Sheeding level (1 = I don't mind shedding) (5 = Shedding is a problem)", 1, 5),
        NumberQuestion('Open to strangers? (1-5)', 1, 5),
        NumberQuestion('High in Playfulness? (1-5)', 1, 5),
        NumberQuestion('High in Protective Nature? (1-5)', 1, 5),
        NumberQuestion('High in Adaptability? (1-5)', 1, 5),
        NumberQuestion('High in Trainability? (1-5)', 1, 5),
        NumberQuestion('High in Energy? (1-5)', 1, 5),
        DropDownQuestion('Is high amount of barking/energy considered a positive or negative trait?',
                         ['positive', 'negative']),
        NumberQuestion('How important is this barking/energy criterion? (1-5)', 1, 5),
        DropDownQuestion('Is needing lots of attention considered a positive or negative trait?',
                         ['positive', 'negative']),
        NumberQuestion('How important is this stimulation/attention criterion? (1-5)', 1, 5)
    ]


def create_demographic_questions(districts: set[District]) -> list[Question]:
    """Creates a set of questions to ask about user demographic.
    """
    return [
        NumberQuestion('What is your age?', 0, 100),
        DropDownQuestion('What is your gender?', ['Male', 'Female', 'Other']),
        DropDownQuestion('What is your district?', [district.district_name for district in districts])
    ]


if __name__ == "__main__":
    districts = data_loader.load_district_data('data/district_quarters_2017.csv')
    district_data_dict = data_loader.get_raw_district_distances(districts, 'data/district_closeness_2017.csv')
    data_loader.normalize_district_distances(district_data_dict)
    data_loader.apply_district_distances(district_data_dict)
    district_data = set(district_data_dict.keys())
    graph = data_loader.load_dog_data('data/zurich_dog_data_2017.csv', district_data)
    district_id_lookup = {district.district_id: district for district in district_data}
    district_name_lookup = {district.district_name: district for district in district_data}

    breeds = data_loader.dog_breed_data_loader('data/breed_traits.csv')

    recommendation_limit = 5

    demographic_questions = create_demographic_questions(district_data)
    preference_questions = create_preference_questions()

    questions = demographic_questions + preference_questions

    def process_answers(answers: list[str]):
        """Processes the answers that are inputted by the user.
        """
        demographic_answers = answers[:len(demographic_questions)]
        preference_answers = answers[len(demographic_questions):]

        demographic_recommendations: list[tuple[str, float]] = user_demographics.get_demographic_recommendations(
            User(
                -1,
                int(demographic_answers[0]),
                demographic_answers[1][:1].upper(),
                district_name_lookup[demographic_answers[2]]),
            recommendation_limit,
            graph,
        )

        preference_answers_to_potential_int: list[str | int] = [
            int(answer) if answer.isdigit() else answer for answer in preference_answers
        ]

        weighted_preferences = user_preference.weight_raw_preference_data(*preference_answers_to_potential_int)
        preference_recommendations: list[tuple[str, int]] = (
            user_preference.get_preference_recommendations(breeds, recommendation_limit, *weighted_preferences))

        print('Demographic Recommendations:')
        for demographic_recommendation in demographic_recommendations:
            print(f'    - {demographic_recommendation[0]}, score: {demographic_recommendation[1]}')

        print('\nPreference Recommendations:')
        for preference_recommendation in preference_recommendations:
            print(f'    - {preference_recommendation[0]}, score: {preference_recommendation[1]}')


    root = tk.Tk()
    root.geometry("800x600")
    app = Questionnaire(root, questions, process_answers)
    root.mainloop()
