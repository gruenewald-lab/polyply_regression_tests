import mutliprocessing
import pytest
from polyply_regression_tests import YML_PATH
from polyply_regression_tests.workflow_utils.workflow_manager import WorkflowManager

@pytest.fixture("test_file",[
        YML_PATH/"template_test.yml",
        YML_PATH/"library_test.yml",
#       YML_PATH/"ring_test.yml",
#       YML_PATH/"template_test.yml",
        ])
def regression_test(test_file):
    nproc=multiprocessing.cpu_count()
    with open(test_file) as stream:
        workflow = WorkflowManager.from_yml_file(stream)
    result = workflow.run_jobs(nproc=nproc)
    assert result
