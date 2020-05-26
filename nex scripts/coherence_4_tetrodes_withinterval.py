#For a specified path, Coherence template, start time, and end time, and interval variables:
    
#Creates a folder with subdirectories for each interval of analysis.
#each subdirectory contains .csv files containing coherence data, one for each reference wire

#NEx needs to be out of demo mode to run this code.  Make sure your license is active, 
#or that you are connected via SX Virtual Key.  Reopen the datafile after connecting.

#importing libraries
import os
import nex

#selects the open Neuroexplorer document
doc = nex.GetActiveDocument()

#####################################################


##################################
#                                #
# PARAMETERS TO SET FOR ANALYSIS #
#                                #
##################################

# 1. The path for where the results are saved
destination = "C:/Users/earnestt/Desktop"

# 2. The name of the template being applied:
template = "coherence_4_tetrodes"

# 3. The start time in seconds of  the analysis window:
start = 0

# 4. The end time in seconds of  the analysis window:
#To select the end of any document, you can use
#       end = nex.GetDocEndTime(doc)
end = nex.GetDocEndTime(doc)

# 5.  The names of the interval variables to include; specify their names in this list:
intervals = ['pre-cocaine', 'post-cocaine']
#####################################################


#moves to the specified director

os.chdir(destination)

#loop for creating a new folder
#new directory name is the document title plus the name of the template used
#if the name already exists, a number is added 

g = 1
basename = nex.GetDocTitle(doc) + " " + template + " with intervals"
newdir = basename
while os.path.exists(newdir):
        newdir = basename + ' ' + str(g)
        g+=1
os.makedirs(newdir)

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
    
#moves into the destination directory
os.chdir(os.path.join(destination, newdir))
    
#modifies the analysis to te specified start and end times

nex.ModifyTemplate(doc, template, "Select Data From (sec)", str(start))
nex.ModifyTemplate(doc, template, "Select Data To (sec)", str(end))

#ensures no other interval filters are specified
nex.ModifyTemplate(doc, template, "Interval Filter", 'None')

#creates a new folder for each interval
#sets the analysis to for the correct interval

for interval in intervals:
    nex.ModifyTemplate(doc, template, "Interval Filter", interval)
    os.mkdir(interval)
    os.chdir(interval)
    
    #loops over the FP variables and uses each as a reference once
    #applies the coherence template
    #saves data as a .csv file in the new folder, with FP##.csv as the name
    
    for i in FP_variables:
        nex.ModifyTemplate(doc, template, "Reference", i)
        nex.ApplyTemplate(doc, template)
        nex.SaveNumResults(doc, i + ".csv")
    os.chdir(os.path.join(destination, newdir))

#exits the directory
#avoids issues with being unable to delete the newly created folder

os.chdir(destination)