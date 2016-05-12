# -*- coding: utf-8 -*-
"""
Created on Mon Jul 14 15:10:06 2014

@author: vesheka
"""

import cython
import numpy as np
cimport numpy as np
from datetime import datetime

DTYPE = np.float32
ctypedef np.float_t DTYPE_t

"""
cpdef subtract_multi(arguments):
    cdef np.ndarray control_RT = arguments[0]
    cdef np.ndarray control_list_of_spectra = arguments[1]
    cdef np.ndarray analyte_RT = arguments[2]
    cdef np.ndarray analyte_list_of_spectra = arguments[3]
    cdef double start_time = arguments[4]
    cdef double end_time = arguments[5]
    cdef int proc_num = arguments[6]
    cdef double tol_window = arguments[7]
    cdef double low_factor = 1- tol_window
    cdef double high_factor = 1+ tol_window
    cdef double time_window = arguments[8]
    cdef double scaling_factor = arguments[9]
    
    print("Starting Process number = " + str(proc_num) + str(tol_window) + str(time_window) + str(scaling_factor))
    startTime = datetime.now()
    cdef np.ndarray sliced_rt_indices = find_RT_range(analyte_RT, start_time, end_time)
    cdef np.ndarray sliced_spectra = np.take(analyte_list_of_spectra, sliced_rt_indices)
    
    cdef np.ndarray sliced_rt = analyte_RT[np.logical_and(analyte_RT>=start_time, analyte_RT<=end_time)]
    
    cdef int i = 0
    cdef double mz,lower_mz,upper_mz,lower_time,upper_time
    cdef int x = 0
    for i in range(len(sliced_spectra)):
        rt = sliced_rt[i]
        sub_fac = []
        
        for x in range(len(sliced_spectra[i])):
            mz = sliced_spectra[i][x][0]

            lower_mz = mz*low_factor
            upper_mz = mz*high_factor
            lower_time = rt-time_window
            upper_time = rt+time_window
            sub_fac.append(get_max(control_RT,control_list_of_spectra,lower_mz, upper_mz, lower_time, upper_time,scaling_factor))
            
        sub_fac = np.array(sub_fac)
        sliced_spectra[i][:,1] = sliced_spectra[i][:,1] - sub_fac
        s = sliced_spectra[i][:,1]
        s[s<0] = 0
        
    endTime = datetime.now()
    print("ENDING Process number = " + str(proc_num)+ "  Time slice : " + str(start_time) +"-"+str(end_time) + " , Total time taken = " + str(endTime-startTime))
    return (sliced_rt,sliced_spectra)
    
    
cdef double get_max(np.ndarray[np.double_t,ndim=1] control_RT, control_list_of_spectra, double lower_mz, double upper_mz, double lower_time, double upper_time, double scaling_factor):
    cdef double current_max = 0
    
    sliced_rt_indices = find_RT_range(control_RT,lower_time,upper_time)
    sliced_spectra = np.take(control_list_of_spectra, sliced_rt_indices)
    cdef int i = 0
    cdef double temp_max = 0
    for i in range(len(sliced_spectra)):
        temp_max = find_max(sliced_spectra[i],lower_mz,upper_mz)
        if temp_max > current_max:
            current_max = temp_max
            
    return scaling_factor*current_max

"""

cpdef find_RT_range(np.ndarray[np.double_t,ndim=1] RT,double start_time,double end_time):
    cdef int start_index = find_index(RT,start_time,0)
    cdef int end_index = find_index(RT,end_time,1)
    return np.arange(start_index,end_index,1)
    
    
cdef int find_index(np.ndarray[np.double_t,ndim=1] RT, double time, int switch):
    cdef int top,bot,mid
    top = 0 
    bot = RT.size
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
    
    
cdef int find_index_float(np.ndarray[np.float32_t,ndim=1] RT, double time, int switch):
    cdef int top,bot,mid
    top = 0 
    bot = RT.size
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
        
cpdef find_max(np.ndarray[np.float32_t,ndim=2] series,double start_mz,double end_mz):
    
    
    #cdef np.ndarray[np.double_t,ndim=2] series = s
    
    cdef int start_index = find_index_float(series[:,0],start_mz,0)
    cdef int end_index = find_index_float(series[:,0],end_mz,1)
    cdef np.ndarray[np.int_t, ndim=1] indices
    cdef int i = 0
    cdef double max_value = 0
    cdef double val
    
    indices = np.arange(start_index,end_index,1)
    
    for i in range(indices.size):
        val = series[indices[i],1]
        if val > max_value:
            max_value = val
            
    return max_value
        