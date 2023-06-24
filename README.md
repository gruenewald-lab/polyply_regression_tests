# Regression tests for polyply

This repository conaints a number of tests in form of workflows which incooperate polyply. They can be used to ensure 
that the current version yields the same results as intented. The tests should be executed by running pytest on this
repository after installing as detailed below. Note that some are resource hungry tests. 

## Running regression tests
1. Clone repository
2. Install it
3. change to polyply_regression_tests/tests
4. run pytest test_regression.py

## Adding regression tests
To add a regression test make a PR. This PR should contain the desired workflow in form of a yml file syntax as outliend
below. Add the name of the yml file to the regression test pytest module. Place all data in the subfolder in the data 
folder. Make sure the test suceeds. 

## Regression test yml file syntax


## Binder Launch
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/marrink-lab/polyply_regression_tests/main?labpath=https%3A%2F%2Fgithub.com%2Fmarrink-lab%2Fpolyply_regression_tests%2Fblob%2Fmain%2Fexamples%2Fliquid_liquid_phase_separation%2FPolyplyTutorial.ipynb)
