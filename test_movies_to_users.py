"""Unit test for recommender_functions.movies_to_users"""
import unittest

from recommender_functions import movies_to_users

class TestMoviesToUsers(unittest.TestCase):

    def test_movies_to_users(self):
        actual = movies_to_users({1: {10: 3.0}, 2: {10: 3.5}})
        expected = {10: [1, 2]}
        self.assertEqual(actual, expected)
        #test if tere are two movies
        user_ratings = {1:{11:3},2:{10:3.5}}
        expected = {10:[2],11:[1]}
        self.assertEqual(movies_to_users(user_ratings),expected)
        user_ratings = {
        1: {68735: 3.5, 302156: 4.0},
        2: {68735: 1.0, 124057: 1.5, 293660: 4.5},
        3: {68735:4.5, 302156:2.0, 124057:3.5},
        }
        actual = movies_to_users(user_ratings)
        user_set = set()
        movie_set = set()
        # test if all movies are included:
        for ratings in user_ratings.values():
            for movie in ratings.keys():
                movie_set.add(movie)
        self.assertEqual(len(actual),len(movie_set))

        for movie, user_list in actual.items():
            #test if the user list are sorted
            sort_list = sorted(user_list)
            self.assertEqual(sort_list,user_list)
            #test if all users are included:
            for user in user_list:
                user_set.add(user)
                self.assertTrue(movie in user_ratings[user])
            self.assertEqual(len(user_ratings),len(user_set))
            #test if all values are correct

    # Add tests below to create a complete set of tests without redundant tests
    # Redundant tests are tests that would only catch bugs that another test
    # would also catch.

if __name__ == '__main__':
    unittest.main(exit=False)
