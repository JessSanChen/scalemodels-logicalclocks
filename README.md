# CS262 Design Project 2

## Usage and Setup: 

Clone the repository on each local computer that will be using the network (all clients and the server). 

### Running Experiments:
Run ``python machine.py`` in base directory. If successful, you'll see the ports connecting and eventually a series of printouts that show the machines communicating. Once complete, .txt log files will be generated and a matplotlib module will pop up. 

### Running Tests:
Run ``python tests.py`` in base directory. This will generate several sets of processes--for each one, you will see the machine connections and communications, followed by generated log outputs as well as printouts for whether each set passes their tests.

### Troubleshooting:
If you encounter "TypeError: cannot pickle '_io.TextIOWrapper' object", then use a virtual environment (conda, etc) to run on Python 3.7. There seems to be a bug in the Multiprocessing package after Python 3.8.

If you encounter "[Errno 48] Address already in use", then manually kill the processes. Find processes by running ``ps -fA | grep python``. Then, given some process 81651, for example, kill it by runnin ``kill 81651``.

## Engineering Notebook
Nothing fancy, just a Google Doc: https://docs.google.com/document/d/1G0VCzdG0dM1QfEQCNZVo66BfxE8sfqC0398XkFM3wLw/edit?usp=sharing
