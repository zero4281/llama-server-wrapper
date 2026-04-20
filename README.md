# LLama Server Wrapper

## Installation
### On macOS/Linux
`python3 -m venv .venv`

### On Windows
`python -m venv .venv`

### On macOS/Linux
`source .venv/bin/activate`

### On Windows
`.venv\Scripts\activate`

### Install the Hugginface Hub CLI for model managment
`pip install hf-cli`

## Run the Code
`./llama-server-wrapper`

## ProjectSkills
### Example Input for /project-create-todos  

Running this command: \`./llama-server-wrapper --install-llama\` has the following issues.  
  
  \* Using the arrow keys on the first menu (Select llama.cpp) causes the program to exit.  
  \* Using the Page Up and Page Down keys on the first menu (Select llama.cpp) don't select anything.  
  \* Using the number keys on the first menu (Select llama.cpp) does work and the selection isn't highlighted.  
  \* The second and third menus work as expected.  
  \* The confirmation prompt doesn't display in a curses menu and the previous menu is still visible.  
  \* Hitting enter on the confirmation prompt causes the program to exit without downloading llama.cpp and displays with two error messages:  
\```  
Release b8833 - llama-b8833-bin-ubuntu-x64.tar.gz  
Proceed? [Y/n]:  
Error: name 'logger' is not defined  
Error restoring terminal state: module 'curses' has no attribute 'keypad'  
\```  
  
Keyboard input needs to be simulated or the program will hang while waiting for user input.  Run two tests, one with numbers and one with arrow keys.  Update existing tests or add new tests in the `./Tests` folder.  
  
There is definitely an error in `./ui_manager.py` even if all the tests pass.  The tests are likely producing false positives and some of them might timeout.
