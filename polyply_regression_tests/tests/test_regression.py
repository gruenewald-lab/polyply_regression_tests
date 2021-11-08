import os
import multiprocessing
import pytest
import polyply_regression_tests
from polyply_regression_tests import YML_PATH
from polyply_regression_tests.workflow_utils.workflow_manager import WorkflowManager

@pytest.mark.parametrize("test_file",(
        "template.yml",
        "restraints.yml",
#       YML_PATH/"ring_test.yml",
#       YML_PATH/"template_test.yml",
        ))
def test_regression(test_file):
    nproc=multiprocessing.cpu_count()
    test_file_path = os.path.join(polyply_regression_tests.__path__[0], YML_PATH, test_file)
    with open(test_file_path) as stream:
         workflow = WorkflowManager.from_ymal(stream)
    result = workflow.run_jobs(nproc=nproc)
    assert result
