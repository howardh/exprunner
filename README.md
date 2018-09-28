# Problems I want to solve

* Lots of experiments are run, and many simultaneously. Sometimes, I get interesting results from one of these executions, but forget what changes I made for that execution, and even if I remember, I might make a mistake reverting the code to that state in order to reproduce those results. I want to automatically save the state of the code when each experiment is run, as well as the exact command that was executed.
* Want to be notified when an execution is completed, whether that be into an interactive session or not.
* After an execution is started, I want to be able to add notes to each execution as they're running. This is so I can remind myself of why I'm running this, and what to do next depending on what the outcome is.

# Plan

* Everything can be saved as git objects
* Commit names can be something simple like "execution #n" where `n` just increments with each execution.
* Each execution can be a separate commit whose parent is HEAD and the last execution
* A ref (refs/exprunner/lastexecution) will point to the last execution.
* Notes on each execution can be saved with git notes.
* Information to store in the commit message:
	* Command that was executed
	* Time of execution
	* Directory in which the command was executed
	* Machine that the command was executed on

Note: There's still the problem of machine state at time of execution. Some scripts are not run with a clean slate, and depend on other scripts being run before it. I don't know how I'd keep track of this.
