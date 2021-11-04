import os
import itertools
import tempfile
import resource
import subprocess
import time
from multiprocessing import Pool
import yaml
from .. import DATA_PATH
import polyply_regression_tests

class  DispatchError(Exception):
    """
    Class for handeling GROMACS errors. This class only
    prints the essentail part to the error message when
    raised.
    """

    def __init__(self, stderr):
        lines = stderr.decode("utf-8")
        message = "GROMACS terminated with the following error:\n"
        message = message + lines
        super().__init__(message)

def run_process(process, current_workdir):
    """
    Run a process in current_workdir.
    """
    os.chdir(current_workdir)

    start_rusage = resource.getrusage(resource.RUSAGE_CHILDREN)
    start_time = time.time()

    command = process.split()
    print(command)
    output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, input=None)

    end_time = time.time()
    end_rusage = resource.getrusage(resource.RUSAGE_CHILDREN)

    metrics = {}
    metrics["user_time"] = end_rusage.ru_utime - start_rusage.ru_utime
    metrics["sys_time"] = end_rusage.ru_stime - start_rusage.ru_stime
    metrics["wall_time"] = end_time - start_time

    if output.returncode:
        raise DispatchError(output.stderr)

    return output.stdout.decode('utf-8'), output.stderr.decode('utf-8'), metrics

def pipe(processes):
    time_output = {}
    with tempfile.TemporaryDirectory() as tmp_dir:
        for process in processes:
            try:
	            stdout, stderr, metrics = run_process(process,
                                                      current_workdir=tmp_dir)
            except DispatchError:
                raise OSError

           #with open("_time_statistic.dat", "w") as _file:
           #    for metric, time in metrics.items():
           #        _file.write("{} {:3.6f}\n".format(metric, time))

    return 0


def expand_job_matrix(strategy, steps, global_vars, job_vars, data_path):
    variables = strategy.keys()
    variable_values = [ strategy[key] for key in variables]
    job_matrix = []
    for tier_variables in itertools.product(*variable_values):
        tier_dict = dict(zip(variables, tier_variables))
        tier_dict["data_path"] = data_path
        tier_dict.update(global_vars)
        tier_dict.update(job_vars)
        processes = [ step.format(**tier_dict) for step in steps.values()]
        job_matrix.append(processes)

    return job_matrix

class WorkflowManager:

    def __init__(self, **kwargs):
        self.jobs = kwargs.pop("jobs")
        self.name = kwargs.pop("name")
        self.data_dir = os.path.join(polyply_regression_tests.__path__[0],
                                     DATA_PATH, kwargs.pop("data_path"))
        self.glob_vars = kwargs

    def run_jobs(self, nproc):
        for job in self.jobs.values():
            strategy = job.pop("strategy")
            steps = job.pop("steps")
            job_vars = job
            processes = expand_job_matrix(strategy,
                                          steps,
                                          self.glob_vars,
                                          job_vars,
                                          self.data_dir)
            pool = Pool(nproc)
            pool.map(pipe, processes)

    @classmethod
    def from_ymal(cls, stream):
        yml_dict = yaml.safe_load(stream)
        job_manager = cls(**yml_dict)
        return job_manager
