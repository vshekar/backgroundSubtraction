# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 16:15:33 2014

@author: vesheka
This module written in cython performs the "heavy lifting" of the background 
subtraction algorithm. This has to be included in Experiment.py which defines
data structure used in the program

"""

import cython
import numpy as np
cimport numpy as np


cpdef subtract(np.ndarray[np.float64_t,ndim=1] a_RT,  a_spec, np.ndarray[np.float64_t,ndim=1] c_RT, c_spec, double mz_range, double RT_range, double mult_fac):
    """
    Perform subtraction of specta
    
    This function performs the subtraction of the control spectrum from the analyte spectrum.
    
    Args:
        a_RT: Analyte retention time (numpy array)
        a_spec: Analyte spectrum (numpy array) 
        c_RT: Control retention time (numpy array)
        c_spec: Control spectrum numpy array
        mz_range: Range of m/z to scan in ppm (Usually +/-10 ppm)
        RT_range: Retention time to scan in seconds (Usually +/-10 seconds)
        mult_fac: Factor by which the control is to be multiplied (Usually 10x)
    
    Returns:
        Subtracted spectrum a_spec
    
    """
    sub = []
    cdef int i = 0
    cdef int x = 0
    cdef double rt,mz
    
    mz_range = mz_range*0.000001
    for i in range(len(a_RT)):
        rt = a_RT[i]
        sub_inten = []
        for x in range(len(a_spec[i])):
            mz = a_spec[i][x,0]
            sub_inten.append(find_max(c_RT, c_spec, mz, rt, mz_range, RT_range))
        sub_inten = np.array(sub_inten)
        if i == 1:
            print sub_inten
        sub.append(sub_inten)
    #print len(a_spec)
    for i in range(len(a_RT)):
        a_spec[i][:,1] = a_spec[i][:,1] - (sub[i]*mult_fac)
    #print len(a_spec)
    return a_spec
    

cdef double find_max(np.ndarray[np.float64_t,ndim=1] c_rt, c_spec, double mz, double rt, double mz_range, double RT_range):
    """
    Find max intensity value in the control spectrum of specified range
    
    Finds the maximum intensity value in the control spectrum based on m/z value, 
    time window defined and the data point in the analyte spectrum.
    
    Args:
        c_rt: Control retention time (numpy array)
        c_spec: Control spectrum (numpy_array)
        mz: m/z value of the particular point in analyte spectrum
        rt: Retention time of particular point in analyte spectrum
        mz_range: Range of m/z to scan in ppm (Usually +/-10 ppm)
        RT_range: Retention time to scan in seconds (Usually +/-10 seconds)
        
    Returns:
        max_val: Maximum value
    
    """
    
    #Defining the bounds of the search
    cdef double start_time = rt - RT_range
    cdef double end_time = rt + RT_range
    cdef double start_mz = mz * (1 - mz_range)
    cdef double end_mz = mz * (1 + mz_range)
    
    all_intensities = []
    cdef int st_idx, et_idx, smz_idx, emz_idx, all_idx = 0
    
    #Finding the index of the columns based on time bounds (Columns represent time in spectrum)
    st_idx = find_index(c_rt,start_time)
    et_idx = find_index(c_rt,end_time)
    cdef int i = 0
    cdef int x = 0
    
    #Iterate through columns and find intensity values within m/z bounds
    for i in range(st_idx, et_idx):
        smz_idx = find_index(c_spec[i][:,0].astype('float64'),start_mz)
        emz_idx = find_index(c_spec[i][:,0].astype('float64'),end_mz)
        if smz_idx != emz_idx:
            for x in range(smz_idx, emz_idx):
                all_intensities.append(c_spec[i][x,1])
        
    #Convert list of found intensities into numpy array and find max
    all_intensities = np.array(all_intensities)
    max_val = 0
    if all_intensities.size > 0:
        max_val = np.amax(all_intensities)

    return max_val
    

cpdef int find_index(np.ndarray[np.float64_t,ndim=1] RT, double time):
    """
    Search the array and return the index of the value greater than supplied value
    
    This function assumes that the array to be searched is already sorted
    Args:
        RT: Retention time array OR m/z array, based on requirement
        time: supplied value, can be time OR m/z
    
    Returns:
        mid: Index of the value > supplied value
    
    e.g. array containing  a = [1 , 2 , 3 , 4 ,5]
    find_index(a, 2.5) will return 2
    
    """
    cdef int top,bot,mid
    top = 0 
    bot = len(RT)
    while (bot-top) >= 1:
        if bot-top == 1:
            mid = bot
            break
        else:
            mid = (bot+top)/2
            if RT[mid] > time:
                bot = mid
            elif RT[mid] < time:
                top = mid
            elif RT[mid] == time:
                top = mid
                bot = mid
            
    return mid
    
    
