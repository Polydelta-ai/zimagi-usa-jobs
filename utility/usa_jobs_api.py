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


class USAJobsAnnouncementResponse(USAJobsResponse):

    def __init__(self, response):
        super().__init__(response)

        self._paging = self.json.get('paging', {}).get('metadata', {})
        self._data = self.json.get('data', [])

        for announcement in self._data:
            self._results.append(RecursiveCollection(**self._convert_keys(announcement)))

    @property
    def count(self):
        return len(self._data)

    @property
    def full_count(self):
        return self._paging.get('totalCount', 0)


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


    def announcements(self, page_count = 1000, **params):
        response = None
        next_page = 1

        while response is None or response.count == page_count:
            response = self._announcements(params, page_count, next_page)

            for result in response.results:
                yield result

            next_page += 1
            time.sleep(self.wait_time)

    def _announcements(self, params, page_count, page):
        params['Pagesize'] = page_count
        params['PageNumber'] = page

        self.command.info("Searching USA Job announcements with search parameters: {}".format(params))
        response = requests.get("{}/api/historicjoa".format(self.BASE_URL))
        logger.debug(response.url)

        if response.status_code != 200:
            raise USAJobsException("USA Jobs Announcement API returned status code: {}".format(response.status_code))

        return USAJobsAnnouncementResponse(response)


    def search(self, page_count = 500, **params):
        response = None
        next_page = 1

        for name, value in params.items():
            if isinstance(value, (list, tuple)):
                params[name] = ";".join(value)

        while response is None or response.count == page_count:
            response = self._search(params, page_count, next_page)

            for result in response.results:
                yield result

            next_page += 1
            time.sleep(self.wait_time)

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
