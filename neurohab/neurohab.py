# -*- coding: utf-8 -*-
"""
@author: Federico Calesella
         Psychiatry and Clinical Psychobiology Unit, Division of Neuroscience, 
         IRCCS San Raffaele Scientific Institute, Milan, Italy
"""

import os
import numpy as np
import nibabel as nib
from scipy import stats

###############################################################################

class BrainHabituation():
    
    def __init__(self, subjects, conditions, rois, tens=None):
        
        """
        Initialize the BrainHabituation object.
        Input:
            subjects: a list containing the number of the subjects to be analyzed
            conditions: a list containing the condition to which each block/scan 
                belongs
            rois: a list containing the number of the seed/region of interest 
                (ROI) to be included
            tens: the number of digits that make up the subject, condition and 
                source numbers. If no value is provided, tens will be based on
                the maximum number of digits that make up the maximum between 
                the subject numbers, the number of blocks/scans, and the
                seed/ROI numbers
        """
        
        self.subj = subjects
        self.cond = conditions
        self.ucond = list(set(self.cond))
        self.rois = rois
        if tens is  None:
            nsubj = len(subjects)
            nblock = len(conditions)
            nroi = len(rois)
            mv = max(nsubj, nblock, nroi)
            self.tens = int(np.ceil(np.log10(mv)))
        else:
            self.tens = tens
            
###############################################################################

    def file_find(self, path):
        
        """
        Create a nested list with the files that must be loaded organized
        following the condition number, the ROI and the subject.
        Input:
            path: directory containing the input files
        Output:
            condition_list: a nested list containing the path of the files on 
                which the analyses will be performed.
        """
        
        files = [os.path.join(path, filename) for filename in os.listdir(path) 
                 if filename.startswith("BETA")]     
        
        condition_list = list()
        
        for condition in self.ucond:
            blocks = [n for n, b in enumerate(self.cond) if b == condition]
            condition_name = ['Condition' + f'{block+1:}'.zfill(self.tens) 
                              for block in blocks]
            condition_files = [[file for file in files if cn in file] 
                               for cn in condition_name]
            roi_list = list()
                
            for roi in self.rois:
                roi_name = 'Source' + f'{roi:}'.zfill(self.tens)
                roi_files = [[file for file in block_files if roi_name in file] for block_files in condition_files]
                subject_list = list()
                
                for subject in self.subj:
                    subject_name = 'Subject' + f'{subject:}'.zfill(self.tens)
                    subject_files = [[file for file in block_files if subject_name in file] for block_files in roi_files]
                    
                    subject_list.append(subject_files)
                roi_list.append(subject_list)
            condition_list.append(roi_list)
            
        return condition_list
    
###############################################################################
    
    def reg(self, images, nan=False):
        
        """
        Compute the voxel-wise habituation following the Regression (REG)
        method (Plichta et al., 2014).
        Input:
            images: a nested list with the files that must be loaded organized
                following the condition number, the ROI and the subject
            nan: boolean defining if nan values should be replaced with zeros.
                Nan values happen to be produced when regression of 0 on 0 is
                computed (in brain images this will be the case for the 
                background)
        Output:
            condition_list: a nested list with the habituation maps organized
                following the condition number, the the ROI and the subject. 
                One map per subject will be produced
        """
        
        condition_list = list()
        for condition in images:
            roi_list = list()
            for roi in condition:
                slope_list = list()
                intercept_list = list()
                for subject in roi:
                    img = [nib.load(image[0]) for image in subject]
                    vim = [np.reshape(image.get_fdata(), np.prod(image.shape)) 
                           for image in img]
                    vim = np.array(vim)
                    slope, intercept = self.regress_voxel(vim)
                    slope_list.append(slope)
                    intercept_list.append(intercept)
                    
                b = np.array(slope_list)
                a = np.array(intercept_list)
                c = self.compute_c(b, a)
                ahat = np.mean(a, axis=0)
                ab = b - c * (a - ahat)
                if nan:
                    ab[np.isnan(ab)] = 0
                ab = [ab[subj] for subj in range(ab.shape[0])]
                roi_list.append(ab)
                
            condition_list.append(roi_list)
            
        return condition_list
    
###############################################################################
                    
    def regress_voxel(self, data):
        
        """
        Perform linear regression over the blocks for each voxel.
        Input:
            data: numpy 2-D array with each block on the rows and the voxels 
                on the columns
        Output:
            slope: slope of the regression fit for each voxel
            intercept: intercept of the regression fit for each voxel
        """
        
        nblock, nvoxel = data.shape
        slope = np.zeros(nvoxel)
        intercept = np.zeros(nvoxel)
        for voxel in range(nvoxel):
            x = np.log(np.linspace(1, nblock, nblock))
            y = data[:, voxel]
            slope[voxel], intercept[voxel], _, _, _ = stats.linregress(x, y)
            
        return slope, intercept
    
###############################################################################
    
    def compute_c(self, b, a):
        
        """
        Compute the c parameter, by regressing the b parameters on the a 
        parameters across subjects (Plichta et al., 2014), for each voxel.
        Input:
            b: slope of the regression fit for each subject across blocks 
                (see the "regress_voxel" method)
            a: intercept of the regression fit for each subject across blocks 
                (see the "regress_voxel" method)
        Output:
            c: slope of the regression fit of b on a across subjects, for each
            voxel
        """
        
        nsubject, nvoxel = b.shape
        c = np.zeros(nvoxel)
        for voxel in range(nvoxel):
            x = a[:, voxel]
            y = b[:, voxel]
            if len(np.unique(x)) == 1:
                c[voxel] = np.nan
            else:
                c[voxel], _, _, _, _ = stats.linregress(x, y)
            
        return c
    
###############################################################################
    
    def fml(self, images):
        
        """
        Compute the voxel-wise habituation following the First-minus-Last (FmL)
        method (Plichta et al., 2014).
        Input:
            images: a nested list with the files that must be loaded organized
                following the condition number, the ROI and the subject
        Output:
            condition_list: a nested list with the habituation maps organized
                following the condition number, the the ROI and the subject. 
                One map per subject will be produced
        """
        
        condition_list = list()
        for condition in images:
            roi_list = list()
            for roi in condition:
                subject_list = list()
                for subject in roi:
                    img = [nib.load(image[0]) for image in subject]
                    vim = [np.reshape(image.get_fdata(), np.prod(image.shape)) 
                           for image in img]
                    vim = np.array(vim)
                    fl = vim[0, :] - vim[-1, :]
                    subject_list.append(fl)
                    
                roi_list.append(subject_list)
                
            condition_list.append(roi_list)
            
        return condition_list
    
###############################################################################
    
    def save_images(self, path, images, shape, affine):
        
        """
        Save the habituation maps.
        Input:
            path: directory where files must be saved
            images: a nested list with the habituation maps organized
                following the condition number, the the ROI and the subject
            shape: the shape of the original images
            affine: the affine matrix of the original images
        """
        
        for nc, condition in enumerate(images):
            for nr, roi in enumerate(condition):
                for ns, subject in enumerate(roi):
                    img = np.reshape(subject, shape)
                    nifti = nib.Nifti1Image(img, affine)
                    prefix = 'HAB'
                    subject_name = 'Subject' + f'{self.subj[ns]:}'.zfill(self.tens)
                    roi_name = 'Source' + f'{self.rois[nr]:}'.zfill(self.tens)
                    condition_name = 'Condition' + f'{self.ucond[nc]:}'.zfill(self.tens)
                    filename = (prefix + '_' + subject_name + '_' + 
                                condition_name + '_' + roi_name)
                    file = os.path.join(path, filename)
                    nib.save(nifti, file)