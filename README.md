# NeuroHab
 Voxelwise brain habituation

## Table of Contents
1. [Project Overview](#Project_Overview)
2. [Installation and Data Requirements](#Installation)
3. [Usage](#Usage)
   1. [Initialize the ```BrainHabituation``` Class](#Initialize)
   2. [Find the Needed Files](#Find_files)
   3. [Estimate Habituation](#Habituation)
   4. [Save the Results](#Save)
5. [Example](#Example)
6. [Notes: Shape and Affine Matrix](#Notes)
7. [References](#References)

## 1. Project Overview <a name="Project_Overview"></a>
The code was conceived to perform voxelwise habituation analysis on functional magnetic resonance imaging (fMRI) data. \
Two measures of habituation were implemented, based on Plichta et al. (2014):
- First-minus-Last (FmL)
- Regression (REG)

The code was run on blood oxygenation level dependent (BOLD) signal maps. Furthermore, it handles both block designs with one or multiple conditions and designs with no blocks nor conditions (e.g., resting state). Finally, also seed based funcitonal connectivity (FC) maps can be given as input.

## 2. Installation and Data Requirements <a name="Installation"></a>
The installation with pip is supported:
```
pip install neurohab
```

The code assumes the data to be NIfTI images, starting with the string "BETA" and organized in:
- subjects, defined as "Subject01"
- blocks/scans, defined as "Condition01"
- seeds/regions of interest (ROIs), defined as "Source01"

As a consequence an exemplary file name might be "BETA_Subject01_Condition01_Source01" for subject one, block/scan one and seed/ROI one. If no condition and/or no source are included in the experimental design, they will just be constant ("Condition01_Source01") across subjects. Please note that the number of digits indicating the subjects, conditions, and ROIs must be set according to the global maximum value across the three fields. For instance, if the sample is composed by 50 subjects with no blocks and seeds, then the file names will be "BETA_Subject01_Condition01_Source01" ... "BETA_Subject50_Condition01_Source01". However, if 100 seeds were present, then the file names will be "BETA_Subject001_Condition001_Source001" ... "BETA_Subject050_Condition001_Source100".

## 3. Usage <a name="Usage"></a>

### i. Initialize the ```BrainHabituation``` class <a name="Initialize"></a>
The ```BrainHabituation``` class requires 3 mandatory and 1 optional parameters to be set as input:
```python 
BrainHabituation(subjects, conditions, rois, tens=None)
``` 
*Parameters*:
- **subjects**: a list containing the numbers of the subjects that will be analyzed 
- **conditions**: a list containing the condition to which each block/scan belongs
- **rois**: a list containing the number of the seed/ROI to be included
- **tens** (optional): the number of digits that make up the subject, condition, and source numbers (e.g., if there are 100 subjects, then the subjects' names will be "BETA_Subject001_Condition001_Source001", and so tens=3). If no value is provided, tens will be based on the maximum number of digits across the subject numbers, the number of blocks/scans, and the seed/ROI numbers.

### ii. Find the Needed Files <a name="Find_files"></a>
The ```find_files``` method allows to create a nested list containing the full path of all the needed NIfTI images. The files are still not loaded for memory saving.
```python 
find_files(path)
``` 
*Parameters*:
- **path**: a string indicating the full path to the directory which contains the input files.

*Outputs*:
- **condition_list**: a nested list containing the path of the files on which the analyses will be performed. The list is nested in the following order: conditions, ROIs, and subjects.

### iii. Estimate Habituation <a name="Habituation"></a>
Two methods can be used to estimate the voxelwise habituation parameters: ```reg``` and ```fml```.\
The ```reg``` method computes voxelwise habituation using the REG method (i.e., based on regression across blocks/scans).
```python 
reg(images, nan=False)
``` 
*Parameters*:
- **images**: a nested list with the full path of the files that must be loaded, organized following the conditions, ROIs and subjects order.
- **nan** (optional): boolean defining if NaN values should be replaced with zeros. NaN values happen to be produced when regression of 0 on 0 is computed (in brain images this will be the case for the background).

*Outputs*:
- **condition_list**: a nested list of numpy.arrays, which will contain the habituation maps for each subject. The list will be organized following the order of the input list (conditions, ROIs, and subjects).

The ```fml``` method computes voxelwise habituation using the FmL method.
```python 
fml(images)
``` 
*Parameters*:
- **images**: a nested list with the full path of the files that must be loaded, organized following the conditions, ROIs and subjects order.

*Outputs*:
- **condition_list**: a nested list of numpy.arrays, which will contain the habituation maps for each subject. The list will be organized following the order of the input list (conditions, ROIs, and subjects).

### iv. Save the Results <a name="Save"></a>
The habituation maps can be saved in a specified directory using the ```save_images``` method. The output files will start with the "HAB_" prefix.
```python 
save_images(path, images, shape, affine)
``` 
*Parameters*:
- **path**: full path of the directory where to save the files
- **images**: a nested list of numpy.arrays, containing the habituation maps for each subject. The list must be nested following the order: conditions, ROIs, and subjects.
- **shape**: the shape of the original images (i.e., the dimension of the arrays of the images - see Section 5). It is assumed that all the images have the same shape. 
- **affine**: the affine matrix (see Section 5) of the original images. It is assumed that all the images have the same affine matrix.

## 4. Example <a name="Example"></a>
An example on how to run the code and estimate the habituation parameters is provided in the ```example.py``` file (it can also be used as a run-file). In this file, the following edits are required:
- line 15: define the full path of the directory where the input files are stored
- line 17: define the directory where the habituation maps will be saved
- lines 19-25: the first and last subject
- line 28: the eventual condition of each block/scan (if no condition exists, create a list of ones with the same length of the blocks/scans number)
- line 30: the eventual seeds (if no seed exists, the list will contain only a number, matching the "Source" field in the file names)
- line 33: the tens parameter
- line 35: the shape of the images (see Section 5)
- line 37: the affine matrix of the images (see Section 5)

In this case, 106 subjects performed a face-matching task, with shape-matching as a control condition. After preprocessing, each subject resulted with voxelwise BOLD maps in 4 face-matching blocks and 5 shape-matching blocks (i.e., each subject had 9 BOLD maps devided in 2 conditions). Consequently, at lines 19-25 106 subjects were set, at line 28 the conditions were specified for each block (i.e., shape=2; face=1), at line 30 ROIs were defined (only a 1 was inserted as we had no FC seeds), and at line 33 the tens parameter was also defined (even though its specification is optional). Here tens is 3 because we had 9 blocks, no ROI, and 106 subjects, so the maximum number is 106, which is composed by 3 digits. The shape and the affine matrix were also defined.

## 5. Notes: shape and affine matrix <a name="Notes"></a>
In order to assess the shape of the array containing the images and the affine matrx, the NiBabel package can be used. Please refer to the [NiBabel page](https://nipy.org/nibabel/) and its [Getting Started page](https://nipy.org/nibabel/gettingstarted.html). Here an example is provided to assess these parameters with NiBabel. To import the package and load an image, just edit the input string at the second line with a valid full path to a NIfTI image.
```python 
import nibabel as nib
img = nib.load('example_filename')

print('Image shape:\n', img.shape)
print('Image affine matrix:\n', img.affine)
```
The same commands can be run with multpile images in order to assess if the shape and affine matrix are the same across the images.

## References <a name="References"></a>
Plichta, M. M., Grimm, O., Morgen, K., Mier, D., Sauer, C., Haddad, L., ... & Meyer-Lindenberg, A. (2014). Amygdala habituation: a reliable fMRI phenotype. NeuroImage, 103, 383-390.
