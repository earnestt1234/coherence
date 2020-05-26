#Use this script to generate a folder containing coherence data for multiple time frames
#an output folder will be created
#in this folder, there will be sub folders which contain the coherence matrix for comparing tetrodes
#each subfolder will correspond to one time frame
#these subfolders can be looped over to create gifs, movies, or plots with a temporal dimension

#NEx needs to be out of demo mode to run this code.  Make sure your license is active, 
#or that you are connected via SX Virtual Key.  Reopen the datafile after connecting.

#importing libraries
import os
import nex
import sys
import csv

#selects the open Neuroexplorer document
doc = nex.GetActiveDocument()

#####################################################


##################################
#                                #
# PARAMETERS TO SET FOR ANALYSIS #
#                                #
##################################

# 1. The path for where the results are saved
destination = "C:\Users\earnestt\Desktop"

# 2. The name of the template being applied:
template = "coherence_4_tetrodes"

# 3. The start point for data anlysis, in seconds:
#Decimals should not cause issues
start = 0

# 4.  The end point for data analysis, in seconds
#The end point must be after the start point
#if you want the entire data file, you can set
#end = nex.GetDocEndTime(doc)
end = 3750

# 5. The bin size for analysis, in seconds:
#The bin size must be no larger than the analysis period (end-start)
binsize = 30

#####################################################

#Checks some conditions about the user input to make sure the analysis will run properly
#stops the program when there is an issue
if start >= end:
    print "Starting point (start) must be before ending point (end)."
    sys.exit()

if end > nex.GetDocEndTime(doc):
    print "The entered end of analysis period is outside of the recording length."
    sys.exit()
    
if binsize > (end-start):
    print "Analysis bin (binsize) must be at least the size of the analysis period."
    sys.exit()
    
#makes list of points where the start of a bin will be
#if the last point in bin_starts is too close to the end of the analysis window, 
#there will not be enough data to have a full bin
#in this case, this bin is dropped so that each bin has an equal amount of data

bin_starts = []

c = start
while c < end:
    bin_starts.append(c)
    c+=binsize

if (bin_starts[-1] + binsize) > end:
    del bin_starts[-1]

#One more bug check (although this shouldn't arise):

if len(bin_starts) == 0:
    print "No bins to analyze."
    sys.exit()

#moves to the specified director

os.chdir(destination)

##loop for creating a new folder
##if the name already exists, a number is added 
#
g = 1
basename = (nex.GetDocTitle(doc) + " Coherence (" + str(start) + "-" + str(end) + "s) bin = " + str(binsize))
newdir = basename
while os.path.exists(newdir):
        newdir = basename + " " + str(g)
        g+=1
os.makedirs(newdir)

#moves into the new directory

os.chdir(newdir)

#finds the field potential variables by searching for the string "FP"
#puts these into a new list, FP_variables

variables = list(doc.ContinuousNames())
FP_variables = []
for x in variables:
    if x[:2] == 'FP':
        FP_variables.append(x)

        
#variable selection
#first deselects all, then adds only the variables cued by FP_variables

nex.DeselectAll(doc)
for i in FP_variables:
    x = nex.GetVarByName(doc, i)
    nex.Select(doc, x)

#makres sure interval filter is unselected
nex.ModifyTemplate(doc, template, "Interval Filter", "None")

#main loop for extracting data

#loops over bin_starts, and makes a subdirectory based on the bin
#moves into that subfolder
#modifies the template to run the coherence analysis from the start to the end of the bin
#does this using each wire as a reference
#moves back into the superdirectory

for m in range(len(bin_starts)):
    subdir = str(m) + "_" + str(bin_starts[m]) + "-" + str(bin_starts[m]+binsize)
    os.makedirs(subdir)
    os.chdir(subdir)
    nex.ModifyTemplate(doc, template, "Select Data From (sec)", str(bin_starts[m]))
    nex.ModifyTemplate(doc, template, "Select Data To (sec)", str(bin_starts[m]+binsize))
    for i in FP_variables:
        nex.ModifyTemplate(doc, template, "Reference", i)
        nex.ApplyTemplate(doc, template)
        nex.SaveNumResults(doc, i + ".csv")
    os.chdir(os.path.join(destination,newdir))

#Adds a small .csv with some information about the analysis

os.chdir(os.path.join(destination, newdir))

infodict = {'start' : start, 'end' : end, 'bin length' : binsize,
            '# bins' : len(bin_starts)}

with open('info.csv', 'wb') as f:  # Just use 'w' mode in 3.x
    w = csv.DictWriter(f, infodict.keys())
    w.writeheader()
    w.writerow(infodict)

motion_vals = list(doc['Motion'].ContinuousValues())
motion_times = list(doc['Motion'].Timestamps())

with open('movement.csv', 'wb') as f:  # Just use 'w' mode in 3.x
    w = csv.writer(f)
    w.writerow(['time','motion'])
    for i in range(len(motion_vals)):
        w.writerow([motion_times[i],motion_vals[i]]) 

os.chdir(destination)