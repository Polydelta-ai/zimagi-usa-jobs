from systems.plugins.index import BaseProvider
from utility.usa_jobs_api import USAJobsAPI


class Provider(BaseProvider('source', 'usa_job_announcements')):

    def item_columns(self):
        return [
            'source',
            'id',
            'vendor',
            'travel_requirements',
            'telework_eligible',
            'service_type',
            'security_clearance_required',
            'security_clearance',
            'promotion_potential',
            'supervisory_status',
            'drug_test_required',
            'relocation_expenses_reimbursed',
            'openings'
        ]


    def load_items(self, context):
        return USAJobsAPI(self.command).announcements(**self._get_search_params())

    def load_item(self, announcement, context):
        return [
            'USAJobs',
            announcement.usajobs_control_number,
            announcement.vendor,
            announcement.travel_requirement,
            True if announcement.telework_eligible.strip().upper() == 'Y' else False,
            announcement.service_type,
            True if announcement.security_clearance_required.strip().upper() == 'Y' else False,
            announcement.security_clearance,
            announcement.promotion_potential,
            True if announcement.supervisory_status.strip().upper() == 'Y' else False,
            True if announcement.drug_test_required.strip().upper() == 'Y' else False,
            True if announcement.relocation_expenses_reimbursed.strip().upper() == 'Y' else False,
            announcement.total_openings
        ]
