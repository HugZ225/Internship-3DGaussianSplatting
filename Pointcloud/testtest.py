import open3d as o3d
import numpy as np
import cv2
import os
#duplication de 9 singes sans extenrsics 
def load_intrinsics(camera_file, cam_id):
    with open(camera_file, "r") as f:
        for line in f:
            if line.startswith(f"{cam_id} "):
                parts = line.strip().split()
                width = int(parts[2])
                height = int(parts[3])
                fx = float(parts[4])
                cx = float(parts[5])
                cy = float(parts[6])
                return o3d.camera.PinholeCameraIntrinsic(width, height, fx, fx, cx, cy)
    raise RuntimeError(f"Intrinsics for camera {cam_id} not found")

def create_pointcloud(color_path, depth_path, intrinsic):
    print(f"Chargement de {color_path}")
    print(f"Chargement de {depth_path}")
    
    if not (os.path.exists(color_path) and os.path.exists(depth_path)):
        print("Fichiers introuvables, saut de cette image.")
        return None

    color_cv = cv2.imread(color_path, cv2.IMREAD_COLOR)
    if color_cv is None:
        print(f"Erreur lecture couleur : {color_path}")
        return None
    color_cv = cv2.cvtColor(color_cv, cv2.COLOR_BGR2RGB)

    depth_cv = cv2.imread(depth_path, cv2.IMREAD_UNCHANGED)
    if depth_cv is None:
        print(f"Erreur lecture profondeur : {depth_path}")
        return None

    color_o3d = o3d.geometry.Image(color_cv)
    depth_o3d = o3d.geometry.Image(depth_cv)

    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
        color_o3d,
        depth_o3d,
        depth_scale=1000.0,
        depth_trunc=1000,
        convert_rgb_to_intensity=False
    )

    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, intrinsic)
    return pcd

# Paramètres
base_path = "/home/hmc/gaussian-splatting/GS_projects/data/Home"
color_folder = os.path.join(base_path, "images")
depth_folder = os.path.join(base_path, "depths")
camera_file = os.path.join(base_path, "sparse/0/cameras.txt")

# Disons que tu as 12 caméras (0 à 11)
camera_ids = list(range(12))

# Charger les intrinsics pour toutes les caméras
intrinsics = {}
for cam_id in camera_ids:
    try:
        intrinsics[cam_id] = load_intrinsics(camera_file, cam_id)
    except RuntimeError as e:
        print(e)

pcd_global = o3d.geometry.PointCloud()

for cam_id in camera_ids:
    color_path = os.path.join(color_folder, f"Cam{cam_id}.png")
    depth_path = os.path.join(depth_folder, f"Cam{cam_id}.png")

    print(f"Traitement cam {cam_id}")
    if cam_id not in intrinsics:
        print(f"Intrinsics manquants pour la cam {cam_id}, skip.")
        continue

    pcd = create_pointcloud(color_path, depth_path, intrinsics[cam_id])
    if pcd is None:
        continue

    # Tu peux appliquer une transformation ici si tu as la pose globale de chaque caméra
    # Par exemple : pcd.transform(T_cam_to_global[cam_id])
    # Sinon ils resteront dans le repère caméra, donc mal alignés

    pcd_global += pcd

print(f"Point cloud global fusionné contient {len(pcd_global.points)} points.")

# Nettoyage optionnel : enlever les doublons, etc.
pcd_global = pcd_global.voxel_down_sample(voxel_size=0.005)

# Sauvegarde finale
o3d.io.write_point_cloud("cloud_test_clean.ply", pcd_global)
print("Nuage global sauvegardé sous cloud_test_clean.ply")

# Affichage optionnel
o3d.visualization.draw_geometries([pcd_global])
