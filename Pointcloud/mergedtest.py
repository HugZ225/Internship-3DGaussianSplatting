import open3d as o3d
import numpy as np

"""mix la liste de pointcloud sans externincs et decuple 9fois les trucs cloud_global_clean"""
# Liste des noms de tes point clouds
point_cloud_files = [
    "/home/hmc/gaussian-splatting/GS_projects/data/Home/pointclouds_all_cameras/cloud_cam0.ply",
    "/home/hmc/gaussian-splatting/GS_projects/data/Home/pointclouds_all_cameras/cloud_cam1.ply",
    "/home/hmc/gaussian-splatting/GS_projects/data/Home/pointclouds_all_cameras/cloud_cam2.ply",
    "/home/hmc/gaussian-splatting/GS_projects/data/Home/pointclouds_all_cameras/cloud_cam3.ply",
    "/home/hmc/gaussian-splatting/GS_projects/data/Home/pointclouds_all_cameras/cloud_cam4.ply",
    "/home/hmc/gaussian-splatting/GS_projects/data/Home/pointclouds_all_cameras/cloud_cam5.ply",
    "/home/hmc/gaussian-splatting/GS_projects/data/Home/pointclouds_all_cameras/cloud_cam6.ply",
    "/home/hmc/gaussian-splatting/GS_projects/data/Home/pointclouds_all_cameras/cloud_cam7.ply",
    "/home/hmc/gaussian-splatting/GS_projects/data/Home/pointclouds_all_cameras/cloud_cam8.ply",
]

# Générer autant de matrices identité qu'il y a de fichiers
transformations = [np.eye(4) for _ in point_cloud_files]

# Création d'un nuage de points global vide
global_pcd = o3d.geometry.PointCloud()

# Boucle sur les fichiers
for file, T in zip(point_cloud_files, transformations):
    print(f"Lecture et transformation de {file}")
    pcd = o3d.io.read_point_cloud(file)
    pcd.transform(T)
    global_pcd += pcd

print(f"Point cloud combiné : {len(global_pcd.points)} points")

# Downsampling : fusionner les points trop proches
voxel_size = 0.005  # Ajuste selon ta scène
global_pcd_down = global_pcd.voxel_down_sample(voxel_size=voxel_size)
print(f"Après downsampling : {len(global_pcd_down.points)} points")

# Nettoyage : suppression des points isolés
cl, ind = global_pcd_down.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
clean_pcd = global_pcd_down.select_by_index(ind)
print(f"Après nettoyage : {len(clean_pcd.points)} points")

# Sauvegarde et affichage du nuage final
o3d.io.write_point_cloud("cloud_global_clean.ply", clean_pcd)
o3d.visualization.draw_geometries([clean_pcd])
