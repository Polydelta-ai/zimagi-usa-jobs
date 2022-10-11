from django.conf import settings

from .data import RecursiveCollection

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
        self._data = self._top.get('SearchResultItems', [])

        for result in self._data:
            job = result['MatchedObjectDescriptor']
            job['Id'] = result['MatchedObjectId']
            job['UserArea'] = job['UserArea']['Details']

            self._results.append(RecursiveCollection(**self._convert_keys(job)))

    @property
    def count(self):
        return len(self._data)

    @property
    def full_count(self):
        return self._top.get('SearchResultCountAll', 0)


class USAJobsAPI(object):

    BASE_URL = "https://data.usajobs.gov"


    def __init__(self, command, wait_time = 0.5):
        self.command = command
        self.wait_time = wait_time

        self.api_email = settings.USA_JOBS_API_EMAIL
        self.api_key = settings.USA_JOBS_API_KEY


    def codes(self, name):
        response = self._codelist(name)
        for result in response.results:
            yield result

    def _codelist(self, name):
        self.command.info("Querying USA Jobs codes for: {}".format(name))
        response = requests.get("{}/api/codelist/{}".format(self.BASE_URL, name))
        logger.debug(response.url)

        if response.status_code != 200:
            raise USAJobsException("USA Jobs CodeList API returned status code: {}".format(response.status_code))

        return USAJobsCodeListResponse(response)


    def search(self,
        params = None,
        page_count = 500,
        start_page = 1,
        next_callback = None,
        complete_callback = None
    ):
        response = None
        next_page = start_page

        if not params:
            params = {}

        for name, value in params.items():
            if isinstance(value, (list, tuple)):
                params[name] = ";".join(value)

        while response is None or response.count == page_count:
            response = self._search(params, page_count, next_page)

            for result in response.results:
                yield result

            next_page += 1
            if next_callback and callable(next_callback):
                next_callback(next_page)

            time.sleep(self.wait_time)

        if complete_callback and callable(complete_callback):
                complete_callback()


    def _search(self, params, page_count, page):
        if not self.api_email or not self.api_key:
            raise USAJobsException('Environment variables ZIMAGI_USA_JOBS_API_EMAIL and ZIMAGI_USA_JOBS_API_KEY required with your credentials')

        params['ResultsPerPage'] = page_count
        params['Page'] = page

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
