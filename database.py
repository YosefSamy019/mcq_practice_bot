import json


class Question:
    def __init__(self, question, answers, right_answer_index):
        self.question = str(question)
        self.answers = answers
        self.right_answer_index = int(right_answer_index)


def load_questions():
    questions = []

    with open('questions.json', 'r') as f:
        questions_raw = json.load(f)

    for q_dict in questions_raw:
        questions.append(Question(
            q_dict['question'],
            q_dict['answers'],
            q_dict['right_answer_index']
        ))

    return questions
