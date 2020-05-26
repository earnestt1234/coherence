#like 'coherence_4_tetrodes_overtime', but a interval is used instead of a manually entered start and end time

#Use this script to generate a folder containing coherence data overtime
#an output folder will be created
#in this folder, there will be sub folders for each interval
#within these folders, there will be coherence matrices for comparing tetrodes
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
destination = "C:/Users/earnestt/Desktop/"

# 2. The name of the template being applied:
template = "coherence_4_tetrodes"

# 3.  The intervals to use; these must match the variable names in NEx exactly.
intervals = ['test interval']

# 4. The bin size for analysis, in seconds:
#The bin size must be no larger than the analysis period (end-start)
binsize = 30

#####################################################
variables = list(doc.ContinuousNames())
FP_variables = []
for x in variables:
    if x[:2] == 'FP':
        FP_variables.append(x)
nex.DeselectAll(doc)
for i in FP_variables:
    x = nex.GetVarByName(doc, i)
    nex.Select(doc, x)
    
nex.ModifyTemplate(doc, template, "Interval Filter", 'None')

#build a series of dictionaries with intervals as keys, values are:
interval_starts = {} #start time of each interval segment
interval_ends = {} #end time of each interval segment
interval_absolute_start = {} #start of the first segment of the interval
interval_absolute_end = {} #end of the last segment of the interval
interval_lengths = {} #length of each segment of each interval
interval_lengths_overbinsize = {} #whether or not each interval segment is longer than the binsize
interval_bin_starts = {} #where each bin of anlysis starts for each interval
interval_good_bins = {} #whether or not each bin is good, i.e. is fully inside of the interval

for interval in intervals:
    interval_starts[interval] = doc[interval].Intervals()[0]
    interval_ends[interval] = doc[interval].Intervals()[1]
    interval_absolute_start[interval] = interval_starts[interval][0]
    interval_absolute_end[interval] = interval_ends[interval][-1]
    interval_lengths[interval] = [interval_ends[interval][i] - interval_starts[interval][i] for i,_ in enumerate(interval_starts[interval])] 
    interval_lengths_overbinsize[interval] = [x >= binsize for x in interval_lengths[interval]]
    interval_bin_starts[interval] = []
    c = interval_absolute_start[interval]
    while c < interval_absolute_end[interval]:
        interval_bin_starts[interval].append(c)
        c+= binsize
    if (interval_bin_starts[interval][-1] + binsize) > interval_absolute_end[interval]:
        del interval_bin_starts[interval][-1]
    
    assert any(interval_lengths_overbinsize[interval]), 'For interval "' + interval + '", no interval segments are longer than the binsize.'
    assert len(interval_bin_starts[interval]) > 0, '# of bins computes to 0 for the interval, "' + interval + '".'
    
    start_end_zip = zip(interval_starts[interval], interval_ends[interval])
    good_bins_list = []
    for bin_start in interval_bin_starts[interval]:
        bin_status = False
        for start, end in start_end_zip:
            if (bin_start >= start) and (bin_start+binsize <= end):
                bin_status = True
                break
        good_bins_list.append(bin_status)
    interval_good_bins[interval] = good_bins_list
    
#breaking loop so that analyses are only run if all variables have checked out
g = 1
basename = (nex.GetDocTitle(doc) + " Coherence over time with filters")
newdir = os.path.join(destination, basename)
while os.path.exists(newdir):
        temp = basename + " " + str(g)
        newdir = os.path.join(destination, temp)
        g+=1
        
os.makedirs(newdir)

#looping again with the working data
for interval in intervals:
    interval_folder_path = os.path.join(newdir, interval)
    os.makedirs(interval_folder_path)
    for i, bin_start in enumerate(interval_bin_starts[interval]):
        subdir_name = str(i) + "_" + str(bin_start) + "-" + str(bin_start+binsize)
        subdir_path = os.path.join(interval_folder_path,subdir_name)
        os.makedirs(subdir_path)
        nex.ModifyTemplate(doc, template, "Select Data From (sec)", str(bin_start))
        nex.ModifyTemplate(doc, template, "Select Data To (sec)", str(bin_start+binsize))
        for FP in FP_variables:
            nex.ModifyTemplate(doc, template, "Reference", FP)
            nex.ApplyTemplate(doc, template)
            savepath = os.path.join(subdir_path, FP + '.csv')
            nex.SaveNumResults(doc, savepath)
            
    infodict = {'start' : interval_absolute_start[interval], 
                'end' : interval_absolute_end[interval], 
                'bin length' : binsize,
                '# bins' : len(interval_bin_starts[interval])}
    info_csv_path = os.path.join(interval_folder_path, 'info.csv')
    movement_csv_path = os.path.join(interval_folder_path, 'movement.csv')
    bin_key_csv_path = os.path.join(interval_folder_path, 'bin_key.csv')
    with open(info_csv_path, 'wb') as f:  # Just use 'w' mode in 3.x
        w = csv.DictWriter(f, infodict.keys())
        w.writeheader()
        w.writerow(infodict)
    motion_vals = list(doc['Motion'].ContinuousValues())
    motion_times = list(doc['Motion'].Timestamps())
    with open(movement_csv_path, 'wb') as f:  # Just use 'w' mode in 3.x
        w = csv.writer(f)
        w.writerow(['time','motion'])
        for i in range(len(motion_vals)):
            w.writerow([motion_times[i],motion_vals[i]])
    with open(bin_key_csv_path, 'wb') as f:
        w = csv.writer(f)
        w.writerow(['bin #', 'complete'])
        for index, value in enumerate(interval_good_bins[interval]):
            w.writerow([index, value])
            
    