from django.conf import settings

from .data import RecursiveCollection

import copy
import time
import requests
import re
import logging


logger = logging.getLogger(__name__)


class USAJobsException(Exception):
    pass


class USAJobsResponse(object):

    def __init__(self, response):
        self.response = response
        self.json = response.json()
        self._results = []


    @property
    def results(self):
        return self._results


    def _convert_keys(self, data):
        conversion = data

        if isinstance(data, (list, tuple)):
            conversion = []

            for value in data:
                conversion.append(self._convert_keys(value))

        elif isinstance(data, dict):
            conversion = {}

            for key, value in data.items():
                key = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', key)
                key = re.sub('([a-z0-9])([A-Z])', r'\1_\2', key).lower()

                conversion[key] = self._convert_keys(value)

        return conversion


class USAJobsCodeListResponse(USAJobsResponse):

    def __init__(self, response):
        super().__init__(response)

        self._top = self.json.get('CodeList', [])
        if self._top:
            self._top = self._top[0].get('ValidValue', [])

        for result in self._top:
            self._results.append(RecursiveCollection(**self._convert_keys(result)))


class USAJobsSearchResponse(USAJobsResponse):

    def __init__(self, response):
        super().__init__(response)

        self._top = self.json.get('SearchResult', {})

        for result in self._top.get('SearchResultItems', []):
            job = result['MatchedObjectDescriptor']
            job['UserArea'] = job['UserArea']['Details']

            self._results.append(RecursiveCollection(**self._convert_keys(job)))

    @property
    def page_count(self):
        return self._top.get('SearchResultCount', 0)

    @property
    def full_count(self):
        return self._top.get('SearchResultCountAll', 0)


class USAJobsAPI(object):

    BASE_URL = "https://data.usajobs.gov"


    def __init__(self, command, page_count = 500, wait_time = 0.5):
        self.command = command
        self.page_count = page_count
        self.wait_time = wait_time

        self.api_email = settings.USA_JOBS_API_EMAIL
        self.api_key = settings.USA_JOBS_API_KEY


    def codes(self, name):
        response = self._codelist(name)
        for result in response.results:
            yield result


    def search(self, params = None):
        response = None
        next_page = 1

        if params is None:
            params = {}
        else:
            params = copy.deepcopy(params)

        for name, value in params.items():
            if isinstance(value, (list, tuple)):
                params[name] = ";".join(value)

        while response is None or response.page_count == self.page_count:
            params['Page'] = next_page
            response = self._search(params)

            for result in response.results:
                yield result

            next_page += 1
            time.sleep(self.wait_time)


    def _codelist(self, name):
        self.command.info("Querying USA Jobs codes for: {}".format(name))
        response = requests.get("{}/api/codelist/{}".format(self.BASE_URL, name))
        logger.debug(response.url)

        if response.status_code != 200:
            raise USAJobsException("USA Jobs CodeList API returned status code: {}".format(response.status_code))

        return USAJobsCodeListResponse(response)


    def _search(self, params):
        if not self.api_email or not self.api_key:
            raise USAJobsException('Environment variables ZIMAGI_USA_JOBS_API_EMAIL and ZIMAGI_USA_JOBS_API_KEY required with your credentials')

        params['ResultsPerPage'] = self.page_count

        if 'Page' not in params:
            params['Page'] = 1

        self.command.info("Searching USA Jobs with search parameters: {}".format(params))
        response = requests.get("{}/api/search".format(self.BASE_URL), params = params, headers = {
            "Host": "data.usajobs.gov",
            "User-Agent": self.api_email,
            "Authorization-Key": self.api_key,
        })
        logger.debug(response.url)

        if response.status_code != 200:
            raise USAJobsException("USA Jobs Search API returned status code: {}".format(response.status_code))

        return USAJobsSearchResponse(response)
