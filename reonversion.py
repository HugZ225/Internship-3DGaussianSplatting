import open3d as o3d
import numpy as np

# Lecture de ton fichier existant
pcd = o3d.io.read_point_cloud("/home/hmc/gaussian-splatting/GS_projects/data/Desert/sparse/0/points3D.ply")

# Conversion explicite des points en float32 (au lieu de double)
points = np.asarray(pcd.points).astype(np.float32)
pcd.points = o3d.utility.Vector3dVector(points)

# Écriture du nouveau fichier en ASCII
o3d.io.write_point_cloud("points3D_fixed.ply", pcd, write_ascii=True)
