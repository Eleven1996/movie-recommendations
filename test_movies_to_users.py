"""Unit test for recommender_functions.movies_to_users"""
import unittest

from recommender_functions import movies_to_users

class TestMoviesToUsers(unittest.TestCase):

    def test_movies_to_users(self):
        actual = movies_to_users({1: {10: 3.0}, 2: {10: 3.5}})
        expected = {10: [1, 2]}
        self.assertEqual(actual, expected)

    # Add tests below to create a complete set of tests without redundant tests
    # Redundant tests are tests that would only catch bugs that another test
    # would also catch.

if __name__ == '__main__':
    unittest.main(exit=False)
