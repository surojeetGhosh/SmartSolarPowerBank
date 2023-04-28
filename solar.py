import json
import os
from web3 import Web3
import time
import RPi.GPIO as GPIO
import serial

#Setting up RPI.GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
dischargeRelay = 14
chargeRelay = 15
GPIO.setup(dischargeRelay, GPIO.OUT)
GPIO.setup(chargeRelay, GPIO.OUT)
GPIO.output(dischargeRelay, False)
GPIO.output(chargeRelay, True)



# Setting up discharging relay switch


# Setting up Machine
contract = json.load(open(os.path.join(os.path.dirname(__file__), 'contract.json')))
abi = contract['abi']
address = contract['address']
caller = contract['owner']
private = contract['private']
w3 = Web3(Web3.HTTPProvider('https://eth-sepolia.g.alchemy.com/v2/eeDrQCWpXpqdm5gsC8Ccyp2I3wpQwmw-'))
MachineCode = 1
state = False
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout = 1)
ser.reset_input_buffer()


#Checking if w3 is connected to provider or not
if w3.is_connected():
    print('Connected to Sepolia Ethereum')
    chain_id = w3.eth.chain_id
    #connecting to solar contract
    Solar = w3.eth.contract(address=address, abi=abi)
    print('Connected to Solar Contract')
    print('Machine Code: ', MachineCode)
    #calling initial state of the machine
    state = Solar.functions.getMachineState(MachineCode).call()
    print('Starting Machine Status: ', state)
    print("-"*50)
    while True:
        # fetching state of the machine
        state = Solar.functions.getMachineState(MachineCode).call()
        if state == True:
            GPIO.output(dischargeRelay, False)
            GPIO.output(chargeRelay, True)
            print("Machine Started")
            # Machine is on
            # Fetching current user
            user = Solar.functions.currentUser(MachineCode).call()
            # Fetching balance of user
            balance = Solar.functions.getBalance(user).call()
            print("User Connected: ",user)
            print("Balance Remaining: ", int(balance)/1e18)
            balance = int(balance)
            if user == "0x0":
                continue
            # if balance is 0 then machine should be stopped
            if balance  == 0:
                # balance is 0
                # Machine should be stopped
                Solar.functions.stopMachine(MachineCode).call()
                continue
            # Reading analog values of voltage and current sensor from arduino
            if ser.in_waiting > 0:
                try:
                    # Reading unit consumed each 5 second
                    unit = ser.readline().decode('utf-8').rstrip()
                    unit = int(float(unit) * 1e18)
                    # if unit < 0 [Boundary Case]
                    if unit < 0:
                        unit = 0
                except:
                    continue
            print("Unit Used:", unit/1e18)
            # If balance >= unit reduce unit from balance else set balance to 0
            if balance >= unit:
                Solar.functions.setBalance(user,unit).call()
            else:
                Solar.functions.setBalance(user,balance).call()
            # sleeping for 5 secondsmnxzasg
            time.sleep(5)                        
        else:
            GPIO.output(dischargeRelay, True)
            GPIO.output(chargeRelay, False)
            if ser.in_waiting > 0:
                try:
                    # Reading unit consumed each 5 second
                    unit = ser.readline().decode('utf-8').rstrip()
                    unit = int(float(unit) * 1e18)
                    # if unit < 0 [Boundary Case]
                    if unit < 0:
                        unit = 0
                except:
                    continue
            print("Unit Produced:", unit/1e18)
            print("Machine Stopped")
            time.sleep(5)
        print("-"*50)

   
   

else:
    print('Could not connect to Ethereum')
