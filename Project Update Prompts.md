# Project Update Prompts

## Note to the coding agent!!!
**DO NOT READ OR UPDATE THIS FILE!!!**

## Create Unit Test Prompt
**This one needs to be rethought.**
Read `./Requirements.md` and `./Plan.md`.  Scan the code base, including `./Unit Tests`. There should be one unit test file for every code file and/or class.  Update existing unit tests or create new unit tests if a file doesn't exists. Unit tests should be created with [unittest](https://docs.python.org/3/library/unittest.html) and save them to `./Unit Tests`.  Don't create unit tests for files in `./Unit Tests`.  Only create unit tests for main.py and top level class functions related to command line arguments and `config.json`.  Don't just add unit tests; remove old, unvaluable, and redundant unit tests as well.

## Run Unit Test Prompt
Read `./Requirements.md` and `./Plan.md`.  Read `./Tests/Tests.md` and `./Tests/Test Bugs.md`.  Run the tests and determine if the issues are with the tests or the code being tested.  Don't update the code, just update `./Tests/Test Bugs.md` with your findings.

## Bug Fix Prompt
Read `./Requirements.md` and `./Plan.md`.  Read `./Tests/Tests.md` and `./Tests/Test Bugs.md`.  Start fixing the bugs listed in `./Tests/Test Bugs.md`.  Ask the user which bug to fix before updating any code.  After updating the code run the tests again to verify that it's fixed.  If there are new bugs then ask the user what to do.