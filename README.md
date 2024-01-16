# Personal Report of Process Control Experiment (PRPCE)
## Description:
This is the source code repo for a personal report on the pressure process control experiment of CYCU ChemE Dept.
## Project structure:
- [**controller_design**](controller_design)
     - [main.py](controller_design/main.py) : Main program of Controller parameter optimization.
- [**fit_model**](fit_model)
     - [main.py](fit_model/main.py) : Main program of FOPDT model analysis.
- [**rpi**](rpi)
     - [prbs.py](rpi/prbs.py) : Main program of process model data collection.
     - [control.py](rpi/control.py) : Main program of controller action.
## Usage:
[**controller_design**](controller_design) and [**fit_model**](fit_model) should be run on computers with ***Python version >= 3.12***. Set up ***virtual environments*** in the directories before running, and use the following commands to load dependencies:
```
python -m pip install -r requirements.txt
```
[**rpi**](rpi) should be deployed and run on ***Raspberry Pi 4B*** with ***Python version >=3.11***. Set up a ***virtual environment*** in the directory before running, and use the following command to load dependencies:
```
sudo apt install libgfortran5 libopenblas0-pthread
pip install -r requirements.txt
```