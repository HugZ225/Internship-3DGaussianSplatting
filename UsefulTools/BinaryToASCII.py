
import open3d as o3d

# Charger le fichier PLY (binaire ou ASCII)
pcd = o3d.io.read_point_cloud("/home/hmc/gaussian-splatting/GS_projects/data/Desert/sparse/0/points3D.ply")

# Sauvegarder en ASCII
o3d.io.write_point_cloud("/home/hmc/gaussian-splatting/GS_projects/data/Desert/sparse/0/point_cloud_ascii.ply", pcd, write_ascii=True)

print("Conversion terminée.")
