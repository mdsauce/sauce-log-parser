"""Created objects needed for Sauce logs"""
import json
import log_collector


class Job(object):
    """docstring for Job."""

    duration = {}
    between_commands = {}
    commands_json = None

    def __init__(self, api_endpoint, owner, job_id):
        super(Job, self).__init__()
        self.api_endpoint = api_endpoint
        self.owner = owner
        self.job_id = job_id

    def parse_json_log(self, admin, access_key, write):
        """Downloads log"""
        try:
            response = log_collector.get_log(self.api_endpoint, admin,
                                             access_key, self.owner,
                                             self.job_id, write)
        except log_collector.AssetsNotFound:
            print("404 API response.  The assets for %s are no longer available\
(> 30 days since test creation) or do not exist." % self.job_id)
            return
        except log_collector.SomethingWentWrong:
            print("Something went wrong. Try running with '-v'")
            return
        if response:
            self.commands_json = json.loads(response)

    def parse_commands(self, timing_value):
        """Reads in commands_json and calculates max, min, mean and total"""
        commands = []
        results = {}
        if self.commands_json is None:
            results["mean"] = "n/a"
            results["max"] = "n/a"
            results["min"] = "n/a"
            results["total"] = "n/a"
            return results

        for log in self.commands_json:
            # If "status" is present, a javascript title was sent
            if "status" in log:
                pass
            else:
                curr_command = log[timing_value]
                if curr_command is not None:
                    commands.append(curr_command)
        if commands:  # Check if there's actual commands to process
            results["mean"] = Job.mean(commands)
            results["max"] = max(commands)
            results["min"] = min(commands)
            results["total"] = Job.total(commands)

        return results

    @staticmethod
    def print_results(results):
        "Prints results dict with the desired calculations"
        if results:
            print("  mean: {}".format(results["mean"]))
            print("  max: {}".format(results["max"]))
            print("  min: {}".format(results["min"]))
            print("  total: {}".format(results["total"]))
        else:
            print("There is no commands to be parsed")

    def generate_results(self):
        """Creates results dicts from commands_json and
        then outputs the results to the user.
        """
        if self.commands_json is None:
            print("Could not download job id", self.job_id)
            return
        self.duration = self.parse_commands("duration")
        self.between_commands = self.parse_commands("between_commands")

        print("---")
        print("test_id: {}".format(self.job_id))
        print("duration:")
        Job.print_results(self.duration)
        print("between_commands:")
        Job.print_results(self.between_commands)
        print("")

    @staticmethod
    def mean(num_list):
        """Calculates mean of a list"""
        i = 0
        num_sum = 0.0
        for item in num_list:
            num_sum += item
            i += 1
        return num_sum/i

    @staticmethod
    def total(num_list):
        """Calculates total of a list"""
        num_sum = 0.0
        for item in num_list:
            num_sum += item
        return num_sum
