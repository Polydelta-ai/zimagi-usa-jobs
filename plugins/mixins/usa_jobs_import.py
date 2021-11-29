from systems.plugins.index import ProviderMixin

import re


class USAJobsImportMixin(ProviderMixin('usa_jobs_import')):

    def _get_search_params(self):
        params = {}
        for key in self.meta['option'].keys():
            if key[0].isupper() and self.config.get(key, None):
                params[key] = self.config[key]
        return params
