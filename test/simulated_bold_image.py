# -*- coding: utf-8 -*-
"""
@author: Federico Calesella
         Psychiatry and Clinical Psychobiology Unit, Division of Neuroscience, 
         IRCCS San Raffaele Scientific Institute, Milan, Italy
"""

import os
import numpy as np
import nibabel as nib
from nilearn import plotting, image
from nilearn.datasets import load_mni152_template
from nilearn.masking import compute_brain_mask

# Define how many subjects to simulate
n_subjects = 5
# Define the condition to which each block/scan belongs
conditions = [2,2,2,2,2,1,1,1,1]
# Define the number of the seed/region of interest (ROI) to be included
rois = [1]
# Define the number of digits that make up the subject, condition and source 
# numbers.
tens = 3

# Get the directory of the script
script_directory = os.path.dirname(os.path.realpath(__file__))
ucond = list(set(conditions))
for condition in (ucond):
    blocks = [n for n, b in enumerate(conditions) if b == condition]
    for block in blocks:
        for roi in (rois):
            for subject in range(1, n_subjects+1):
                
                # Load the MNI152 template
                template = load_mni152_template()
                
                # Compute the brain mask from the template
                brain_mask = compute_brain_mask(template)
                
                # Convert the mask to a numpy array
                mask_data = brain_mask.get_fdata().astype(bool)
                
                # Initialize random BOLD signal data within the brain mask
                bold_data = np.zeros_like(mask_data, dtype=float)
                bold_data[mask_data] = np.random.rand(mask_data.sum())
                
                # Create a new Nifti1Image with the simulated data
                bold_img = nib.Nifti1Image(bold_data, template.affine)
                
                subject_name = 'Subject' + f'{subject:}'.zfill(tens)
                roi_name = 'Source' + f'{roi:}'.zfill(tens)
                condition_name = 'Condition' + f'{block+1:}'.zfill(tens)
                filename = ('BETA_' + subject_name + '_' + condition_name + '_' + roi_name + '.nii')
                file = os.path.join(script_directory, 'test_data', filename)
                
                nib.save(bold_img, file)

