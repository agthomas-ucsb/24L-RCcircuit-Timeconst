#Imports the necessary libraries
import csv
import tkinter as tk
from tkinter import filedialog
from time import sleep, perf_counter
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
#Defines the exponetial function, the value we are interested in is our time constant, b

def exponential(x, a, b, c):
    return a*np.exp(-b*x) + c

#Hides the Tk() window
root = tk.Tk()
root.withdraw()

#Opens the file explorer
filename = filedialog.askopenfilename(title = "Select a File", filetypes = (("csv files", "*.csv*"), ("all files", "*.*"))) 

start_time = perf_counter()

#Creates blank lists to append data into
time=[]
voltage=[]

with open(filename) as csv_file:
    csv_reader=csv.reader(csv_file)
    line_count=0
    #print(csv_reader)
    for row in csv_reader:
        if line_count < 20:
            line_count += 1
        else:
            # print(f'\t{row[0]} seconds {row[1]} volts.')
            time = np.append(time,float(row[0]))
            voltage = np.append(voltage,float(row[1]))

#sets up a dummy variable to test with, we start at 10 to allow system a few miliseconds to get started.
x = 10

#This prunes out the initial wave and gives us a new starting point so we know we are starting at the beginning of a curve.
if voltage[10] > voltage[9]:
    #print('starts increasing')
    while voltage[x+1] > voltage[x]:
        x += 1
    mode = 'dec'
else:
    #print('starts decreasing')
    while voltage[x+1] <= voltage[x]:
        x += 1
    mode = 'inc'
#This is the starting value for the first curve we will find

#Creates the master lists to populate
time_curves = []
voltage_curves = []

#Creates the arrays to append voltage into
time_curve = np.array([])
voltage_curve = np.array([])

while x <= len  (voltage)-5:
    if mode == 'inc':
        #checks if the "boxcar average" of 3 points increases or decreases from the next box
        if voltage[x+2] + voltage[x+3] + voltage[x+4] > voltage[x-1] + voltage[x] + voltage[x+1]:
            #print('increasing')
            voltage_curve = np.append(voltage_curve, voltage[x])
            time_curve = np.append(time_curve, time[x])
            x += 1
        else:
            #print('stopped increasing')
            voltage_curves.append(voltage_curve)
            time_curves.append(time_curve)
            voltage_curve = np.array([])
            time_curve = np.array([])
            mode = 'dec'
    if mode == 'dec':
        if voltage[x+2] + voltage[x+3] + voltage[x+4] <= voltage[x-1] + voltage[x] + voltage[x+1]:
            #print('decreasing')
            voltage_curve = np.append(voltage_curve, voltage[x])
            time_curve = np.append(time_curve, time[x])
            x += 1
        else:
            #print('stopped decreasing')
            voltage_curves.append(voltage_curve)
            time_curves.append(time_curve)
            voltage_curve = np.array([])
            time_curve = np.array([])
            mode = 'inc'

if len(time_curves) != len(voltage_curves):
    raise ValueError('Bad data, number of time curves does not match number of voltage curves') #If there is somehow more values of time than voltage, something is really wrong and we need to abort asap.

str1 = input(f'there are {len(time_curves)} curves, please enter a number for which curve would you like to view?\n')
while True:                     #An infinite loop.
    try:                        #This allows attempt something dangerous, turning the inputted string into an integer without crashing if it isn't an integer
        choice=int(str1) - 1    #Checks for an error.
    except ValueError:          #Expects the error so python doesn't error out
        print("Your input was not an integer, please try again")    #If there was an error, make them give you a new value until there is no error.                         
    else:
        if choice not in range(0, len(time_curves)):
            print(f'{str1} is not between 1 and {len(time_curves)}, please select another') #Explains the error
        elif len(time_curves[choice]) > 10:   #Checks if the curve is a fragment
            voltage_curves[choice] -= voltage_curves[choice][6]
            time_curves[choice] -= time_curves[choice][6]
            pars, cov = curve_fit(f=exponential, xdata=time_curves[choice][6:], ydata=voltage_curves[choice][6:], p0=[0, 4000, 0], bounds=(-np.inf, np.inf))
            stdevs = np.sqrt(np.diag(cov))
            res = voltage_curves[choice][6:] - exponential(time_curves[choice][6:], *pars)
            timeconst = pars.item(1)
            break
        else:
            print('This curve does not contain enough points and could not be processed, please select another') #Explains the error
    str1=input() #Makes the user try again
    #If there isn't an error, break the loop. 

scientific_notation = "{:0.3e}".format(timeconst) #Changes the timeconst to scientific notation with 3 decimal places
printme = 'τ=' + str(scientific_notation) #Creates the Tau equals timeconst line to show on the figure

########################## Visualization Code - not required to find time constant ##########################

#processed data, generate one graph
plt.scatter(time_curves[choice][6:], voltage_curves[choice][6:], s=20, color='#00b3b3', label='Data') #Plots the data
plt.plot(time_curves[choice][6:], exponential(time_curves[choice][6:], *pars), linestyle='--', linewidth=2, color='black') #Plots the curve fitted line
plt.title("Specified Voltage over Time Curve with Initial Value at Origin") #Adds the title
plt.xlabel("Time [s]")      #Adds the x-axis label
plt.ylabel("Voltage [V]")   #Adds the y-axis label

pos1, pos2 = plt.xlim()
pos3, pos4 = plt.ylim()
x = pos2*0.75
if abs(pos3) > abs(pos4):
    y = pos3*0.75
else:
    y= pos4*0.75

plt.text(x, y, printme, horizontalalignment='center', verticalalignment='center', bbox=dict(facecolor='grey', alpha=0.5)) #Adds the text showing the time constant on the figure
plt.show() #Shows the figure

#Performance information that can be printed or displayed
end_time = perf_counter()
duration = end_time - start_time
#print(f"Finished in {duration} seconds")
