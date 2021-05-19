# -*- coding: utf-8 -*-
"""
@author: Federico Calesella
         Psychiatry and Clinical Psychobiology Unit, Division of Neuroscience, 
         IRCCS San Raffaele Scientific Institute, Milan, Italy
"""

# Make the required imports
import numpy as np
from neurohab import BrainHabituation

# Define the input directory
input_path = 'Input_directory'
# Define the output directory
output_path = 'Output_directory'
# Define the number of the first subject
first_subject = 1
# Define the number of the last subject
last_subject = 106
# If the subjects to be analyzed are not sequential, comment out the lines: 19,
# 21, 43, and 45. Then uncomment the line 25, and manually fill the list
# with the the subject numbers
# subjects = []

# Define the condition to which each block/scan belongs
conditions = [2,2,2,2,2,1,1,1,1]
# Define the number of the seed/region of interest (ROI) to be included
rois = [1, 2]
# Define the number of digits that make up the subject, condition and source 
# numbers.
tens = 3
# Define the shape of the data array extracted from the nifti images
shape = [91, 109, 91]
# Define the affine matrix of the nifti images
affine = np.array([[  -2.,    0.,    0.,   90.],
                   [   0.,    2.,    0., -126.],
                   [   0.,    0.,    2.,  -72.],
                   [   0.,    0.,    0.,    1.]])

# Find out how many subjects will be analyzed
nsubjects = last_subject - first_subject + 1
# Create a list with the subject numbers from the first to the last (included)
subjects = list(np.linspace(first_subject, last_subject, nsubjects, dtype=int))

# Initialize the BrainHabituation object
brhab = BrainHabituation(subjects, conditions, rois, tens)
# Find the files that must be loaded for the analyses
images = brhab.file_find(input_path)
# Perform the habituation analysis. Keep brab.reg to use the REG
# method or replace it with brab.fml to use the FmL method
hab = brhab.reg(images)
# Save the habituation maps
brhab.save_images(output_path, hab, shape, affine)