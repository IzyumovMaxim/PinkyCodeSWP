import unittest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from metrics import get_density, get_comments, get_readability

class TestDensityAssessment(unittest.TestCase):
    def setUp(self):
        self.func = get_density
        with open(f"{os.path.dirname(os.path.abspath(__file__))}/codetest.txt") as file:
            self.code = file.read()

    def test_density(self):
        # Фактическое значение: 8%
        self.assertAlmostEqual(self.func(self.code), 8, places=1)


class TestCommentedPctAssessment(unittest.TestCase):
    def setUp(self):
        self.func = get_comments

        with open(f"{os.path.dirname(os.path.abspath(__file__))}/codetest2.txt") as file:
            self.code_existing_language = file.read()

        with open(f"{os.path.dirname(os.path.abspath(__file__))}/codetest3.txt") as file:
            self.code_not_existing_language = file.read()

    def test_commented_pct(self):
        # Фактическое значение: 30.76923076923077%
        self.assertAlmostEqual(self.func(self.code_existing_language), 30.76923076923077, places=1)

    def test_on_non_existing_language(self):
        self.assertEqual(self.func(self.code_not_existing_language), 0.0)


class TestReadabilityAssessment(unittest.TestCase):
    def setUp(self):
        self.func = get_readability
        self.code = '''#include <stdio.h>

int main() {
    printf(123)
    
    return 0
}'''

    def test_not_commented(self):
        '''Test if the result of assessment is 0.0 in case of entirely non-commented code'''
        self.assertEqual(self.func(self.code), 0.0)
