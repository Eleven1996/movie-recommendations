"""CSC108 A3 recommender starter code."""

from typing import TextIO, List, Dict

from recommender_constants import (MovieDict, Rating, UserRatingDict,
                                   MovieUserDict)
from recommender_constants import (MOVIE_FILE_STR, RATING_FILE_STR,
                                   MOVIE_DICT_SMALL, USER_RATING_DICT_SMALL,
                                   MOVIE_USER_DICT_SMALL)


############## HELPER FUNCTIONS

def get_similarity(user1: Rating, user2: Rating) -> float:
    """Return the a similarity score between user1 and user2 based on their
    movie ratings. The returned similarity score is a number between 0 and 1
    inclusive. The higher the number, the more similar user1 and user2 are.

    For those who are curious, this type of similarity measure is called the
    "cosine similarity".

    >>> r1 = {1: 4.5, 2: 3.0, 3: 1.0}
    >>> r2 = {2: 4.5, 3: 3.5, 4: 1.5, 5: 5.0}
    >>> s1 = get_similarity(r1, r1)
    >>> abs(s1 - 1.0) < 0.0001 # s1 is close to 1.0
    True
    >>> s2 = get_similarity(r1, {6: 4.5})
    >>> abs(s2 - 0.0) < 0.0001 # s2 is close to 0.0
    True
    >>> round(get_similarity(r1, r2), 2)
    0.16
    """
    shared = 0.0
    for m_id in user1:
        if m_id in user2:
            shared += user1[m_id] * user2[m_id]
    norm1 = 0.0
    for m_id in user1:
        norm1 = norm1 + user1[m_id] ** 2
    norm2 = 0.0
    for m_id in user2:
        norm2 = norm2 + user2[m_id] ** 2
    return (shared * shared) / (norm1 * norm2)


############## STUDENT CONSTANTS

# suppose there are at most SAME+SCORE_LIMIT number of movies
# which has same score as the last movie in recommendation movies
# this is for better running time
SAME_SCORE_LIMIT = 10
CUT_OFF_RATING = 3.5

############## STUDENT HELPER FUNCTIONS

def get_candidate_movies(target_rating: Rating, sim_user_list: List[int],
                         user_ratings: UserRatingDict) -> List[int]:
    """
    Return candidate movies that similar users rated 3.5 or
    above that target user has not rated
    :param:target_rating: dictionary of movie_ids to rating of a
    target user for whom we would like to recommend movies to
    :param sim_user_list: the potential user list,who rated at least one
    same movie as the target user
    :param user_ratings: UserRartingDict dictionary
    :return: list of candidate movies
    >>> Target_rating = {293660: 4.5}
    >>> sim_user_list = [1,2]
    >>> candidate_movies = get_candidate_movies(Target_rating,sim_user_list,USER_RATING_DICT_SMALL)
    >>> candidate_movies
    [302156, 68735]
    >>> 293660 in candidate_movies
    False
    """
    candidate_movies = set()
    target_movies = list(target_rating.keys())
    # movies similar users rated 3.5 or above
    for user, ratings in user_ratings.items():
        if user in sim_user_list:
            potential_movies = list(ratings.keys())
            for movie in potential_movies:
                if not (movie in target_movies) and ratings[movie] >= CUT_OFF_RATING:
                    candidate_movies.add(movie)
    return list(candidate_movies)


def get_movie_score_dict(candidate_movies: List[int],
                         user_sim_dict: Dict[int, float],
                         user_ratings: UserRatingDict) -> Dict[int, float]:
    """
    return a dictionary with each movie with its corresponding score
    described in the handout
    :param candidate_movies:candidate movies
    :param user_sim_dict: similar user dict{user:sim_score}
    :param user_ratings: user ratings
    :return: return a dict
    """
    movie_score_dict = {}
    similar_users = list(user_sim_dict.keys())
    for movie in candidate_movies:
        movie_score = 0
        movie_popularity = get_movie_popularity(movie, user_ratings)
        candidate_users = get_candidate_users(movie, user_ratings, similar_users)
        for user in candidate_users:
            user_sim_score = user_sim_dict[user]
            num_user_movie = get_num_user_movie(user, candidate_movies, user_ratings)
            con_user_to_movie = user_sim_score / (num_user_movie * movie_popularity)
            movie_score = movie_score + con_user_to_movie
        movie_score_dict[movie] = movie_score
    return movie_score_dict


def get_candidate_users(movie_id: int, user_ratings: UserRatingDict,
                        similar_users: List[int])->List[int]:
    """
    return a candidate user list, who are similar user,
    and rated a particular movie 3.5 or above
    :param movie_id:movie id
    :param user_ratings: user rating
    :param similar_users:list of similar users
    :return:candidate user list
    >>> sim_users = [1,2]
    >>> get_candidate_users(68735,USER_RATING_DICT_SMALL,sim_users)
    [1]
    >>> get_candidate_users(124057,USER_RATING_DICT_SMALL,sim_users)
    []
    >>> get_candidate_users(000,USER_RATING_DICT_SMALL,sim_users)
    []
    """
    candidate_user_list = []
    for user in similar_users:
        if movie_id in user_ratings[user] and \
                user_ratings[user][movie_id] >= CUT_OFF_RATING:
            candidate_user_list.append(user)
    return candidate_user_list


def get_movie_popularity(movie_id: int, user_rating: UserRatingDict) -> int:
    """
    get total number of users who rated the movie
    (including any user in the UserRatingDict and any rating)
    :param movie_id: movie id
    :param user_rating:user rating dict
    :return:number of users rated the movie
    >>> get_movie_popularity(293660, USER_RATING_DICT_SMALL)
    1
    >>> get_movie_popularity(68735, USER_RATING_DICT_SMALL)
    2
    """
    movie_user_dict = movies_to_users(user_rating)
    return len(movie_user_dict[movie_id])


def get_num_user_movie(user_id: int, candidate_movies: List[int],
                       user_ratings: UserRatingDict) -> int:
    """
    return the number of candidate movies for particular user a rated 3.5 or above
    :param candidate_movies:list of candidate movies
    :param user_ratings:UserRatingDict
    :return:int, number of candidate movies
    >>> candidate_movies=[302156, 68735]
    >>> get_num_user_movie(1,candidate_movies,USER_RATING_DICT_SMALL)
    2
    >>> get_num_user_movie(2,candidate_movies,USER_RATING_DICT_SMALL)
    0
    """
    num = 0
    for movie, rating in user_ratings[user_id].items():
        if movie in candidate_movies and rating >= CUT_OFF_RATING:
            num = num + 1
    return num


def sort_moviescore_dict(movie_score_dict: Dict[int, float],
                         same_score_num_limit: int) -> List[int]:
    """
    sort movie score dict with value, when the value are the same,
    sort by movie_id,smaller id appear first
    :param movie_score_dict: dictionary {movie_id:score}
    :param same_score_num_limit:the length of returned list
    :return:list of sorted movies
    >>> movie_score_dict = {3333:3,2345:3,1111:4,2555:1,1133:1,3557:1.5}
    >>> sort_moviescore_dict(movie_score_dict,6)
    [1111, 2345, 3333, 3557, 1133, 2555]
    """
    # we have to sort the whole movie list for movie score,
    # but we don't need to sort the whole list for movie_id
    res_list = []
    sort_tuple = tuple(sorted(movie_score_dict.items(),
                              key=lambda x: x[1],
                              reverse=True))[:same_score_num_limit]
    current_value = sort_tuple[0][1]#defalt score,score for first movie
    current_list = []
    for moviescore in sort_tuple:
        if moviescore[1] == current_value:
            current_list.append(moviescore[0])
        else:#if the score are different, append the last list,update the list
            current_value = moviescore[1]
            current_list = sorted(current_list)
            for i in current_list:
                res_list.append(i)
            current_list = [moviescore[0]]
    current_list = sorted(current_list)
    for i in current_list:#for left overs in current list
        res_list.append(i)
    return res_list

############## STUDENT FUNCTIONS


def read_movies(movie_file: TextIO) -> MovieDict:
    """Return a dictionary containing movie id to (movie name, movie genres)
    in the movie_file.

    >>> movfile = open('movies_tiny.csv')
    >>> movies = read_movies(movfile)
    >>> movfile.close()
    >>> 68735 in movies
    True
    >>> movies[124057]
    ('Kids of the Round Table', [])
    >>> len(movies)
    4
    >>> movies == MOVIE_DICT_SMALL
    True
    """
    res_dict = {}
    movie_file.readline()  # skip header
    for line in movie_file:  # for the rest of the file
        info_list = line.rstrip("\n").split(",")
        res_dict[int(info_list[0])] = (info_list[1], info_list[4:])
    return res_dict


def read_ratings(rating_file: TextIO) -> UserRatingDict:
    """Return a dictionary containing user id to {movie id: ratings} for the
    collection of user movie ratings in rating_file.

    >>> rating_file = open('ratings_tiny.csv')
    >>> ratings = read_ratings(rating_file)
    >>> len(ratings)
    2
    >>> ratings[1]
    {2968: 1.0, 3671: 3.0}
    >>> ratings[2]
    {10: 4.0, 17: 5.0}
    >>> rating_file.close()
    """
    rating_dict = {}
    rating_file.readline()  # skip header
    for line in rating_file:
        info_list = line.split(",")
        user_id = int(info_list[0])
        movie_id = int(info_list[1])
        rating = float(info_list[2])
        if user_id in rating_dict:  # if key exist,add element directy
            rating_dict[user_id][movie_id] = rating
        else:  # if key does not exist, need to create nested dict first
            rating_dict[user_id] = {}
            rating_dict[user_id][movie_id] = rating
    return rating_dict


def remove_unknown_movies(user_ratings: UserRatingDict,
                          movies: MovieDict) -> None:
    """Modify the user_ratings dictionary so that only movie ids that are in the
    movies dictionary is remaining. Remove any users in user_ratings that have
    no movies rated.

    >>> small_ratings = {1001: {68735: 5.0, 302156: 3.5, 10: 4.5}, 1002: {11: 3.0}}
    >>> remove_unknown_movies(small_ratings, MOVIE_DICT_SMALL)
    >>> len(small_ratings)
    1
    >>> small_ratings[1001]
    {68735: 5.0, 302156: 3.5}
    >>> 1002 in small_ratings
    False
    """
    remove_movie_list = []
    remove_user_list = []
    for user, rating in user_ratings.items():
        for movie_ids in rating:
            if not (movie_ids in movies):
                remove_movie_list.append((user, movie_ids))
    for remove in remove_movie_list:
        del user_ratings[remove[0]][remove[1]]
    for user, rating in user_ratings.items():
        if rating == {}:
            remove_user_list.append(user)
    for remove in remove_user_list:
        del user_ratings[remove]


def movies_to_users(user_ratings: UserRatingDict) -> MovieUserDict:
    """Return a dictionary of movie ids to list of users who rated the movie,
    using information from the user_ratings dictionary of users to movie
    ratings dictionaries.

    >>> result = movies_to_users(USER_RATING_DICT_SMALL)
    >>> result == MOVIE_USER_DICT_SMALL
    True
    """
    movie_user_dict = {}
    for user, value in user_ratings.items():
        for movie_id in value:
            if movie_id in movie_user_dict:
                if movie_user_dict[movie_id] is None:
                    movie_user_dict[movie_id] = [user]
                else:
                    movie_user_dict[movie_id].append(user)
            else:
                movie_user_dict[movie_id] = [user]
    return movie_user_dict


def get_users_who_watched(movie_ids: List[int],
                          movie_users: MovieUserDict) -> List[int]:
    """Return the list of user ids in moive_users who watched at least one
    movie in moive_ids.

    >>> get_users_who_watched([293660], MOVIE_USER_DICT_SMALL)
    [2]
    >>> lst = get_users_who_watched([68735, 302156], MOVIE_USER_DICT_SMALL)
    >>> len(lst)
    2
    >>> lst
    [1, 2]
    """
    result_list = set()
    for movie_id, users in movie_users.items():
        if movie_id in movie_ids:
            for user in users:
                result_list.add(user)
    return list(result_list)


def get_similar_users(target_rating: Rating,
                      user_ratings: UserRatingDict,
                      movie_users: MovieUserDict) -> Dict[int, float]:
    """Return a dictionary of similar user ids to similarity scores between the
    similar user's movie rating in user_ratings dictionary and the
    target_rating. Only return similarites for similar users who has at least
    one rating in movie_users dictionary that appears in target_Ratings.
    example return dict:{u1:simscore1,u2:simscore2},higher the score,more sim

    >>> sim = get_similar_users({293660: 4.5}, USER_RATING_DICT_SMALL, MOVIE_USER_DICT_SMALL)
    >>> len(sim)
    1
    >>> round(sim[2], 2)
    0.86
    """
    movie_ids = list(target_rating.keys())  # [293660,337540]
    user_sim_dict = {}
    filter_user_ids = get_users_who_watched(movie_ids, movie_users)  # [1,2,3]
    for user in filter_user_ids:
        user_movie_rating = user_ratings[user]
        sim_socre = get_similarity(target_rating, user_movie_rating)
        user_sim_dict[user] = sim_socre
    return user_sim_dict


def recommend_movies(target_rating: Rating,
                     user_ratings: UserRatingDict,
                     movie_users: MovieUserDict,
                     num_movies: int) -> List[int]:
    """Return a list of num_movies movie id recommendations for a target user 
    with target_rating of previous movies. The recommendations are based on
    movies and "similar users" data from the user_ratings / movie_users 
    dictionaries.

    >>> recommend_movies({302156: 4.5}, USER_RATING_DICT_SMALL, MOVIE_USER_DICT_SMALL, 2)
    [68735]
    >>> recommend_movies({68735: 4.5}, USER_RATING_DICT_SMALL, MOVIE_USER_DICT_SMALL, 2)
    [302156, 293660]
    """
    user_sim_dict = get_similar_users(target_rating, user_ratings, movie_users)
    # who rated at least one movies the target rated
    similar_users = list(user_sim_dict.keys())
    # candidate_movies: movies similar users rated 3.5 or above and user has not rated
    candidate_movies = get_candidate_movies(target_rating, similar_users, user_ratings)
    # assign score to each movie
    movie_score_dict = get_movie_score_dict\
        (candidate_movies, user_sim_dict, user_ratings)  # {[movie:score]}
    length_limit = num_movies + SAME_SCORE_LIMIT
    final_movie_list = sort_moviescore_dict(movie_score_dict, length_limit)
    return final_movie_list[:num_movies]


if __name__ == '__main__':
    """Uncomment to run doctest"""
    import doctest

    doctest.testmod()
