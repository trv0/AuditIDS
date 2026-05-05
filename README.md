The purpose of this project is to demonstrate knowledge of both common attack techniques as well as intrusion detection systems (IDS) via simulated network activity with a malicious actor. 
Attack techniques that are simulated will be detected and mapped based on the MITRE ATT&CK framework and delivered to the user for review. 

AttackSim.py simulates a login screen while also allowing user to perform several types of attacks. Logs “network” activity to a file (network_log.txt) in real time

inlineIDS.py reads from network_log.txt, examines each line as they appear to detect intrusion techniques and warn the user. Logs each alert into both terminal and new file (IDS_report.txt)

MITRE Techniques Demonstrated and Detected: 
    (TA006: Credential Access) T1110: Brute Force
        Brute force used to determine password
    (TA001: Initial Access) T1078: Valid Account 
        Use of legitimate, “compromised” credentials
    (TA001: Initial Access) T1190: Exploit Public Facing Information 
        SQL Injection


REQUIREMENTS: 

In terminal, please run: 
    pip install mitreattack-python

To Use: 
Run in two separate terminals: 
    python .\AttackSim.py
    python .\inlineIDS.py
    
All code was written and tested using Visual Studio Code. 

MITRE-Attack Data courtesy of : https://github.com/mitre/cti/blob/master/enterprise-attack/enterprise-attack.json