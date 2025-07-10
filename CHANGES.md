# CHANGES 

Here you can find the modifications and additions I made to the original GitHub repository.  
I made these modifications during my internship at the GTI lab, ETSIT-UPM Madrid, from April to August 2025.  
In this document, I provide explanations of several methods, accompanied by examples and insights drawn from my experience.

## Training with a PLY 

To train, we need the COLMAP files: cameras.bin, images.bin, and points3D.bin.  
I modified the colmap_loader.py and dataset_readers.py files to enable training with a points3D.ply file instead of a .bin file (I kept a backup of the original versions).

## Pointcloud 

I made two functions to generate pointcloud (.ply files) from images and depths of the dataset.

## Useful Tools
