# Project Update Prompts

## Note to the coding agent!!!
**DO NOT READ OR UPDATE THIS FILE!!!**

## Plan Prompt
`./Requirements.md` has been updated.  Read it and the code to verify that `./Plan.md` is up to date with the new requirements.  Update `./Plan.md` with the new requirements and then create `./Update.md` with information about the code updates are still required.

## Update Prompt
Read `./Requirements.md` and `./Plan.md`. Use `./Update.md` to update the code.  Don't update the Markdown files.

## Create Unit Test Prompt
Read `./Requirements.md` and `./Plan.md`.  Update or create unit tests with [unittest](https://docs.python.org/3/library/unittest.html) and save them to `./Unit Tests`.  The unit tests are saved to `./Unit Tests`, don't create unit tests for these files.

## Run Unit Test Prompt
Run the unit tests in `./Unit Tests`.  Use the results of the unit tests to create `./Bugs.md`.

## Bug Fix Prompt
Read `./Requirements.md` and `./Plan.md`.  Read `./Bugs.md` and update the code.

## Commit prompt
Check `git status`, use `git ls-files --others --exclude-standard` to find new files, and read `./Update.md` to create a git commit message.  Make sure the commit message is only once sentence long.  Then commit the update.