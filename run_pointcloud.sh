#!/bin/bash
conda activate Open3D
LD_LIBRARY_PATH=$(conda info --base)/envs/Open3D/lib:$LD_LIBRARY_PATH python pointcloud2.py
