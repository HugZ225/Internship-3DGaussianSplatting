# CHANGES 

Here you can find the modifications and additions I made to the original GitHub repository.  
I made these modifications during my internship at the GTI lab, ETSIT-UPM Madrid, from April to August 2025.  
In this document, I provide explanations of several methods, accompanied by examples and insights drawn from my experience.

## Training with a PLY 

To train a dataset, we need the COLMAP files: cameras.bin, images.bin, and points3D.bin.  
I modified the *colmap_loader.py* and *dataset_readers.py* files to enable training with a points3D.ply file instead of a .bin file (I kept a backup of the original versions).

## Pointcloud 

I made two functions to generate point clouds (.ply files) from the images and depth maps of the dataset:  
*Pointcloud_from1Cam.py*: generates a point cloud from a single camera point of view.  
*FVVpointcloud.py*: generates a point cloud by combining information from all the cameras.

## Useful Tools

The COLMAP files need to have a special format, for example the type of the cameras has to be PINHOLE, and I made function to convert others types of cameras (SIMPLE_PINHOLE, OPEN_CV) into pinhole. 

All this functions are in the Useful Tools folder 

## Visualization 

The remote viewer and real-time visualization didn’t work on my computer.

To visualize the results, I first used Blender with  this GitHub repository (https://github.com/Kiri-Innovation/3dgs-render-blender-addon/blob/main/README.md) and followed this tutorial (https://www.youtube.com/watch?v=WUL73wQDtcE&t=634s).

Later, someone recommended this web viewer (https://antimatter15.com/splat/) to quickly preview the splats with better performance.

## Dataset 

## Results 
