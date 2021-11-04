# Copyright 2021 University of Groningen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pbr.version
__version__ = pbr.version.VersionInfo('polyply_regression_tests').release_string()

# Find the data directory once.
try:
    import pkg_resources
except ImportError:
    import os
    YML_PATH = os.path.join(os.path.dirname(__file__), 'ymls')
    DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
    FF_PATH = os.path.join(os.path.dirname(__file__), 'data/force_fields')
    del os
else:

    YML_PATH = os.path.join(os.path.dirname('polyply_regression_tests'), 'ymls')
    DATA_PATH = os.path.join(os.path.dirname('polyply_regression_tests'), 'data')
    FF_PATH = os.path.join(os.path.dirname('polyply_regression_tests'), 'data/force_fields')
    del pkg_resources

del pbr
