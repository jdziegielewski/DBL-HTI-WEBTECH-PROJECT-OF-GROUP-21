To setup a virtual environment:
-------------------

	- Python 3 must be installed

	- Open Command Prompt (or Anaconda Prompt if python isn't in system environment variables)

	- Navigate to target root directory of the application (/app/)

	- "python -m venv webtech-env" to create the environment (the folder "webtech-env" will be ignored by git)

	- "webtech-env\Scripts\activate.bat" to activate the environment (this allows for installing packages / running python commands from anywhere)

	- "python -m pip install --upgrade pip" to upgrade pip (python package manager)
		(if this doesn't work, install pip first using "python get-pip.py")

	- "pip install -r requirements.txt" to install required libraries (~400mb) to the virtual environment
		(assuming the requirements.txt file is in the root directory)
	
	Now activate.bat or deactivate.bat (in webtech-env\Scripts\) can be used from a prompt to toggle the environment.

Launch
------

	- python app/flask_app.py

Use
---

	- Documentation is included on the website. The visualization tool is explained in detail in the report.