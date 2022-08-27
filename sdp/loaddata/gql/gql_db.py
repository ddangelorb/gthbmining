import abc
import requests
import json
import time
from datetime import datetime


class VariableDates:
    def __init__(self, initial_date, final_date):
        self.initial_date = initial_date
        self.final_date = final_date


class GQLdb(metaclass=abc.ABCMeta):
    URL_GRAPHQL_REQUEST = "https://api.github.com/graphql"

    def __init__(self, logger, function_name, token, set_query_limit=True):
        self.logger = logger
        self.function_name = function_name
        self.headers = {'Authorization': 'token %s' % token, 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
        self.rate_limit_query = ""
        if set_query_limit:
            f_query = open("gql/query/GetRateLimit.gql", mode='r')
            self.rate_limit_query = f_query.read()
            f_query.close()

    @abc.abstractmethod
    def _get_query(self):
        pass

    @abc.abstractmethod
    def _get_variables(self, initial_date, final_date, after_cursor):
        pass

    @abc.abstractmethod
    def _get_total_count_value(self, data):
        pass

    @abc.abstractmethod
    def _preprocess_data(self, data):
        pass

    @abc.abstractmethod
    def _get_has_next_page(self, data):
        pass

    @abc.abstractmethod
    def _get_after_cursor(self, data):
        pass

    def _get_post_requests(self, query, variables):
        post_return = requests.post(url=self.URL_GRAPHQL_REQUEST, json={'query': query, 'variables': variables}, headers=self.headers)
        if post_return.status_code != 200:
            post_return.raise_for_status()
        return json.loads(post_return.text)

    def _get_data_request(self, query, variables):
        #check the rate limit before querying
        data_rate_limit = self._get_post_requests(self.rate_limit_query, None)
        remaining_limit = data_rate_limit["data"]["rateLimit"]["remaining"]
        if remaining_limit < 50:
            self.logger.info("          {} Sleeping for 1 hour due to the remaining limit less than 50...".format(self.function_name))
            time.sleep(3600)

        return self._get_post_requests(query, variables)

    def _get_total_count(self, statement, initial_date, final_date):
        parameters = self._get_variables(initial_date, final_date, None)
        data = self._get_data_request(statement, parameters)
        return self._get_total_count_value(data)

    def _get_variable_dates_queries(self, statement, initial_date, final_date):
        variable_dates_queries = []
        data_total_count = self._get_total_count(statement, initial_date, final_date)

        # https://docs.github.com/en/rest/reference/search#about-the-search-api
        if data_total_count < 1000 or data_total_count == -1:
            variable_dates_queries.append(VariableDates(initial_date, final_date))
        else:
            final_date = datetime.now().strftime('%Y-%m-%d')
            year_param = datetime.strptime(final_date, '%Y-%m-%d').year
            while data_total_count > 1000:
                initial_date = "{}-01-01".format(year_param)
                variable_dates_queries.append(VariableDates(initial_date, final_date))
                year_param -= 1
                final_date = "{}-12-31".format(year_param)
                data_total_count = self._get_total_count(statement, initial_date, final_date)
            variable_dates_queries.append(VariableDates("*", final_date))

        return variable_dates_queries

    def insert(self):
        query = self._get_query()

        variable_dates_queries = self._get_variable_dates_queries(query, "*", "*")
        for variable_dates_query in variable_dates_queries:
            has_next_page = True
            after_cursor = None
            variables = self._get_variables(variable_dates_query.initial_date, variable_dates_query.final_date, after_cursor)
            while has_next_page:
                data = self._get_data_request(query, variables)
                self._preprocess_data(data)

                has_next_page = self._get_has_next_page(data)
                if has_next_page:
                    self.logger.info("          {} Sleeping for 5 seconds...".format(self.function_name))
                    time.sleep(5)
                    after_cursor = self._get_after_cursor(data)
                    variables = self._get_variables(variable_dates_query.initial_date, variable_dates_query.final_date, after_cursor)
