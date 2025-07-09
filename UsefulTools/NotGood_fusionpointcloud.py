import numpy as np
import open3d as o3d
from scipy.spatial.transform import Rotation as R

def load_extrinsics(image_path):
    extrinsics = {}
    with open(image_path, "r") as f:
        for line in f:
            if line.startswith("#") or len(line.strip()) == 0:
                continue
            parts = line.strip().split()
            img_name = parts[9]
            qx, qy, qz, qw = map(float, parts[1:5])
            tx, ty, tz = map(float, parts[5:8])

            # Quaternion -> matrice de rotation
            rot = R.from_quat([qx, qy, qz, qw]).as_matrix()  # Attention ordre : x y z w

            # Matrice 4x4
            extrinsic = np.eye(4)
            extrinsic[:3, :3] = rot
            extrinsic[:3, 3] = [tx, ty, tz]

            extrinsics[img_name] = extrinsic
    return extrinsics

# Exemple : charger toutes les extrinsèques
extrinsics_dict = load_extrinsics("/home/hmc/gaussian-splatting/GS_projects/data/FVV/sparse/0/images.txt")

# Charger tes point clouds
pcd0 = o3d.io.read_point_cloud("cloud_cam0.ply")
pcd1 = o3d.io.read_point_cloud("cloud_cam1.ply")
pcd2 = o3d.io.read_point_cloud("cloud_cam2.ply")
pcd3 = o3d.io.read_point_cloud("cloud_cam3.ply")

# Appliquer les transformations
pcd0.transform(extrinsics_dict["CalibCam00.png"])
pcd1.transform(extrinsics_dict["CalibCam01.png"])
pcd2.transform(extrinsics_dict["CalibCam02.png"])
pcd3.transform(extrinsics_dict["CalibCam03.png"])

# Fusionner
pcd_combined = pcd0 + pcd1 + pcd2 + pcd3

# Sauvegarder
o3d.io.write_point_cloud("cloud_fusion.ply", pcd_combined)
o3d.visualization.draw_geometries([pcd_combined])
