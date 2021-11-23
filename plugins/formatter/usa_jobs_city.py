from systems.plugins.index import BaseProvider

import re


class Provider(BaseProvider('formatter', 'usa_jobs_city')):

    def format(self, value, record):
        if record.get('province', None):
            value = re.sub(r"[\s\,]+{}\s*$".format(record['province']), '', value)

        value = re.sub(r'^[\s\,]+', '', value)
        value = re.sub(r'[\s\,]+$', '', value)
        return value
