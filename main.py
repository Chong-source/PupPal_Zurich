"""The class containing UI components for our project.

This is primarily the Questionnaire that sequentially asks users questions for us
to recommend dog breeds for them.

Utilizes TKinter for UI elements, and OOP for questions and such.

Contains a lot more logic for displaying popups, post-processing data,
loading images, etc.
"""
import io
import math
import tkinter as tk
import urllib.request
from typing import Callable, Optional
from urllib.error import HTTPError
import ssl

from PIL import Image, ImageTk
from PIL.ImageTk import PhotoImage

import data_loader
import user_demographics
import user_preference
import zurich_map
from userdata import User
from districts import District


class Question:
    """Abstract class that represents a question in a questionnaire

    Instance Attributes:
        - prompt: The string that represents the prompt of this question
    """
    prompt: str

    def __init__(self, prompt: str) -> None:
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

    def on_display(self) -> None:
        """Runs on displaying the widgets for this question
        """
        pass


class DropDownQuestion(Question):
    """Represents a drop-down question with multiple options in this questionnaire.

    Instance Attributes:
        - options: List of strings that represent options for this question. The user must pick from these.
    """
    options: list[str]

    def __init__(self, prompt: str, options: list[str]) -> None:
        super().__init__(prompt)
        self.options = options

    def create_widget(self, master: tk.Tk) -> tuple[tk.Widget, Callable[[], str]]:
        variable = tk.StringVar(master)
        variable.set(self.options[0])  # default value, first option
        return tk.OptionMenu(master, variable, *self.options), variable.get


class NumberQuestion(Question):
    """Represents a number-input question for this questionnaire.

    Instance Attributes:
        - min_val: Minimum value for this number input
        - max_val: Maximum value for this number input
        - entry: TK box to input into
    """
    min_val: int
    max_val: int
    entry: tk.Entry

    def __init__(self, prompt: str, min_val: int, max_val: int) -> None:
        super().__init__(prompt)
        self.min_val = min_val
        self.max_val = max_val

    def create_widget(self, master: tk.Tk) -> tuple[tk.Widget, Callable[[], str]]:
        self.entry = tk.Entry(master)
        return self.entry, self.entry.get

    def can_update(self) -> bool:
        return self.entry.get().isdigit() and self.min_val <= int(self.entry.get()) <= self.max_val

    def on_display(self) -> None:
        try:
            self.entry.focus()
        except tk.TclError:
            pass  # Edge case where we focus something that is closing


class Questionnaire(tk.Tk):
    """Represents a questionnaire in which questions are sequentially asked from the user and
    they must input their answer.
    Questions are propogated using widgets generated from the Question objects.
    After completing all questions, executes the answer_callback that will process the answers.

    Instance Attributes:
        - questions: List of questions to use
        - current_question_index: Current index of question that we are on
        - widgets: List of TK widgets that we will propogate the window with
        - answers: User inputted answers from widgets
        - answer_callback: Function to call when user has completed all questions
        - next_button: TK button for moving to next question
        - current_question: Current question and callable for current widget to get its value
    """
    questions: list[Question]
    current_question_index: int
    widgets: list[tk.Widget]
    answers: list[str]
    answer_callback: Callable[[list[str]], None]
    next_button: tk.Button
    current_question: tuple[Question, Callable[[], str]]

    def __init__(self, questions: list[Question], answer_callback: Callable[[list[str]], None]) -> None:
        # Initialize TK superclas
        super().__init__()
        self.title("Questionnaire")
        self.geometry("800x600")

        # Initialize questionnaire
        self.questions = questions
        self.current_question_index = 0
        self.widgets = []
        self.answers = []
        self.answer_callback = answer_callback

        self.setup_ui()

    def start(self) -> None:
        """Starts the main TK window.

        THIS IS A BLOCKING FUNCTION.
        It must also be called on the same thread where TK was initialized!
        """
        self.mainloop()

    def setup_ui(self) -> None:
        """Propogate the master TK with our initial question
        """
        self.next_button = tk.Button(self, text="Next", command=self.next_question)
        self.next_button.pack(side=tk.BOTTOM)

        self.update_question()

    def clear_widgets(self) -> None:
        """Clear all widgets from the TK UI
        """
        for widget in self.widgets:
            widget.destroy()
        self.widgets.clear()

    def update_question(self) -> None:
        """Update the question widgets in the TK UI to represent the current question we are on.
        """
        self.clear_widgets()
        if self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]

            # Create and pack the question prompt label
            prompt_label = tk.Label(self, text=question.prompt, font=("Arial", 14))
            prompt_label.pack(pady=(10, 5))
            self.widgets.append(prompt_label)

            # Create the question widget and get the method to retrieve its value
            widget, widget_val = question.create_widget(self)
            self.current_question = (question, widget_val)
            widget.pack(pady=(5, 20))
            self.widgets.append(widget)

            # Bind the Enter key to the next_question method
            # This assumes all relevant widgets can receive focus.
            self.bind('<Return>', lambda _: self.next_question())
        else:
            self.display_results()

    def next_question(self) -> None:
        """Move to the next question in the TK UI
        """
        if self.current_question[0].can_update():
            self.answers.append(self.current_question[1]())
            self.current_question_index += 1
            self.update_question()
            self.current_question[0].on_display()

    def display_results(self) -> None:
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


def create_demographic_questions(all_districts: set[District]) -> list[Question]:
    """Creates a set of questions to ask about user demographic.
    """
    return [
        NumberQuestion('What is your age?', 0, 100),
        DropDownQuestion('What is your gender?', ['Male', 'Female', 'Other']),
        DropDownQuestion('What is your district?', sorted([district.district_name for district in all_districts]))
    ]


if __name__ == "__main__":
    # Load all our data from files
    districts = data_loader.load_district_data('data/district_quarters_2017.csv')
    district_data_dict = data_loader.get_raw_district_distances(districts, 'data/district_closeness_2017.csv')
    data_loader.normalize_district_distances(district_data_dict)
    data_loader.apply_district_distances(district_data_dict)
    district_data = set(district_data_dict.keys())
    graph, district_graph = data_loader.load_dog_data('data/zurich_dog_data_2017.csv', district_data)
    district_id_lookup = {district.district_id: district for district in district_data}
    district_name_lookup = {district.district_name: district for district in district_data}
    district_lat_lng = data_loader.load_district_lat_lng('data/district_lat_lng.csv', districts)

    breeds = data_loader.dog_breed_data_loader('data/breed_traits.csv')
    dog_translations = data_loader.load_translation_mapping('data/translated_dog_breed.csv')
    dog_images = data_loader.load_dog_images('data/dog_images.csv')

    # Create questions
    recommendation_limit = 5

    demographic_questions = create_demographic_questions(district_data)
    preference_questions = create_preference_questions()

    all_questions = demographic_questions + preference_questions

    def curve_data(target_diff_percent: float, data: list[tuple[str, float]]) -> list[tuple[str, float]]:
        """Curves the % matches that we have in our data so that they are spread out a little more.
        Makes for more interesting matches.

        target_diff_percent: a magic number that kind of determines how far apart the upper and lower %s are
        data: our data to curve
        Does not mutate data, returns new list
        """
        min_val = data[-1][1]
        max_val = data[0][1]
        diff = 1 - max_val
        power = math.log(1 - target_diff_percent, min_val)
        return [(entry[0], ((entry[1] + diff) ** power) - diff) for entry in data]

    def add_frame(parent: tk.Misc) -> tk.Frame:
        """Add and return an empty frame to our TKinter window.
        """
        input_frame = tk.Frame(parent, pady=5)
        input_frame.pack()
        return input_frame

    def add_label_to_frame(parent: tk.Frame, column: int, text: str, font_size: int = 14) -> None:
        """Add a label (plaintext) to a TK frame in the given column with the given label and font size
        """
        label = tk.Label(parent, text=text, font=("Arial", font_size))
        label.pack(padx=(5, 5), pady=(10, 5))
        label.grid(row=0, column=column)

    def add_button_to_frame(parent: tk.Frame, column: int, text: str,
                            command: Callable[[], None], font_size: int = 14) -> None:
        """Add a button to a TK frame in the given column with the given function callable, text label and font size
        """
        button = tk.Button(parent, text=text, command=command, font=("Arial", font_size))
        button.grid(row=0, column=column)

    def create_map_popup(dog_breed: str, limit: int) -> None:
        """Creates and displays a TKinterMapView window with the top districts in terms of number of
        a specific dog breed (in proportion to the total dog population).
        """
        top_districts = zurich_map.get_top_districts(dog_breed, districts, district_graph)[:limit]
        top_district_pins = set()
        index = 1
        for district in top_districts:
            lat, lng = district_lat_lng[district]
            top_district_pins.add((lat, lng, f'#{index}: {district.district_name}'))
            index += 1
        zurich_map.create_map_overlay(f'Top Zurich District Choices for {dog_breed}', top_district_pins)

    def get_image_from_url(url: str, target_image_y_pixel: int) -> PhotoImage:
        """WARNING: BLOCKING METHOD
        Retrieves an image from URL then loads it into an ImageTk
        """
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(url, context=ctx) as get:
            raw_data = get.read()
        image_raw = Image.open(io.BytesIO(raw_data))
        y_ratio = target_image_y_pixel / image_raw.size[1]
        new_x = round(image_raw.size[0] * y_ratio)
        resized = image_raw.resize((new_x, target_image_y_pixel))
        return ImageTk.PhotoImage(resized)

    def create_breed_info_popup(english_dog_breed: str) -> None:
        """Creates and displays a Tkinter window with an image of the dog breed and other relevant information.
        """
        popup = tk.Toplevel()
        popup.geometry("700x700")
        popup.title(f'{english_dog_breed} Information')
        popup.resizable(False, False)
        frame = add_frame(popup)
        tk.Label(popup, text=f'{english_dog_breed} Information', font=('Arial', 20)).pack(pady=(10, 5))
        if english_dog_breed in dog_images:
            try:
                image_url = dog_images[english_dog_breed]
                image: PhotoImage = get_image_from_url(image_url, 250)
                tk.Label(frame, image=image).pack(pady=(5, 10))
            except (HTTPError, tk.TclError):
                tk.Label(popup, text='Error finding image').pack(pady=(5, 10))
        else:
            tk.Label(popup, text='Error finding image').pack(pady=(5, 10))
        breed: Optional[data_loader.UserPreferenceDogBreed] = None
        for target in breeds:
            if target.breed_name == english_dog_breed:
                breed = target
                break
        if breed is None:
            tk.Label(popup,
                     text='Information about this breed is not available! (Working on it)',
                     font=('Arial', 14)
                     ).pack(pady=(5, 10))
        else:
            (tk.Label(popup,
                      text=f'Affectionate with Family: {breed.affectionate_w_family}', font=('Arial', 11))
             .pack(pady=(1, 1)))
            (tk.Label(popup,
                      text=f'Good with Young Children: {breed.good_w_young_children}', font=('Arial', 11))
             .pack(pady=(1, 1)))
            (tk.Label(popup,
                      text=f'Good with Other Dogs: {breed.good_w_other_dog}', font=('Arial', 11))
             .pack(pady=(1, 1)))
            (tk.Label(popup,
                      text=f'Shedding Level: {breed.shedding_level}', font=('Arial', 11))
             .pack(pady=(1, 1)))
            (tk.Label(popup,
                      text=f'Openness to Strangers: {breed.openness_to_strangers}', font=('Arial', 11))
             .pack(pady=(1, 1)))
            (tk.Label(popup,
                      text=f'Playfullness: {breed.playfulness}', font=('Arial', 11))
             .pack(pady=(1, 1)))
            (tk.Label(popup,
                      text=f'Protective Nature: {breed.protective_nature}', font=('Arial', 11))
             .pack(pady=(1, 1)))
            (tk.Label(popup,
                      text=f'Adaptability: {breed.adaptability}', font=('Arial', 11))
             .pack(pady=(1, 1)))
            (tk.Label(popup,
                      text=f'Trainability: {breed.trainability}', font=('Arial', 11))
             .pack(pady=(1, 1)))
            (tk.Label(popup,
                      text=f'Energy: {breed.energy}', font=('Arial', 11))
             .pack(pady=(1, 1)))
            (tk.Label(popup,
                      text=f'Barking: {breed.barking}', font=('Arial', 11))
             .pack(pady=(1, 1)))
            (tk.Label(popup,
                      text=f'Stimulation Needs: {breed.stimulation_needs}', font=('Arial', 11))
             .pack(pady=(1, 1)))
        popup.mainloop()

    def process_answers(answers: list[str]) -> None:
        """Processes the answers that are inputted by the user.
        """
        demographic_answers = answers[:len(demographic_questions)]
        preference_answers = answers[len(demographic_questions):]

        input_user = User(
            -1,
            int(demographic_answers[0]),
            demographic_answers[1][:1].upper(),
            district_name_lookup[demographic_answers[2]]
        )
        demographic_recommendations: list[tuple[str, float]] = user_demographics.get_demographic_recommendations(
            input_user,
            recommendation_limit,
            graph,
        )

        casted_preference_answers: list[str | int] = [
            int(answer) if answer.isdigit() else answer for answer in preference_answers
        ]

        weighted_preferences = user_preference.weight_raw_preference_data(*casted_preference_answers)
        preference_recommendations = (
            user_preference.get_preference_recommendations(breeds, recommendation_limit, *weighted_preferences))
        preference_recommendations = (
            user_preference.normalize_preference_recommendations(preference_recommendations))

        # Curve scores after normalizing
        demographic_recommendations = curve_data(0.5, demographic_recommendations)
        preference_recommendations = curve_data(0.15, preference_recommendations)

        def add_dog_breed_entry(english_dog_breed: str, german_dog_breed: Optional[str], percent_match: float) -> None:
            """Adds a dog breed entry to our TKinter window with the top districts and dog info buttons.
            """
            score_percent = int(round(percent_match * 10000) / 100)
            frame = add_frame(app)
            add_label_to_frame(frame, 0, f'{english_dog_breed}: {score_percent}% match', font_size=11)
            if german_dog_breed is not None:
                add_button_to_frame(frame, 1, 'See top districts',
                                    lambda: create_map_popup(german_dog_breed, 5),
                                    font_size=11)
            add_button_to_frame(frame, 2, 'Dog Breed Information',
                                lambda: create_breed_info_popup(english_dog_breed),
                                font_size=11)

        def add_large_label(message: str) -> None:
            """Adds a large padded text label to the tkinter window with given message
            """
            label = tk.Label(app, text=message, font=("Arial", 14))
            label.pack(pady=(10, 5))

        add_large_label('Dog Breed Recommendations Based on your Demographic:')
        for rec in demographic_recommendations:
            add_dog_breed_entry(dog_translations[rec[0]], rec[0], rec[1])
        add_large_label('Dog Breed Recommendations Based on your Preferences:')
        for rec in preference_recommendations:
            add_dog_breed_entry(rec[0], None, rec[1])

    app = Questionnaire(all_questions, process_answers)
    app.start()
