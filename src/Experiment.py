# -*- coding: utf-8 -*-
"""
Created on Wed Jul 09 11:37:26 2014

@author: vesheka
Defines the Expriment class and the implementation of the subtraction algo
for the multiprocessing module in python (It does not accept classes)

"""
import numpy as np
from pyopenms import *
from datetime import datetime
#from searchRT import *
import subtract as sub
import sys
import math




class Experiment(object):
    """
    The Experiment class is an alternate implementation of the MSExperiment() class
    in pyopenms. This class ONLY extracts the retention time values and the peak values
    from MSExperiment()
    
    This class assumes the mzml file imported is a high resolution chromatogram.
    
    """
    def __init__(self):
        self.RT = []    #List of retention time
        self.list_of_spectra = [] #List of [m/z,intensity] values
        self.filename = ""   #Filename of the mzml file imported
        self.graph_points = []  #Maximum intensity values at each retention time (Used to genereate graphs in GUI)
        self.graph_points_mz = [] #M/z values of the intensity values in graph_points
        
    def write_to_file(self,filename):
        """
        Write the spectra into an mzml file
        
        Note: None of the metadata associated with the original mzml file is 
        saved. ONLY the retention time, m/z and intensities are written
        
        Args:
            filename: Full path of the file to be written (if .mzml is not present, it will add it)
            
        Returns:
            0: If write is successful
            1: If write fails
        """
        exp = MSExperiment()
        mzmlFile = MzMLFile()
        
        
        for i,spec in enumerate(self.list_of_spectra):
            
            s = pyopenms.MSSpectrum()
            s.setRT(self.RT[i])
            s.set_peaks(spec)
            exp.addSpectrum(s)
            
        if filename[-5:] != ".mzml":
            filename = filename + ".mzml"
            
        try:
            mzmlFile.store(filename,exp)
        except:
            return 1
        else:
            return 0
        
    def import_data(self,experiment):
        """
        Imports pyopenms.MSExperiment() type into Experiment format
        
        If MSExperiment is already in memory, this function converts it to Experiment
        (Currently only used in import_data_from_mzml)
        Args:
            experiment: pyopenms.MSExperiment() type
        
        Returns:
            nothing
        """
        for spec in experiment:
            self.RT.append(spec.getRT())
            self.list_of_spectra.append(spec.get_peaks())
            if len(spec.get_peaks()) > 0:
                idx = np.argmax(spec.get_peaks()[:,1])
                self.graph_points.append(spec.get_peaks()[idx,1])
                self.graph_points_mz.append(spec.get_peaks()[idx,0])
            else:
                self.graph_points.append(0)
                self.graph_points_mz.append(0)                
        
        self.RT = np.array(self.RT)
        self.list_of_spectra = np.array(self.list_of_spectra)
        self.graph_points = np.array(self.graph_points)
        print "RT length = " + str(len(self.RT))
        print "Graph point length = " + str(len(self.graph_points))
        
    def import_data_from_mzml(self,mzmlfilename):
        """
        Import mzml file directly to Experiment
        
        This function assumes that the file being imported is high resolution
        mass spectrometry data. This data is processed (peak picking) to reduce
        it to a managable amount to perform background subtraction. 
        Signal to noise ratio is set to 1.0. This can be increased to remove 
        more points although not recommended due to potential data loss
        
        """
        self.filename = mzmlfilename
        exp = MSExperiment()            #Input experiment to peak picker
        mzmlFile = MzMLFile()
        mzmlFile.load(mzmlfilename,exp)
        self.import_data(exp)
        
    def import_processed_mzml(self,mzmlfilename):
        self.filename = mzmlfilename
        exp = MSExperiment()
        mzmlFile = MzMLFile()
        mzmlFile.load(mzmlfilename,exp)
        self.import_data(exp)
        
    def get_scan(self,scan_number):
        """Returns the peak list correnponding to scan number (in numpy array form)"""
        return self.list_of_spectra[scan_number]
    
    def get_RT(self,time):
        """Returns a peak list corresponding to the time stamp passed""" 
        return self.list_of_spectra[np.where(self.RT[:]==time)]
        
    def gen_indices(self,index):
        for i in range(index-self.scan_range,index+self.scan_range):
            if i >= 0 and i < len(self.list_of_spectra) and i != index:
                yield i

    def adjacent_ions(self,index,mz,tol_window):
        ion_count = 0
        for i in self.gen_indices(index):
            spec = self.list_of_spectra[i]
            mz_spec = self.list_of_spectra[i][:,0].astype('float64')
            start_mz_index = sub.find_index(mz_spec ,mz*(1-tol_window))
            end_mz_index = sub.find_index(mz_spec ,mz*(1+tol_window))
            if start_mz_index != end_mz_index:
                for x in range(start_mz_index,end_mz_index):
                    if spec[x,1] > 0:
                        ion_count += 1
        return ion_count
    
    def reduce_noise(self,min_ion_count,scan_range,tol_window, output_filename):
        self.scan_range = scan_range
        for index, spec in enumerate(self.list_of_spectra):
            for point in spec:
                if point[1] > 0:    #point[1] is intensity
                    ion_count = self.adjacent_ions(index,point[0],tol_window)
                    if ion_count < min_ion_count:
                        point[1] = 0
        self.write_to_file(output_filename)
        
            


tol_window = 15
low_factor = 1-tol_window
high_factor = 1+tol_window
time_window = 10.0
scaling_factor  = 20.0
completed_tasks = None

def init(args):
    global completed_tasks
    completed_tasks = args

     
def subtract_multi(arguments):
    
    #Performs subtraction of supplied experiment from the current experiment (Used for background sub) MULTIPROCESSING VERSION
    global completed_tasks
    control_RT = arguments[0]
    control_list_of_spectra = arguments[1]
    analyte_RT = arguments[2]
    analyte_list_of_spectra = arguments[3]
    start_time = arguments[4]
    end_time = arguments[5]
    proc_num = arguments[6]
    tol_window = arguments[7]
    time_window = arguments[8]
    scaling_factor = arguments[9]
    
    
    try:
        a_spec = sub.subtract(analyte_RT, analyte_list_of_spectra, control_RT, control_list_of_spectra, tol_window, time_window, scaling_factor, start_time, end_time, proc_num)
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise
        
    
    start_index = sub.find_index(analyte_RT,start_time)
    end_index = sub.find_index(analyte_RT,end_time)
    sliced_rt = analyte_RT[start_index:end_index]
    sliced_spectra = a_spec[start_index:end_index]
    for i,series in enumerate(sliced_spectra):
        s = series[:,1]
        s[s<0] = 0
    
    completed_tasks.value = completed_tasks.value+1
    print "Completed Tasks , Process number " + str(completed_tasks.value) + "," + str(proc_num)
    
    return (sliced_rt, sliced_spectra)
                   
"""        
        #for scan_num,spec in enumerate(self.list_of_spectra):
            #for mz,i in spec:
def subtract_multi(arguments):
    
    #Performs subtraction of supplied experiment from the current experiment (Used for background sub) MULTIPROCESSING VERSION
    
    control_RT = arguments[0]
    control_list_of_spectra = arguments[1]
    analyte_RT = arguments[2]
    analyte_list_of_spectra = arguments[3]
    start_time = arguments[4]
    end_time = arguments[5]
    proc_num = arguments[6]
    
    print("Starting Process number = " + str(proc_num))
    startTime = datetime.now()
    #assert isinstance(control_experiment, Experiment), "Argument of subtract should be of type Experiment"
    #sliced_rt_indices = np.where(np.logical_and(analyte_RT>=start_time, analyte_RT<=end_time))
    sliced_rt_indices = find_RT_range(analyte_RT,start_time,end_time)
    #sliced_spectra = analyte_list_of_spectra[sliced_rt_indices]
    sliced_spectra = np.take(analyte_list_of_spectra,sliced_rt_indices)
    #sliced_rt = analyte_RT[sliced_rt_indices]
    sliced_rt = analyte_RT[np.logical_and(analyte_RT>=start_time, analyte_RT<=end_time)]
    
    for i,series in enumerate(sliced_spectra):
        rt = sliced_rt[i]
        sub_fac = []
        for mz,i in series:
            lower_mz = mz*low_factor
            upper_mz = mz*high_factor
            lower_time = rt-time_window
            upper_time = rt+time_window
            sub_fac.append(get_max(control_RT,control_list_of_spectra,lower_mz, upper_mz, lower_time, upper_time))
    
        sub_fac = np.array(sub_fac)
        series[:,1] = series[:,1] - sub_fac
        s = series[:,1]
        s[s<0] = 0
        
    endTime = datetime.now()
    print("ENDING Process number = " + str(proc_num)+ "  Time slice : " + str(start_time) +"-"+str(end_time) + " , Total time taken = " + str(endTime-startTime))
    return (sliced_rt,sliced_spectra)
         
def get_max(control_RT,control_list_of_spectra,lower_mz, upper_mz, lower_time, upper_time):
    #Returns the maximum value of intensity for the given range of m/z value and time
    current_max = 0
    #max_list  = np.empty([0,])
    
    #sliced_rt_indices = np.where(np.logical_and(control_RT>=lower_time, control_RT<=upper_time))
    sliced_rt_indices = find_RT_range(control_RT,lower_time,upper_time)
    
    #sliced_spectra = control_list_of_spectra[sliced_rt_indices]
    sliced_spectra = np.take(control_list_of_spectra, sliced_rt_indices)
    
    
    
    for series in sliced_spectra:
        #temp_indices = find_RT_range(series[:,0],lower_mz,upper_mz)
       
        #temp = series[np.logical_and(series[:,0]>=lower_mz, series[:,0]<=upper_mz),1]
        #temp = np.take(series[:,1],temp_indices)
        #print(temp)
        #series = series.astype('float64')
        temp_max = find_max(series,lower_mz,upper_mz)
        if temp_max > current_max:       
            current_max = temp_max
        #max_list = np.concatenate((max_list,temp))
        #max_list = np.append(max_list,temp)
    #if len(max_list)>0:
        #current_max = np.amax(max_list)        
        #current_max = max_list.max()
    
    return scaling_factor*current_max        
    
    """