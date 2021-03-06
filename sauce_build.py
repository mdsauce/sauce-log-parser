import sauce_job
import requests


class BuildNotFound(Exception):
    """Build was not present or the build does not exist"""
    pass


class SomethingWentWrong(Exception):
    """A non 200 HTTP status was returned.  Something bad may have happened"""
    pass


class Build():
    """docstring for Build."""

    URL_BASE = "{api_endpoint}/builds/{build_id}"
    URL_JOBS = URL_BASE + "/jobs"

    def __init__(self, api_endpoint, username, build_id):
        self.api_endpoint = api_endpoint
        self.build_id = build_id
        self.username = username
        self.job_list = []

    def get_build_id(self):
        return self.build_id

    def get_job_list(self):
        return self.job_list

    def get_job_ids(self, admin, access_key):
        url = self.URL_JOBS.format(api_endpoint=self.api_endpoint,
                                   build_id=self.build_id)

        resp = requests.get(url, auth=(admin, access_key))

        # TODO: Check for pagination

        if resp.status_code == 400:
            raise BuildNotFound
        if resp.status_code != 200:
            raise SomethingWentWrong

        json_resp = resp.json()
        tmp_job_list = json_resp['jobs']

        self.job_list = [job['id'] for job in tmp_job_list]

    def build_jobs(self, admin, access_key, write):
        jobs = []
        for job_id in self.job_list:
            job = sauce_job.Job(self.api_endpoint, self.username, job_id)
            job.parse_job_json(admin, access_key, write)

            jobs.append(job)
        return jobs
