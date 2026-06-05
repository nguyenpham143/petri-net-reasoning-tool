# BTL-MHH-251 HCMUT

Petri Net Analysis Tool - Assignment Group 35

This Petri Net Analysis tool supports State Space exploration, Reachability analysis, Deadlock detection, and Optimization.

System Requirements

Operating System: Windows (using WSL - Windows Subsystem for Linux) or Linux/MacOS.

Python: Version 3.10 or higher.

Installation & Running Instructions (Step-by-Step)

Below is the standard procedure to run the program on a Windows environment using WSL.

1. Start the Environment

Open your WSL terminal (Ubuntu/Debian on Windows) and navigate to the project directory.

2. Create Virtual Environment

Create a separate environment to avoid library conflicts.

python3 -m venv venv


3. Activate the Environment

source venv/bin/activate


(After running this command, your command line should show the (venv) prefix).

4. Install Required Libraries

Install numpy, pyeda, pulp, and other dependencies from the configuration file.

pip install -r requirements.txt


Testing

The program comes with 2 sample test files located in the tests/ directory.

5. Run Default Test (Small Size - Has Deadlock)

This command defaults to reading the tests/test_small.pnml file.

python3 main.py


Expected Result:

Task 4: Reports DEADLOCK DETECTED.

Task 3 (BDD) and Task 2 (BFS) state counts match.

6. Run Medium Test (Medium Size - Safe)

Specify a specific input file using the --input argument.

python3 main.py --input tests/test_medium.pnml


Expected Result:

Task 4: Reports SYSTEM IS SAFE (Deadlock-free).

Task 5: Finds the optimal marking.

Test Case Descriptions

1. tests/test_small.pnml (Small Size)

Description: Models a simple Resource Allocation problem between 2 processes.

Characteristics: Small structure, easy to track (consists of 6 places, 4 transitions).

Properties: Contains a DEADLOCK due to circular resource contention (Circular Wait).

2. tests/test_medium.pnml (Medium Size)

Description: Models a Parallel Workflow process (Fork-Join type). A task splits into 2 parallel branches and merges upon completion.

Characteristics: Larger state space, uses a Mutex to protect shared resources.

Properties: SAFE System (Safe/Live), no Deadlock, ensures 1-Safe property.