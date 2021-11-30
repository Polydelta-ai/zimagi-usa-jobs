from django.utils.timezone import make_aware

from systems.plugins.index import BaseProvider
from utility.usa_jobs_api import USAJobsAPI
from utility.data import get_identifier

import datetime
import re


class Provider(BaseProvider('source', 'usa_job_search')):

    def item_columns(self):
        return {
            'location': [
                'id',
                'country',
                'province',
                'city',
                'latitude',
                'longitude'
            ],
            'organization': [
                'name',
                'parent',
                'locations'
            ],
            'job_source': [
                'name'
            ],
            'job_classification': [
                'code',
                'name',
            ],
            'job_grade': [
                'code'
            ],
            'job_schedule': [
                'code',
                'name'
            ],
            'job_offering_type': [
                'code',
                'name'
            ],
            'job_remuneration': [
                'id',
                'interval_code',
                'min_range',
                'max_range'
            ],
            'job_description': [
                'id',
                'label',
                'label_description',
                'content'
            ],
            'usa_job': [
                'source',
                'id',
                'title',
                'url',
                'locations',
                'organization',
                'department',
                'classifications',
                'grades',
                'schedules',
                'offering_types',
                'remunerations',
                'qualification_summary',
                'start_date',
                'end_date',
                'publication_start_date',
                'application_close_date',
                'descriptions',
                'major_duties',
                'education',
                'requirements',
                'evaluations',
                'how_to_apply',
                'what_to_expect_next',
                'required_documents',
                'benefits',
                'benefits_url',
                'other_information',
                'job_summary',
                'who_may_apply_name',
                'who_may_apply_code',
                'low_grade',
                'high_grade',
                'sub_agency_name',
                'organization_codes'
            ]
        }


    def load_items(self, context):
        return USAJobsAPI(self.command).search(**self._get_search_params())

    def load_item(self, job, context):
        source = 'USAJobs'

        locations = []
        for location in job.position_location:
            location.city_name = self._format_city(location)

            locations.append([
                get_identifier([
                    location.country_code,
                    location.country_sub_division_code,
                    location.city_name
                ]),
                location.country_code,
                location.country_sub_division_code,
                location.city_name,
                location.longitude,
                location.latitude
            ])
        location_ids = [ location[0] for location in locations ]

        organizations = [
            [ job.organization_name, None, location_ids ],
            [ job.department_name, job.organization_name, location_ids ]
        ]

        classifications = []
        for category in job.job_category:
            classifications.append([
                category.code,
                category.name
            ])

        grades = []
        for grade in job.job_grade:
            grades.append([
                grade.code
            ])

        schedules = []
        for schedule in job.position_schedule:
            schedules.append([
                schedule.code,
                schedule.name
            ])

        offering_types = []
        for offering_type in job.position_offering_type:
            offering_types.append([
                offering_type.code,
                offering_type.name
            ])

        remunerations = []
        for remuneration in job.position_remuneration:
            remunerations.append([
                get_identifier([
                    remuneration.rate_interval_code,
                    remuneration.minimum_range,
                    remuneration.maximum_range
                ]),
                remuneration.rate_interval_code,
                remuneration.minimum_range,
                remuneration.maximum_range
            ])

        descriptions = []
        for description in job.position_formatted_description:
            descriptions.append([
                get_identifier([
                    description.label,
                    description.label_description,
                    description.content
                ]),
                description.label,
                description.label_description,
                description.content
            ])

        if job.job_summary is None:
            job.job_summary = "\n\n".join([ str(description[3] or '') for description in descriptions ])

        return {
            'location': locations,
            'organization': organizations,
            'job_source': [ source ],
            'job_classification': classifications,
            'job_grade': grades,
            'job_schedule': schedules,
            'job_offering_type': offering_types,
            'job_remuneration': remunerations,
            'job_description': descriptions,
            'usa_job': [
                source,
                job.id,
                job.position_title,
                job.position_uri,
                location_ids,
                job.organization_name,
                job.department_name,
                [ classification[0] for classification in classifications ],
                [ grade[0] for grade in grades ],
                [ schedule[0] for schedule in schedules ],
                [ offering_type[0] for offering_type in offering_types ],
                [ remuneration[0] for remuneration in remunerations ],
                job.qualification_summary,
                make_aware(datetime.datetime.strptime(job.position_start_date, '%Y-%m-%dT%H:%M:%S.%f')),
                make_aware(datetime.datetime.strptime(job.position_end_date, '%Y-%m-%dT%H:%M:%S.%f')),
                make_aware(datetime.datetime.strptime(job.publication_start_date, '%Y-%m-%dT%H:%M:%S.%f')),
                make_aware(datetime.datetime.strptime(job.application_close_date, '%Y-%m-%dT%H:%M:%S.%f')),
                [ description[0] for description in descriptions ],
                job.user_area.major_duties,
                job.user_area.education,
                job.user_area.requirements,
                job.user_area.evaluations,
                job.user_area.how_to_apply,
                job.user_area.what_to_expect_next,
                job.user_area.required_documents,
                job.user_area.benefits,
                job.user_area.benefits_url,
                job.user_area.other_information,
                job.user_area.job_summary,
                job.user_area.who_may_apply.name,
                job.user_area.who_may_apply.code,
                job.user_area.low_grade,
                job.user_area.high_grade,
                job.user_area.sub_agency_name,
                job.user_area.organization_codes
            ]
        }


    def _format_city(self, location):
        city_name = location.city_name

        if location.country_sub_division_code:
            city_name = re.sub(r"[\s\,]+{}\s*$".format(location.country_sub_division_code), '', city_name)

        city_name = re.sub(r'^[\s\,]+', '', city_name)
        city_name = re.sub(r'[\s\,]+$', '', city_name)
        return city_name
