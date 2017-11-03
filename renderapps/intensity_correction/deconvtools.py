# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 18:05:26 2016

@author: olgag
"""
# this module contains all functions used to apply deconvolution to image

import numpy as np
from scipy.fftpack import fftn, ifftn

def psf2otf(psf, otf_size):
    # calculate otf from psf with size >= psf size
    
    if psf.any(): # if any psf element is non-zero    
        # pad PSF with zeros up to image size  
        pad_size = ((0,otf_size[0]-psf.shape[0]),(0,otf_size[1]-psf.shape[1]))
        psf_padded = np.pad(psf, pad_size, 'constant')    
        
        # circularly shift psf   
        psf_padded = np.roll(psf_padded, -int(np.floor(psf.shape[0]/2)), axis=0)    
        psf_padded = np.roll(psf_padded, -int(np.floor(psf.shape[1]/2)), axis=1)       
       
       #calculate otf    
        otf = fftn(psf_padded)
        # this condition depends on psf size    
        num_small = np.log2(psf.shape[0])*4*np.spacing(1)    
        if np.max(abs(otf.imag))/np.max(abs(otf)) <= num_small:
            otf = otf.real 
    else: # if all psf elements are zero
        otf = np.zeros(otf_size)
    return otf

def otf2psf(otf, psf_size):
    # calculate psf from otf with size <= otf size
    
    if otf.any(): # if any otf element is non-zero
        # calculate psf     
        psf = ifftn(otf)
        # this condition depends on psf size    
        num_small = np.log2(otf.shape[0])*4*np.spacing(1)    
        if np.max(abs(psf.imag))/np.max(abs(psf)) <= num_small:
            psf = psf.real 
        
        # circularly shift psf
        psf = np.roll(psf, int(np.floor(psf_size[0]/2)), axis=0)    
        psf = np.roll(psf, int(np.floor(psf_size[1]/2)), axis=1) 
        
        # crop psf
        psf = psf[0:psf_size[0], 0:psf_size[1]]
    else: # if all otf elements are zero
        psf = np.zeros(psf_size)
    return psf

def deconvlucy(image, psf, num_iter, weight=None, subsmpl=1):
    # apply Richardson-Lucy deconvolution to image    
    
    # calculate otf from psf with the same size as image
    otf = psf2otf(psf, np.array(image.shape)*subsmpl)
    
    # create list to be used for iterations
    data = [image, 0, [0, 0]]    
    
    # create indexes taking into account subsampling
    idx = [np.tile(np.arange(0,image.shape[0]), (subsmpl,1)).flatten(1),
            np.tile(np.arange(0,image.shape[1]), (subsmpl,1)).flatten(1)]
         
    if weight is None:
        weight = np.ones(image.shape) # can be input parameter
    # apply weight to image to exclude bad pixels or for flat-field correction
    image_wtd = np.maximum(weight*image, 0)    
    data[0] = data[0].take(idx[0], axis=0).take(idx[1], axis=1)
    weight = weight.take(idx[0], axis=0).take(idx[1], axis=1)    
    # normalizing constant    
    norm_const = np.real(ifftn(otf.conj()*fftn(weight))) + np.sqrt(np.spacing(1))
    
    if subsmpl !=1:
        vec = np.zeros(len(image.shape)*2, dtype=np.int)
        vec[np.arange(0,len(image.shape)*2,2)] = image.shape
        vec[vec==0] = subsmpl
        
    # iterations
    alpha = 0 # acceleration parameter
    for k in range(num_iter):
        if k > 2:
            alpha = np.dot(data[2][0].T,data[2][1])\
                    /(np.dot(data[2][1].T,data[2][1]) + np.spacing(1))             
            alpha = max(min(alpha,1),0) # 0<alpha<1
        
        # make the estimate for the next iteration and apply positivity constraint       
        estimate = np.maximum(data[0] + alpha*(data[0] - data[1]), 0)
        
        # construct the expected image from the estimate         
        reblurred = np.real(ifftn(otf*fftn(estimate)))                
              
        # If subsmpl is not 1, bin reblurred back to original image size by 
        # calculating mean
        if subsmpl !=1:        
            reblurred = reblurred.reshape(vec)
            for i in np.arange(1,len(image.shape)*2,2)[::-1]:
                reblurred =reblurred.mean(axis=i)             
                        
        reblurred[reblurred==0] = np.spacing(1)        
        
        # calculate the ratio of the measured image to the expected image        
        ratio = image_wtd/reblurred + np.spacing(1)
        ratio = ratio.take(idx[0], axis=0).take(idx[1], axis=1)
        
        # determine next estimate and apply positivity constraint       
        data[1] = data[0]        
        data[0] = np.maximum(estimate*np.real(ifftn(otf.conj()*fftn(ratio)))\
                             /norm_const, 0)
        data[2] = [np.array([np.ravel(data[0] - estimate, order='F')])\
                   .T,data[2][0]]
    return data[0] 
    
def deconvblind(image, psf, num_iter, weight=None, subsmpl=1):
    # apply blind deconvolution to image    
         
    # create lists to be used for iterations
    data_img = [image, 0, [0, 0]] # image data   
    data_psf = [psf, 0, [0, 0]] # psf data
    
    # create indexes taking into account subsampling
    idx = [np.tile(np.arange(0,image.shape[0]), (subsmpl,1)).flatten(1),
            np.tile(np.arange(0,image.shape[1]), (subsmpl,1)).flatten(1)]
    idx1 = [np.tile(np.arange(0,psf.shape[0]), (subsmpl,1)).flatten(1),
            np.tile(np.arange(0,psf.shape[1]), (subsmpl,1)).flatten(1)]
    
    if weight is None:
        weight = np.ones(image.shape) # can be input parameter
    # apply weight to image to exclude bad pixels or for flat-field correction
    image_wtd = np.maximum(weight*image, 0)   
    data_img[0] = data_img[0].take(idx[0], axis=0).take(idx[1], axis=1)
    data_psf[0] = data_psf[0].take(idx1[0], axis=0).take(idx1[1], axis=1)
    weight = weight.take(idx[0], axis=0).take(idx[1], axis=1)        
    
    if subsmpl !=1:
        vec = np.zeros(len(image.shape)*2, dtype=np.int)
        vec[np.arange(0,len(image.shape)*2,2)] = image.shape
        vec[vec==0] = subsmpl
    
    # iterations
    alpha_img = 0 # acceleration parameter
    alpha_psf = 0 # acceleration parameter    
    for k in range(num_iter):
        if k > 2:
            alpha_img = np.dot(data_img[2][0].T,data_img[2][1])\
                        /(np.dot(data_img[2][1].T,data_img[2][1]) + np.spacing(1))             
            alpha_img = max(min(alpha_img,1),0) # 0<alpha<1
            alpha_psf = np.dot(data_psf[2][0].T,data_psf[2][1])\
                        /(np.dot(data_psf[2][1].T,data_psf[2][1]) + np.spacing(1))             
            alpha_psf = max(min(alpha_psf,1),0) # 0<alpha<1
        
        # make the image and psf estimate for the next iteration and apply 
        # positivity constraint       
        estimate_img = np.maximum(data_img[0] + alpha_img*(data_img[0]\
                                  - data_img[1]), 0)
        estimate_psf = np.maximum(data_psf[0] + alpha_psf*(data_psf[0]\
                                  - data_psf[1]), 0)
        # normalize psf
        estimate_psf = estimate_psf/(np.sum(estimate_psf)\
                       + (np.sum(estimate_psf)==0)*np.spacing(1)) 
        
        # calculate otf from psf with the same size as image
        otf = psf2otf(estimate_psf, np.array(image.shape)*subsmpl)
        
        # construct the expected image from the estimate         
        reblurred = np.real(ifftn(otf*fftn(estimate_img)))                
        
        # If subsmpl is not 1, bin reblurred back to original image size by 
        # calculating mean
        if subsmpl !=1:        
            reblurred = reblurred.reshape(vec)
            for i in np.arange(1,len(image.shape)*2,2)[::-1]:
                reblurred =reblurred.mean(axis=i)            
        
        reblurred[reblurred==0] = np.spacing(1)
        
        # calculate the ratio of the measured image to the expected image        
        ratio = image_wtd/reblurred + np.spacing(1)
        ratio = ratio.take(idx[0], axis=0).take(idx[1], axis=1)
        
        # determine next image estimate and apply positivity constraint       
        data_img[1] = data_img[0]        
        h1 = psf2otf(data_psf[0], np.array(image.shape)*subsmpl)
        # normalizing constant    
        norm_const1 = np.real(ifftn(h1.conj()*fftn(weight)))\
                      + np.sqrt(np.spacing(1))
        data_img[0] = np.maximum(estimate_img*np.real(ifftn(h1.conj()\
                      *fftn(ratio)))/norm_const1, 0)
        data_img[2] = [np.array([np.ravel(data_img[0] - estimate_img,
                                order='F')]).T,data_img[2][0]]

        # determine next psf estimate and apply positivity constraint       
        data_psf[1] = data_psf[0]        
        h2 = fftn(data_img[1])
        # normalizing constant    
        norm_const2 = otf2psf(h2.conj()*fftn(weight), np.array(psf.shape)\
                              *subsmpl) + np.sqrt(np.spacing(1))
        data_psf[0] = np.maximum(estimate_psf*otf2psf(h2.conj()*fftn(ratio),\
                                 np.array(psf.shape)*subsmpl)/norm_const2, 0)
        data_psf[0] = data_psf[0]/(np.sum(data_psf[0])\
                       + (np.sum(data_psf[0])==0)*np.spacing(1))         
        data_psf[2] = [np.array([np.ravel(data_psf[0] - estimate_psf,
                                order='F')]).T,data_psf[2][0]]        
    return data_img[0], data_psf[0]
    
        

        
        
        
        
        
        
        
        
        
        
        
        