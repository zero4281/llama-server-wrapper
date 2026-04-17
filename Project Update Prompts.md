# Project Update Prompts

## Note to the coding agent!!!
**DO NOT READ OR UPDATE THIS FILE!!!**

## Plan Prompt
`./Requirements.md` has been updated.  `Plan.md` is the implementation plan for this project.  Read `./Requirements.md` and `./Plan.md` and the code to verify that `./Plan.md` is up to date with the requirements.  Update `./Plan.md` with the new requirements.

## Update Prompt
Read `./Requirements.md` and `./Plan.md`.  Perform a gap assessment on the code base, but ignore './Unit Tests'.  Look for features to remove that have been implemented but are not required.  Then use the gap assessment to create or update `./Update.md` with information about the code updates that are still required.

## Implement Code Prompt
Read `./Requirements.md` and `./Plan.md`.  Use `./Update.md` to update the code.  Don't update any of the Markdown files.  Don't update or execute anything in `./Unit Tests`.  Create Todos and then complete them.

## Create Unit Test Prompt
**This one needs to be rethought.**
Read `./Requirements.md` and `./Plan.md`.  Scan the code base, including `./Unit Tests`. There should be one unit test file for every code file and/or class.  Update existing unit tests or create new unit tests if a file doesn't exists. Unit tests should be created with [unittest](https://docs.python.org/3/library/unittest.html) and save them to `./Unit Tests`.  Don't create unit tests for files in `./Unit Tests`.  Only create unit tests for main.py and top level class functions related to command line arguments and `config.json`.  Don't just add unit tests; remove old, unvaluable, and redundant unit tests as well.

## Run Unit Test Prompt
Read `./Requirements.md` and `./Plan.md`.  Read `./Tests/Tests.md` and `./Tests/Test Bugs.md`.  Run the tests and determine if the issues are with the tests or the code being tested.  Don't update the code, just update `./Tests/Test Bugs.md` with your findings.

## Bug Fix Prompt
Read `./Requirements.md` and `./Plan.md`.  Read `./Tests/Tests.md` and `./Tests/Test Bugs.md`.  Start fixing the bugs listed in `./Tests/Test Bugs.md`.  Ask the user which bug to fix before updating any code.  After updating the code run the tests again to verify that it's fixed.  If there are new bugs then ask the user what to do.

## Commit prompt
If the project is on the main branch then create a new branch with the format: `[feature/bugfix]/[version]-[short-description]` (e.g. `feature/v1.1-user-confirmation-flows`).  If the project is already in a feature branch (not the main branch) then continue without creating a branch.  Check `git status`, use `git ls-files --others --exclude-standard` to find new files, then create a git commit message.  Make sure the commit message is only one sentence long.  Then commit the update and push the commit.

## Create TODOs
Read `./Requirements.md` and `./Plan.md`.
Read `./Tests/Tests.md`.
Read `./TODOs.md`.

Don't do any work yet, just analysis.  Create or update `./TODOs.md` with enough detail about each TODO that the work can be picked up later.  Mark items as incomplete when they're added to the list.  Estimate the level of priority of each item.  Make sure to list any other items as dependencies for each TODO.

Base the analysis on this request:

## Complete TODO
Read `./Requirements.md` and `./Plan.md`.
Read `./Tests/Tests.md`.
Read `./TODOs.md`.

Create a list of items to work on from `./TODOs.md`.  Ignore items that are already marked as complete.  Ask the user which one to fix.  Make sure the list indicates the estimated priority and dependencies on other items in the list.  Once the user makes a selection delegate the work to @general with the context provided in `./TODOs.md` and this prompt (e.g. Read `./Requirements.md` and `./Plan.md`).  After the task is completed, mark the item status as complete in `./TODOs.md`.