#Imports the programs I will need
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
    line_count = 0
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
    raise ValueError('Bad data, number of time curves does not match number of voltage curves')

timeconst=[]
for i in range(len(time_curves)):
    if len(time_curves[i]) > 10:
        voltage_curves[i] -= voltage_curves[i][6]
        time_curves[i] -= time_curves[i][6]
        pars, cov = curve_fit(f=exponential, xdata=time_curves[i][6:], ydata=voltage_curves[i][6:], p0=[0, 4000, 0], bounds=(-np.inf, np.inf))
        stdevs = np.sqrt(np.diag(cov))
        res = voltage_curves[i][6:] - exponential(time_curves[i][6:], *pars)
        timeconst.append(pars.item(1))
    else:
        pass

end_time = perf_counter()
duration = end_time - start_time
print(timeconst)
print(f"Finished in {duration} seconds")

#voltage_curves[4] -= voltage_curves[4][6]
#time_curves[4] -= time_curves[4][6]

#print(time_curves[4][6:])
#print(time_curves)
#print(voltage_curves)

########################## Visualization Code - not required to find time constant ##########################
#fig = plt.figure()
#ax = fig.add_axes([0, 0, 1, 1])
#ax.grid(True, which='both')
#ax.axhline(y=0, color='k')
#ax.axvline(x=0, color='k')

#raw data, generate every graph
#print(range(len(time_curves)))
#for i in range(len(time_curves)):
#    fig = plt.figure()
#    ax = fig.add_axes([0, 0, 1, 1])
#    
#    ax.scatter(time_curves[i], voltage_curves[i], s=20, label='Data')
#    plt.show()
#    print(i)
    #plt.cla()

#processed data, generate one graph
#ax.scatter(time_curves[4][6:], voltage_curves[4][6:], s=20, color='#00b3b3', label='Data')
#ax.plot(time_curves[4][6:], exponential(time_curves[4][6:], *pars), linestyle='--', linewidth=2, color='black')
#plt.show()