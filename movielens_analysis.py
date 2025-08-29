#!/usr/bin/env pytest

from collections import defaultdict, Counter
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import pytest
import os


class Movies:
    """
    Analyzing data from movies.csv
    """

    def __init__(self, path_to_the_file):
        """
        Put here any fields that you think you will need.
        """
        self.movies = []
        try:
            with open(path_to_the_file, 'r', encoding='utf-8') as file:
                headers = file.readline().strip().split(',')
                if headers != ['movieId', 'title', 'genres']:
                    raise ValueError("Invalid file structure")
                for line in file:
                    row = line.strip().split(',')
                    if len(row) > 3:
                        title = ','.join(row[1:-1])
                        row = [row[0], title, row[-1]]
                    movie = dict(zip(headers, row))
                    self.movies.append(movie)
        except Exception as e:
            print(f"Exception: {e}")

    def dist_by_release(self):
        """
        The method returns a dict or an OrderedDict where the keys are years and the values are counts. 
        You need to extract years from the titles. Sort it by counts descendingly.
        """
        release_years = defaultdict(int)
        for movie in self.movies:
            title = movie['title']
            match = re.search(r'\((\d{4})\)', title)
            if match:
                year = int(match.group(1))
                release_years[year] += 1
        release_years = dict(sorted(release_years.items(), key=lambda x: -x[1]))
        return release_years

    def dist_by_genres(self):
        """
        The method returns a dict where the keys are genres and the values are counts.
        Sort it by counts descendingly.
        """
        genres = defaultdict(int)
        for movie in self.movies:
            all_genres = movie['genres'].split('|')
            if all_genres and all_genres[0] != '(no genres listed)':
                for genre in all_genres:
                    genres[genre] += 1
        genres = dict(sorted(genres.items(), key=lambda x: -x[1]))
        return genres

    def most_genres(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and 
        the values are the number of genres of the movie. Sort it by numbers descendingly.
        """
        movies_genres = [(movie['title'], len(movie['genres'].split('|'))) for movie in self.movies if
                         movie['genres'] != '(no genres listed)']
        movies_genres = sorted(movies_genres, key=lambda x: -x[1])
        return dict(movies_genres[:n])

    def get_movies_by_year(self, year):
        """
        BONUS PART
        The method returns a list of movies made in the given year. They are sorted in alphabetic.
        """
        year_movies=set()
        for movie in self.movies:
            match = re.search(r'\((\d{4})\)', movie['title'])
            if match:
                movie_year = int(match.group(1))
                if movie_year == year:
                    year_movies.add(movie['title'])
        return sorted(year_movies)


class Tags:
    """
    Analyzing data from tags.csv
    """

    def __init__(self, path_to_the_file):
        """
        Put here any fields that you think you will need.
        """
        self.tags = []
        try:
            with open(path_to_the_file, 'r') as file:
                headers = file.readline().strip().split(',')
                if headers != ['userId', 'movieId', 'tag', 'timestamp']:
                    raise ValueError("Invalid file structure")
                for line_num, line in enumerate(file, 1):
                    if line_num > 1000:
                        break
                    row = line.strip().split(',')
                    if len(row) != 4:
                        raise ValueError("Invalid representation of tag")
                    self.tags.append(dict(zip(headers, row)))
        except Exception as e:
            print(f"Exception: {e}")

    def most_words(self, n):
        """
        The method returns top-n tags with most words inside. It is a dict
        where the keys are tags and the values are the number of words inside the tag.
        Drop the duplicates. Sort it by numbers descendingly.
        """
        big_tags = set([(tag['tag'], len(tag['tag'].split())) for tag in self.tags])
        big_tags = sorted(big_tags, key=lambda x: -x[1])
        return dict(big_tags[:n])

    def longest(self, n):
        """
        The method returns top-n longest tags in terms of the number of characters.
        It is a list of the tags. Drop the duplicates. Sort it by numbers descendingly.
        """
        big_tags = set([(tag['tag'], len(tag['tag'])) for tag in self.tags])
        big_tags = sorted(big_tags, key=lambda x: -x[1])
        return dict(big_tags[:n])

    def most_words_and_longest(self, n):
        """
        The method returns the intersection between top-n tags with most words inside and 
        top-n longest tags in terms of the number of characters.
        Drop the duplicates. It is a list of the tags.
        """
        unique_tags = [tag['tag'] for tag in self.tags]
        most_words_tags = set(sorted(unique_tags, key=lambda tag: -len(tag.split()))[:n])
        longest_tags = set(sorted(unique_tags, key=lambda tag: -len(tag))[:n])
        big_tags = most_words_tags & longest_tags
        return list(sorted(big_tags))

    def most_popular(self, n):
        """
        The method returns the most popular tags. 
        It is a dict where the keys are tags and the values are the counts.
        Drop the duplicates. Sort it by counts descendingly.
        """
        all_tags=[tag['tag'] for tag in self.tags]
        popular_tags=Counter(all_tags).most_common(n)
        return dict(popular_tags)

    def tags_with(self, word):
        """
        The method returns all unique tags that include the word given as the argument.
        Drop the duplicates. It is a list of the tags. Sort it by tag names alphabetically.
        """
        tags_with_word={tag['tag'] for tag in self.tags if word in tag['tag']}
        return sorted(tags_with_word)
    def movie_by_tag(self, given_tag):
        """
        BONUS PART
        The method returns list if movieID that include the given_tag as the argument.
        It is sorted alphabetically.
        """
        movies={tag['movieId'] for tag in self.tags if given_tag in tag['tag']}
        return sorted(movies)


class Ratings:
    """
    Analyzing data from ratings.csv
    """
    def __init__(self, path_to_the_file="./datasets/ratings.csv", path_to_movies_file="../datasets/movies.csv"):
        try:
            self.data_ratings = []
            self.data_joined = []
            movieid_to_title = {}
            try:
                with open(path_to_movies_file, 'r', encoding='utf-8') as movies_file:
                    movies_file.readline()  
                    for line in movies_file:
                        values = line.strip().split(',')
                        if len(values) < 3:
                            continue
                        movie_id = int(values[0])
                        title = ','.join(values[1:-1]).strip('"')
                        movieid_to_title[movie_id] = title
            except FileNotFoundError:
                print(f"File not found: {path_to_movies_file}")
            except Exception as e:
                print(f"Exception while reading movies.csv: {e}")
            with open(path_to_the_file, 'r', encoding='utf-8') as ratings:
                headers = ratings.readline().strip().split(',')
                for i, line in enumerate(ratings):
                    if i >= 1000:
                        break
                    values = line.strip().split(',')
                    if len(values) != 4:
                        raise ValueError(f"Incorrect format in line {i+2}: {line}")
                    movie_id = int(values[1])
                    title = movieid_to_title.get(movie_id, None)
                    row = {
                        'userId': int(values[0]),
                        'movieId': movie_id,
                        'title': title,
                        'rating': float(values[2]),
                        'timestamp': int(values[3])
                    }
                    self.data_ratings.append(row)
                    self.data_joined.append(row)
        except FileNotFoundError:
            print(f"File not found: {path_to_the_file}")
            self.data_ratings = []
            self.data_joined = []
        except ValueError as ve:
            print(f"ValueError: {ve}")
            self.data_ratings = []
            self.data_joined = []
        except Exception as e:
            print(f"Exception: {e}")
            self.data_ratings = []
            self.data_joined = []

    class Movies:
        def __init__(self, parent):
            self.parent = parent  
        def dist_by_year(self):
            """
            The method returns a dict where the keys are years and the values are counts. 
            Sort it by years ascendingly. You need to extract years from timestamps.
            """
            try:
                ratings_by_year = {}
                for data in self.parent.data_joined: 
                    year = datetime.fromtimestamp(data['timestamp']).year
                    ratings_by_year[year] = ratings_by_year.get(year, 0) + 1
                ratings_by_year = dict(sorted(ratings_by_year.items()))
                return ratings_by_year
            except Exception as e:
                print(f"Exception in dist_by_year: {e}")
                return  {}
        def dist_by_rating(self):
            """
            The method returns a dict where the keys are ratings and the values are counts.
         Sort it by ratings ascendingly.
            """
            try:
                ratings_by_amount = {}
                for data in self.parent.data_joined: 
                    rating = data['rating']
                    ratings_by_amount[rating] = ratings_by_amount.get(rating, 0) + 1
                ratings_by_amount = dict(sorted(ratings_by_amount.items()))
                return ratings_by_amount
            except Exception as e:
                print(f"Exception in dist_by_rating: {e}")
                return {}
        def top_by_num_of_ratings(self, n):
            """
            The method returns top-n movies by the number of ratings. 
            It is a dict where the keys are movie titles and the values are numbers.
     Sort it by numbers descendingly.
            """
            try:
                movie_counts = {}
                for data in self.parent.data_joined:
                    title = data['title'] or f"Unknown {data['movieId']}"
                    movie_counts[title] = movie_counts.get(title, 0) + 1
                total_movies = len(movie_counts)
                if not (1 <= n <= total_movies):
                    raise ValueError(f"n must be between 1 and {total_movies}, got {n}")
                sorted_movies = sorted(movie_counts.items(), key=lambda x: x[1], reverse=True)
                top_by_num_of_ratings = dict(sorted_movies[:n])
                return top_by_num_of_ratings
            except ValueError as ve:
                print(f"ValueError in top_by_num_of_ratings: {ve}")
                return {}
            except Exception as e:
                print(f"Exception in top_by_num_of_ratings: {e}")
                return {}
        @staticmethod
        def median(lst):
            n = len(lst)
            if n == 0:
                return None
            s = sorted(lst)
            mid = n // 2
            if n % 2 == 1:
                return s[mid]
            else:
                return (s[mid - 1] + s[mid]) / 2
        def top_by_ratings(self, n, metric='average'):
            """
            The method returns top-n movies by the average or median of the ratings.
            It is a dict where the keys are movie titles and the values are metric values.
            Sort it by metric descendingly.
            The values should be rounded to 2 decimals.
            """
            try:
                ratings_by_movie = {}
                for data in self.parent.data_joined:
                    title = data['title'] or f"Unknown {data['movieId']}"
                    rating = data['rating']
                    if title not in ratings_by_movie:
                        ratings_by_movie[title] = []
                    ratings_by_movie[title].append(rating)
                total_movies = len(ratings_by_movie)
                if not (1 <= n <= total_movies):
                    raise ValueError(f"n must be between 1 and {total_movies}, got {n}")
                if metric not in ('average', 'median'):
                    raise ValueError("metric must be 'average' or 'median'")
                movie_metric = {}
                for title, ratings in ratings_by_movie.items():
                    if metric == 'average':
                        value = round(sum(ratings) / len(ratings), 2)
                    elif metric == 'median':
                        value = round(self.median(ratings), 2)
                    movie_metric[title] = value
                sorted_movies = sorted(movie_metric.items(), key=lambda x: x[1], reverse=True)
                top_by_ratings = dict(sorted_movies[:n])
                return top_by_ratings
            except ValueError as ve:
                print(f"ValueError in top_by_ratings: {ve}")
                return {}
            except Exception as e:
                print(f"Exception in top_by_ratings: {e}")
                return {}
        def top_controversial(self, n):
            """
            The method returns top-n movies by the variance of the ratings.
            It is a dict where the keys are movie titles and the values are the variances.
          Sort it by variance descendingly.
            The values should be rounded to 2 decimals.
            """
            try:
                ratings_by_movie = {}
                for data in self.parent.data_joined:
                    title = data['title'] or f"Unknown {data['movieId']}"
                    rating = data['rating']
                    if title not in ratings_by_movie:
                        ratings_by_movie[title] = []
                    ratings_by_movie[title].append(rating)
                total_movies = len(ratings_by_movie)
                if not (1 <= n <= total_movies):
                    raise ValueError(f"n must be between 1 and {total_movies}, got {n}")
                movie_variance = {}
                for title, ratings in ratings_by_movie.items():
                    mean = sum(ratings) / len(ratings)
                    variance = sum((r - mean) ** 2 for r in ratings) / len(ratings)
                    movie_variance[title] = round(variance, 2)
                sorted_movies = sorted(movie_variance.items(), key=lambda x: x[1], reverse=True)
                top_controversial = dict(sorted_movies[:n])
                return top_controversial
            except Exception as e:
                print(f"Exception in top_controversial: {e}")
                return {}

        def most_active_user_by_coverage(self):
            """
            extra - Returns (userId, percent) — пользователя, который оценил наибольший процент фильмов из выборки,
            и этот процент (0-100, округлён до 2 знаков).
            """
            try:
                all_movies = set(data['movieId'] for data in self.parent.data_joined) 
                user_movies = {}
                for data in self.parent.data_joined: 
                    user = data['userId']
                    movie = data['movieId']
                    if user not in user_movies:
                        user_movies[user] = set()
                    user_movies[user].add(movie)
                max_user = None
                max_percent = 0
                total_movies = len(all_movies)
                for user, movies in user_movies.items():
                    percent = (len(movies) / total_movies * 100) if total_movies else 0
                    if percent > max_percent:
                        max_percent = percent
                        max_user = user
                return (max_user, round(max_percent, 2))
            except Exception as e:
                print(f"Exception in most_active_user_by_coverage: {e}")
                return (None, 0)

        def percent_of_max_ratings_per_movie(self, n=None):
            """
            Returns a dict {title: percent}, где percent — процент оценок 5.0 от всех оценок этого фильма (0-100, округлён до 2 знаков).
            Если n задан, возвращает только топ-n фильмов по проценту оценок 5.0.
            """
            try:
                movie_counts = {}
                movie_max_counts = {}
                for data in self.parent.data_joined:
                    title = data['title'] or f"Unknown {data['movieId']}"
                    rating = data['rating']
                    movie_counts[title] = movie_counts.get(title, 0) + 1
                    if rating == 5.0:
                        movie_max_counts[title] = movie_max_counts.get(title, 0) + 1
                percent_dict = {}
                for title in movie_counts:
                    percent = (movie_max_counts.get(title, 0) / movie_counts[title] * 100) if movie_counts[title] else 0
                    percent_dict[title] = round(percent, 2)
                sorted_percent_dict = dict(sorted(percent_dict.items(), key=lambda x: x[1], reverse=True))
                if n is not None:
                    total_movies = len(sorted_percent_dict)
                    if not (1 <= n <= total_movies):
                        raise ValueError(f"n must be between 1 and {total_movies}, got {n}")
                    items = list(sorted_percent_dict.items())[:n]
                    return dict(items)
                return sorted_percent_dict
            except Exception as e:
                print(f"Exception in percent_of_max_ratings_per_movie: {e}")
                return {}

    class Users(Movies):
        def __init__(self, parent):
            super().__init__(parent)
        def users_distribution(self):
            try:
                users_distribution = {}
                for data in self.parent.data_joined: 
                    user_id = data['userId']
                    users_distribution[user_id] = users_distribution.get(user_id, 0) + 1
                return users_distribution
            except Exception as e:
                print(f"Exception in users_distribution: {e}")
                return {}
        def users_rating_distribution(self, metric='average'):
            try:
                users_rating_distribution = {}
                for data in self.parent.data_joined: 
                    userid = data['userId']
                    rating = data['rating']
                    if userid not in users_rating_distribution:
                        users_rating_distribution[userid] = []
                    users_rating_distribution[userid].append(rating)
                if metric not in ('average', 'median'):
                    raise ValueError("metric must be 'average' or 'median'")
                av_rating = {}
                for userid, ratings in users_rating_distribution.items():
                    if metric == 'average':
                        value = round(sum(ratings) / len(ratings), 2)
                    elif metric == 'median':
                        value = round(self.median(ratings), 2)
                    av_rating[userid] = value
                return av_rating
            except Exception as e:
                print(f"Exception in users_rating_distribution: {e}")
                return {}
        def top_n_users_by_variance(self, n):
            try:
                users_ratings = {}
                for data in self.parent.data_joined: 
                    userid = data['userId']
                    rating = data['rating']
                    if userid not in users_ratings:
                        users_ratings[userid] = []
                    users_ratings[userid].append(rating)
                total_users = len(users_ratings)
                if not (1 <= n <= total_users):
                    raise ValueError(f"n must be between 1 and {total_users}, got {n}")
                user_variance = {}
                for userid, ratings in users_ratings.items():
                    mean = sum(ratings) / len(ratings)
                    variance = sum((r - mean) ** 2 for r in ratings) / len(ratings)
                    user_variance[userid] = round(variance, 2)
                sorted_users = sorted(user_variance.items(), key=lambda x: x[1], reverse=True)
                top_n = dict(sorted_users[:n])
                return top_n
            except Exception as e:
                print(f"Exception in top_n_users_by_variance: {e}")
                return {}


class Links:
    """
    Analyzing data from links.csv
    """
    def __init__(self, path_to_the_file:str, lenght:int = 1000):
        self.__movie_to_imdb = {}
        self.__fields = ["Director", "Budget", "Cumulative Worldwide Gross", "Runtime", "Title", "Rating"]
        self.__parsed_data = {}
        self.__session = requests.Session()
        self.__session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br'
        })
        with open(path_to_the_file, 'r') as file:
            headers = file.readline().strip().split(',')
            if headers != ['movieId', 'imdbId', 'tmdbId']:
                raise ValueError("Invalid file structure, expected headers: ['movieId', 'imdbId', 'tmdbId']")
            i = 0
            while i < lenght:
                i+=1
                parts = file.readline().strip().split(',')
                if len(parts) != 3 or parts[0] == '' or parts[1] == '' or parts[2] == '':
                    raise ValueError("Invalid file structure, expected 3 non-empty columns per row")
                movie_id, imdb_id, _ = parts
                self.__movie_to_imdb[int(movie_id)] = imdb_id
                
    def get_ids_dict(self):
        return self.__movie_to_imdb
    
    def get_imdb(self, list_of_movies:list, list_of_fields:list):
        """
        The method returns a list of lists [movieId, field1, field2, field3, ...] for the list of movies given as the argument (movieId).
        For example, [movieId, Director, Budget, Cumulative Worldwide Gross, Runtime].
        The values should be parsed from the IMDB webpages of the movies.
        Sort it by movieId descendingly.
        """
        imdb_info = []
        if len(self.__parsed_data) == 0:
            self.__load_and_parse_all_data()
        for movie_id in list_of_movies:
            if movie_id in self.get_ids_dict().keys():
                movie_data = [movie_id]
                for field in list_of_fields:
                    movie_data.append(self.__parsed_data.get(movie_id, {}).get(field))
                imdb_info.append(movie_data)
            
        imdb_info.sort(key=lambda x: x[0], reverse=True)
        return imdb_info
 

    def __load_and_parse_all_data(self):
        if len(self.__parsed_data) == 0:
            bad_ids = []
            for movie_id, imdb_id in self.__movie_to_imdb.items():
                try:
                    response = self.__session.get(f"https://www.imdb.com/title/tt{imdb_id}/")
                    if response.status_code >= 300:
                        bad_ids.append(movie_id)
                        continue
                    soup = BeautifulSoup(response.content, 'html.parser')
                    movie_data = {field: self.__extract_data(soup, field) for field in self.__fields}
                    self.__parsed_data[movie_id] = movie_data
                except requests.RequestException as e:
                    raise requests.RequestException(f"Error fetching data for movie ID {movie_id}: {e}")
            if len(bad_ids) > 0:
                for id in bad_ids:
                    self.__movie_to_imdb.pop(id)

    def __extract_data(self, soup, field:str):
        extractors = {
            "Director": {
                'selector': 'a',
                'attrs': {'href': re.compile(r'/name/nm\d+/')}
            },
            "Budget": {
                'search_text': 'Budget'
            },
            "Cumulative Worldwide Gross": {
                'search_text': 'Gross worldwide'
            },
            "Runtime": {
                'search_text': 'Runtime'
            },
            "Title": {
                'selectors': [
                    {'selector': 'h1', 'attrs': {}}
                ]
            },
            "Rating": {
                'search_text': 'IMDb RATING'
            }
        }
        
        currency_rates = { 
            '$': 1.0,      
            'U': 1.0,
            '¥': 0.0067,   
            '€': 1.09,     
            'E': 1.09,
            'C': 0.7276,   
            '£': 1.26,     
            '₹': 0.012,    
            'R': 0.18,     
            '₽': 0.011,    
            'R': 0.011   
        }

        config = extractors.get(field, {})
        if 'search_text' in config:
            element = soup.find(string=config['search_text'])
            if element:
                value = element.find_next().text.strip()
                if field == "Runtime":
                    return self.__parse_runtime(value)
                elif field == 'Budget':
                    return float(re.sub(r'[^\d.]', '', value)) * currency_rates[value[0]] if value[0] in currency_rates.keys() else None
                elif field == 'Cumulative Worldwide Gross':
                    return float(re.sub(r'[^\d.]', '', value)) if value else None
                return value[:6]
        elif 'selectors' in config:
            for selector in config['selectors']:
                element = soup.find(selector['selector'], selector['attrs'])
                if element:
                    return element.get_text(strip=True)
        elif 'selector' in config:
            element = soup.find(config['selector'], config['attrs'])
            if element:
                return element.get_text(strip=True)
        return None

    def __parse_runtime(self, runtime_str:str):
        parts = runtime_str.split()
        if len(parts) == 4:
            return int(parts[0]) * 60 + int(parts[2])
        elif len(parts) == 2 and 'hour' in parts[1].lower():
            return int(parts[0]) * 60
        else:
            return int(parts[0])

    def top_directors(self, n:int):
        """
        The method returns a dict with top-n directors where the keys are directors and 
        the values are numbers of movies created by them. Sort it by numbers descendingly.
        """
        directors = defaultdict(int)
        movies = self.get_imdb([key for key, _ in self.get_ids_dict().items()], ['Director'])
        
        for movie in movies:
            director = movie[1]

            if director:
                directors[director] += 1
                
        return dict(sorted(directors.items(), key=lambda x: x[1], reverse=True)[:n])

    def most_expensive(self, n:int):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
        the values are their budgets. Sort it by budgets descendingly.
        """
        movies = {}
        data = self.get_imdb([key for key, _ in self.get_ids_dict().items()], ['Title', 'Budget'])
        for movie in data:
            title = movie[1]
            budget = movie[2]

            if title and budget:
                movies[title] = budget

        return dict(sorted(movies.items(), key=lambda x: x[1], reverse=True)[:n])

    def most_profitable(self, n:int):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
        the values are the difference between cumulative worldwide gross and budget.
        Sort it by the difference descendingly.
        """
        profits = {}
        data = self.get_imdb([key for key, _ in self.get_ids_dict().items()], ['Title', 'Budget', 'Cumulative Worldwide Gross'])
        for movie in data:
            title = movie[1]
            budget = movie[2]
            gross = movie[3]
            
            if title and budget and gross:
                profits[title] = gross - budget

        return dict(sorted(profits.items(), key=lambda x: x[1], reverse=True)[:n])

    def longest(self, n:int):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
        the values are their runtime. If there are more than one version – choose any.
        Sort it by runtime descendingly.
        """
        runtimes = {}
        data = self.get_imdb([key for key, _ in self.get_ids_dict().items()], ['Title', 'Runtime'])
        
        for movie in data:
            title = movie[1]
            runtime = movie[2]
            
            if title and runtime:
                runtimes[title] = runtime
                    
        return dict(sorted(runtimes.items(), key=lambda x: x[1], reverse=True)[:n])

    def top_cost_per_minute(self, n:int):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
        the values are the budgets divided by their runtime. The budgets can be in different currencies – do not pay attention to it. #YET I PAID
        The values should be rounded to 2 decimals. Sort it by the division descendingly.
        """
        costs = {}
        data = self.get_imdb([key for key, _ in self.get_ids_dict().items()], ['Title', 'Budget', 'Runtime'])
        
        for movie in data:
            title = movie[1]
            budget = movie[2]
            runtime = movie[3]
            if title and budget and runtime and runtime > 0 and budget > 0:
                cost_per_minute = round(budget / runtime, 2)
                costs[title] = cost_per_minute
        return dict(sorted(costs.items(), key=lambda x: x[1], reverse=True)[:n])
    
    def get_imdb_rating(self, list_of_movie_ids:list): #bonus part
        """"
        Huntin bonus exp I invented this method, which returns dict with imdb ratings for given movie_ids where the keys are movie_ids and
        the values are the ratings
        Dict sorted by movie_id asc
        """
        return {movie_id: rating for movie_id, rating in reversed(self.get_imdb(list_of_movie_ids, ['Rating']))}


MOVIE_CSV_FILE = '../datasets/movies.csv'


class Tests:
    """Unified test class for all MovieLens analysis classes"""
    
    @classmethod
    def setup_class(cls):
        cls.movies = Movies(MOVIE_CSV_FILE)
        cls.tags = Tags("../datasets/tags.csv")

    # Movies class tests
    def test_dist_by_release(self):
        result = self.movies.dist_by_release()
        precalculated_data=[(2002, 311), (2006, 295), (2001, 294), (2007, 284), (2000, 283)]
        assert list(result.items())[:5]==precalculated_data
        assert isinstance(result, dict)
        counts = list(result.values())
        assert all(isinstance(counts[i], int) for i in range(len(counts)))
        assert all(counts[i] >= counts[i + 1] for i in range(len(counts) - 1))

    def test_dist_by_genres(self):
        result = self.movies.dist_by_genres()
        precalculated_data=[('Drama', 4361), ('Comedy', 3756), ('Thriller', 1894), ('Action', 1828), ('Romance', 1596)]
        assert list(result.items())[:5]==precalculated_data
        assert isinstance(result, dict)
        counts = list(result.values())
        assert all(isinstance(counts[i], int) for i in range(len(counts)))
        assert all(counts[i] >= counts[i + 1] for i in range(len(counts) - 1))

    def test_most_genres(self):
        result = self.movies.most_genres(15)
        precalculated_data=[('Rubber (2010)', 10), ('Patlabor: The Movie (Kidô keisatsu patorebâ: The Movie) (1989)', 8), ('Mulan (1998)', 7), ('Who Framed Roger Rabbit? (1988)', 7), ('Osmosis Jones (2001)', 7)]
        assert list(result.items())[:5]==precalculated_data
        assert isinstance(result, dict)
        counts = list(result.values())
        assert all(isinstance(counts[i], int) for i in range(len(counts)))
        assert all(counts[i] >= counts[i + 1] for i in range(len(counts) - 1))
        assert len(result) == 15

    def test_get_movies_by_year(self):
        result = self.movies.get_movies_by_year(1999)
        precalculated_data=['"13th Warrior, The (1999)"', '"Adventures of Elmo in Grouchland, The (1999)"', '"Affair of Love, An (Liaison pornographique, Une) (1999)"', '"Astronaut\'s Wife, The (1999)"', '"Bachelor, The (1999)"']
        assert result[:5]==precalculated_data
        assert isinstance(result, list)
        assert all(isinstance(result[i], str) for i in range(len(result)))
        assert all(result[i] <= result[i + 1] for i in range(len(result) - 1))

    # Tags class tests
    def test_most_words(self):
        result = self.tags.most_words(10)
        precalculated_data=[('Something for everyone in this one... saw it without and plan on seeing it with kids!', 16)]
        assert list(result.items())[:1]==precalculated_data
        assert isinstance(result, dict)
        assert len(result) == len(set(result)) == 10
        counts = list(result.values())
        assert all(isinstance(counts[i], int) for i in range(len(counts)))
        assert all(counts[i] >= counts[i + 1] for i in range(len(counts) - 1))

    def test_longest(self):
        result = self.tags.longest(10)
        precalculated_data=[('Something for everyone in this one... saw it without and plan on seeing it with kids!', 85), ('the catholic church is the most corrupt organization in history', 63), ('audience intelligence underestimated', 36), ('Oscar (Best Music - Original Score)', 35), ('assassin-in-training (scene)', 28)]
        assert list(result.items())[:5]==precalculated_data
        assert isinstance(result, dict)
        assert len(result) == len(set(result)) == 10
        counts = list(result.values())
        assert all(isinstance(counts[i], int) for i in range(len(counts)))
        assert all(counts[i] >= counts[i + 1] for i in range(len(counts) - 1))

    def test_most_words_and_longest(self):
        result = self.tags.most_words_and_longest(10)
        precalculated_data=['Everything you want is here']
        assert result[:1]==precalculated_data
        assert isinstance(result, list)
        assert all(isinstance(item, str) for item in result)

    def test_most_popular(self):
        result = self.tags.most_popular(10)
        precalculated_data=[('funny', 15), ('sci-fi', 14), ('twist ending', 12), ('dark comedy', 12), ('atmospheric', 10)]
        assert list(result.items())[:5]==precalculated_data
        assert isinstance(result, dict)
        assert len(result) == len(set(result)) == 10
        counts = list(result.values())
        assert all(isinstance(counts[i], int) for i in range(len(counts)))
        assert all(counts[i] >= counts[i + 1] for i in range(len(counts) - 1))

    def test_tags_with(self):
        result = self.tags.tags_with('Netflix')
        precalculated_data=['In Netflix queue']
        assert result==precalculated_data
        assert isinstance(result, list)
        assert len(result) == len(set(result))
        assert all(isinstance(tag, str) for tag in result)
        assert all(result[i] <= result[i + 1] for i in range(len(result) - 1))

    def test_movie_by_tag(self):
        result=self.tags.movie_by_tag('Netflix')
        precalculated_data=['28']
        assert result==precalculated_data
        assert isinstance(result, list)
        assert len(result) == len(set(result))
        assert all(isinstance(tag, str) for tag in result)
        assert all(result[i] <= result[i + 1] for i in range(len(result) - 1))

    # Ratings class tests
    @pytest.fixture
    def sample_csv_file(self):
        """Create a sample CSV file for testing"""
        filename = "test_ratings.csv"
        content = """userId,movieId,rating,timestamp
1,1,5.0,1609459200
2,1,4.5,1609545600
1,2,3.0,1609632000
3,2,4.0,1609718400
2,3,2.5,1609804800
1,3,5.0,1609891200
3,1,3.5,1609977600
"""
        with open(filename, 'w') as f:
            f.write(content)
        yield filename
        if os.path.exists(filename):
            os.remove(filename)
    
    def test_ratings_init_data_types(self, sample_csv_file):
        """Test that Ratings initialization creates correct data types"""
        ratings = Ratings(sample_csv_file)
        
        assert isinstance(ratings.data_ratings, list)
        
        for record in ratings.data_ratings:
            assert isinstance(record, dict)
            assert isinstance(record['userId'], int)
            assert isinstance(record['movieId'], int)
            assert isinstance(record['rating'], float)
            assert isinstance(record['timestamp'], int)

    # Ratings.Movies class tests
    @pytest.fixture
    def movies_instance(self):
        """Create a Movies instance with sample data"""
        filename = "test_movies.csv"
        content = """userId,movieId,rating,timestamp
1,1,5.0,1609459200
2,1,4.5,1609545600
1,2,3.0,1609632000
3,2,4.0,1609718400
2,3,2.5,1609804800
1,3,5.0,1609891200
3,1,3.5,1609977600
"""
        with open(filename, 'w') as f:
            f.write(content)
        
        ratings = Ratings(filename)
        movies = ratings.Movies(ratings)
        yield movies
        
        if os.path.exists(filename):
            os.remove(filename)
    
    def test_dist_by_year_return_type(self, movies_instance):
        """test dist_by_year returns correct data types"""
        result = movies_instance.dist_by_year()
        
        assert isinstance(result, dict)
        
        for year, count in result.items():
            assert isinstance(year, int)
            assert isinstance(count, int)
    
    def test_dist_by_year_sorted(self, movies_instance):
        """test dist_by_year returns sorted data"""
        result = movies_instance.dist_by_year()
        years = list(result.keys())
        assert years == sorted(years)
    
    def test_dist_by_rating_return_type(self, movies_instance):
        """test dist_by_rating returns correct data types"""
        result = movies_instance.dist_by_rating()
        
        assert isinstance(result, dict)
        
        for rating, count in result.items():
            assert isinstance(rating, float)
            assert isinstance(count, int)
    
    def test_dist_by_rating_sorted(self, movies_instance):
        """test dist_by_rating returns sorted data"""
        result = movies_instance.dist_by_rating()
        ratings = list(result.keys())
        assert ratings == sorted(ratings)
    
    def test_top_by_num_of_ratings_return_type(self, movies_instance):
        """test top_by_num_of_ratings returns correct data types"""
        result = movies_instance.top_by_num_of_ratings(2)
        
        assert isinstance(result, dict)
        
        for title, count in result.items():
            assert isinstance(title, str)
            assert isinstance(count, int)
    
    def test_top_by_num_of_ratings_sorted(self, movies_instance):
        """test top_by_num_of_ratings returns sorted data (descending)"""
        result = movies_instance.top_by_num_of_ratings(3)
        counts = list(result.values())
        assert counts == sorted(counts, reverse=True)
    
    def test_top_by_ratings_return_type(self, movies_instance):
        """test top_by_ratings returns correct data types"""
        result = movies_instance.top_by_ratings(2, 'average')
        
        assert isinstance(result, dict)
        
        for title, rating in result.items():
            assert isinstance(title, str)
            assert isinstance(rating, float)
    
    def test_top_by_ratings_sorted(self, movies_instance):
        """test top_by_ratings returns sorted data (descending)"""
        result = movies_instance.top_by_ratings(3, 'average')
        ratings = list(result.values())
        assert ratings == sorted(ratings, reverse=True)
    
    def test_top_by_ratings_median_return_type(self, movies_instance):
        """test top_by_ratings with median metric returns correct data types"""
        result = movies_instance.top_by_ratings(2, 'median')
        
        assert isinstance(result, dict)
        
        for title, rating in result.items():
            assert isinstance(title, str)
            assert isinstance(rating, float)
    
    def test_top_controversial_return_type(self, movies_instance):
        """test top_controversial returns correct data types"""
        result = movies_instance.top_controversial(2)
        
        assert isinstance(result, dict)
        
        for title, variance in result.items():
            assert isinstance(title, str)
            assert isinstance(variance, float)
    
    def test_top_controversial_sorted(self, movies_instance):
        """test top_controversial returns sorted data (descending by variance)"""
        result = movies_instance.top_controversial(3)
        variances = list(result.values())
        assert variances == sorted(variances, reverse=True)

    def test_most_active_user_by_coverage(self, movies_instance):
        """test most_active_user_by_coverage returns correct types and range"""
        result = movies_instance.most_active_user_by_coverage()
        """check return type"""
        assert isinstance(result, tuple)
        user_id, percent = result
        """ check user_id and percent types"""
        assert (isinstance(user_id, int) or user_id is None)
        assert isinstance(percent, float)
        """check percent range"""
        assert 0 <= percent <= 100

    def test_percent_of_max_ratings_per_movie(self, movies_instance):
        """test percent_of_max_ratings_per_movie returns correct types, range, and sorting"""
        result = movies_instance.percent_of_max_ratings_per_movie()
        """check return type"""
        assert isinstance(result, dict)
        """check key and value types"""
        assert all(isinstance(title, str) for title in result.keys())
        assert all(isinstance(val, float) for val in result.values())
        """check value range"""
        assert all(0 <= val <= 100 for val in result.values())
        """check sorting (descending)"""
        values = list(result.values())
        assert values == sorted(values, reverse=True)

    def test_percent_of_max_ratings_per_movie_n(self, movies_instance):
        """test percent_of_max_ratings_per_movie with n returns correct types, length, and sorting"""
        n = 3
        result = movies_instance.percent_of_max_ratings_per_movie(n)
        assert isinstance(result, dict)
        assert len(result) == n
        values = list(result.values())
        """check sorting (descending)"""
        assert values == sorted(values, reverse=True)
        """check ValueError for invalid n"""
        assert movies_instance.percent_of_max_ratings_per_movie(0) == {}
        total = len(movies_instance.percent_of_max_ratings_per_movie())
        assert movies_instance.percent_of_max_ratings_per_movie(total + 1) == {}

    # Ratings.Users class tests
    @pytest.fixture
    def users_instance(self):
        """Create a Users instance with sample data"""
        filename = "test_users.csv"
        content = """userId,movieId,rating,timestamp
1,1,5.0,1609459200
2,1,4.5,1609545600
1,2,3.0,1609632000
3,2,4.0,1609718400
2,3,2.5,1609804800
1,3,5.0,1609891200
3,1,3.5,1609977600
"""
        with open(filename, 'w') as f:
            f.write(content)
        
        ratings = Ratings(filename)
        users = ratings.Users(ratings)
        yield users
        
        if os.path.exists(filename):
            os.remove(filename)
    
    def test_users_distribution_return_type(self, users_instance):
        """test users_distribution returns correct data types"""
        result = users_instance.users_distribution()
        
        assert isinstance(result, dict)
        
        for user_id, count in result.items():
            assert isinstance(user_id, int)
            assert isinstance(count, int)
    
    def test_users_rating_distribution_return_type(self, users_instance):
        """test users_rating_distribution returns correct data types"""
        result = users_instance.users_rating_distribution('average')
        
        assert isinstance(result, dict)
        
        for user_id, rating in result.items():
            assert isinstance(user_id, int)
            assert isinstance(rating, float)
    
    def test_users_rating_distribution_median_return_type(self, users_instance):
        """test users_rating_distribution with median metric returns correct data types"""
        result = users_instance.users_rating_distribution('median')
        
        assert isinstance(result, dict)
        
        for user_id, rating in result.items():
            assert isinstance(user_id, int)
            assert isinstance(rating, float)
    
    def test_top_n_users_by_variance_return_type(self, users_instance):
        """test top_n_users_by_variance returns correct data types"""
        result = users_instance.top_n_users_by_variance(2)
        
        assert isinstance(result, dict)
        
        for user_id, variance in result.items():
            assert isinstance(user_id, int)
            assert isinstance(variance, float)
    
    def test_top_n_users_by_variance_sorted(self, users_instance):
        """test top_n_users_by_variance returns sorted data (descending)"""
        result = users_instance.top_n_users_by_variance(3)
        variances = list(result.values())
        assert variances == sorted(variances, reverse=True)

    # Links class tests
    @pytest.fixture
    def links_instance(self):
        return Links("../datasets/links.csv", 10)

    def test_initialization(self, links_instance):
        assert len(links_instance._Links__movie_to_imdb) == 10
        assert links_instance._Links__movie_to_imdb == {
            1: '0114709',
            2: '0113497',
            3: '0113228',
            4: '0114885',
            5: '0113041',
            6: '0113277',
            7: '0114319',
            8: '0112302',
            9: '0114576',
            10: '0113189'
        }

    def test_get_imdb_structure(self, links_instance):
        result = links_instance.get_imdb(
            links_instance.get_ids_dict().keys(),
            ['Director', 'Budget', 'Cumulative Worldwide Gross', 'Runtime', 'Title']
        )
        assert isinstance(result, list)
        assert len(result) == 10
        assert all(isinstance(item, list) for item in result)
        assert all(len(item) == 6 for item in result)

    def test_get_imdb_values(self, links_instance):
        expected_data = [[10, 'Martin Campbell', 60000000.0, 352194034.0, 130, 'GoldenEye'],
                        [9, 'Peter Hyams', 35000000.0, 64350171.0, 111, 'Sudden Death'],
                        [8, 'Peter Hewitt', None, 23920048.0, 97, 'Tom and Huck'],
                        [7, 'Sydney Pollack', 58000000.0, 53696959.0, 127, 'Sabrina'],
                        [6, 'Michael Mann', 60000000.0, 187436818.0, 170, 'Heat'],
                        [5, 'Charles Shyer', 30000000.0, 76594107.0, 106, 'Father of the Bride Part II'],
                        [4, 'Forest Whitaker', 16000000.0, 81452156.0, 124, 'Waiting to Exhale'],
                        [3, 'Howard Deutch', 25000000.0, 71518503.0, 101, 'Grumpier Old Men'],
                        [2, 'Joe Johnston', 65000000.0, 262821940.0, 104, 'Jumanji'],
                        [1, 'John Lasseter', 30000000.0, 394436586.0, 81, 'Toy Story']
                        ]
        result = links_instance.get_imdb(
            links_instance.get_ids_dict().keys(),
            ['Director', 'Budget', 'Cumulative Worldwide Gross', 'Runtime', 'Title']
        )
        sorted_result = sorted(result, key=lambda x: x[0], reverse=True)
        for expected, actual in zip(expected_data, sorted_result):
            assert actual == expected

    def test_top_directors(self, links_instance):
        expected = {'Martin Campbell': 1,
                    'Peter Hyams': 1,
                    'Peter Hewitt': 1,
                    'Sydney Pollack': 1,
                    'Michael Mann': 1
                    }
        result = links_instance.top_directors(5)
        assert isinstance(result, dict)
        assert len(result) == 5
        assert dict(sorted(result.items(), key=lambda x: x[1], reverse=True)) == expected

    def test_most_expensive(self, links_instance):
        expected = {
            'Jumanji': 65000000.0,
            'Heat': 60000000.0,
            'GoldenEye': 60000000.0,
            'Sabrina': 58000000.0,
            'Sudden Death': 35000000.0
        }
        result = links_instance.most_expensive(5)
        assert isinstance(result, dict)
        assert result == expected

    def test_most_profitable(self, links_instance):
        expected = {
            'Toy Story': 364436586.0,
            'GoldenEye': 292194034.0,
            'Jumanji': 197821940.0,
            'Heat': 127436818.0,
            'Waiting to Exhale': 65452156.0
        }
        result = links_instance.most_profitable(5)
        assert isinstance(result, dict)
        assert result == expected

    def test_longest(self, links_instance):
        expected = {'Heat': 170, 'GoldenEye': 130, 'Sabrina': 127, 'Waiting to Exhale': 124, 'Sudden Death': 111}
        result = links_instance.longest(5)
        assert isinstance(result, dict)
        assert result == expected

    def test_top_cost_per_minute(self, links_instance):
        expected = {'Jumanji': 625000.0,
                    'GoldenEye': 461538.46,
                    'Sabrina': 456692.91,
                    'Toy Story': 370370.37,
                    'Heat': 352941.18
                    }
        result = links_instance.top_cost_per_minute(5)
        assert isinstance(result, dict)
        for k, v in result.items():
            assert pytest.approx(v, rel=1e-2) == expected[k]

    def test_get_imdb_rating(self, links_instance):
        expected = {1: '8.3/10',
                    2: '7.1/10',
                    3: '6.7/10',
                    4: '6.0/10',
                    5: '6.1/10',
                    6: '8.3/10',
                    7: '6.3/10',
                    8: '5.5/10',
                    9: '5.9/10',
                    10: '7.2/10'}
        result = links_instance.get_imdb_rating(links_instance.get_ids_dict().keys())
        assert isinstance(result, dict)
        assert result == expected