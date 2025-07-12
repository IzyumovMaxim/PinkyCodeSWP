import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from readability_grading_functions import count_syllables, analyze_text


class TestSyllablesCounting(unittest.TestCase):
    def setUp(self):
        self.func = count_syllables

    def test_syllables_counting(self):
        self.assertEqual(self.func("Tetrahedron"), 4)

    def test_non_existing_syllables_counting(self):
        self.assertEqual(self.func("jnvfvfjslnv"), 1)


class TestTextAnalysis(unittest.TestCase):
    def setUp(self):
        self.func = analyze_text

    def test_analysis(self):
        text = '''
        Python is a high-level, versatile programming language known for its readability and ease of use,
        making it popular for both beginners and experienced developers.
        It's widely used in web development, data science, machine learning, and scripting, among other applications. 
        '''

        expected_result = {
            'num_sentences': 2,
            'num_words': 48,
            'num_syllables': 72,
            'avg_word_length': 4.458333333333333,
            'avg_sentence_length': 24.0,
            'avg_syllables_per_word': 1.5,
            'percent_complex_words': 45.83333333333333
        }

        self.assertEqual(self.func(text.replace("\n", "")), expected_result)