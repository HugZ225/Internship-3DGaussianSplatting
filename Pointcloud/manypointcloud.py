import open3d as o3d
import numpy as np
import cv2
import os
#crée plein de pointcloud
def load_camera_intrinsics(camera_id, cameras_txt_path):
    with open(cameras_txt_path, "r") as f:
        for line in f:
            if line.startswith(str(camera_id) + " "):
                parts = line.strip().split()
                fx = float(parts[4])
                cx = float(parts[5])
                cy = float(parts[6])
                width = int(parts[2])
                height = int(parts[3])
                return o3d.camera.PinholeCameraIntrinsic(width, height, fx, fx, cx, cy)
    raise ValueError(f"Camera {camera_id} not found in {cameras_txt_path}")

def generate_pointcloud_for_camera(camera_id, base_path, output_folder, depth_scale=1000.0, depth_trunc=1000):
    # Construire chemins des images couleur et profondeur
    color_path = os.path.join(base_path, "images", f"Cam{camera_id}.png")
    depth_path = os.path.join(base_path, "depths", f"Cam{camera_id}.png")
    cameras_txt_path = os.path.join(base_path, "sparse", "0", "cameras.txt")  # à adapter si nécessaire

    # Charger images
    color_cv = cv2.imread(color_path, cv2.IMREAD_COLOR)
    if color_cv is None:
        print(f"Erreur : couleur non trouvée pour caméra {camera_id} à {color_path}")
        return None
    color_cv = cv2.cvtColor(color_cv, cv2.COLOR_BGR2RGB)

    depth_cv = cv2.imread(depth_path, cv2.IMREAD_UNCHANGED)
    if depth_cv is None:
        print(f"Erreur : profondeur non trouvée pour caméra {camera_id} à {depth_path}")
        return None

    # Convertir en open3d images
    color_o3d = o3d.geometry.Image(color_cv)
    depth_o3d = o3d.geometry.Image(depth_cv)

    # Charger intrinsèques
    intrinsic = load_camera_intrinsics(camera_id, cameras_txt_path)

    # Créer image RGBD
    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
        color_o3d,
        depth_o3d,
        depth_scale=depth_scale,
        depth_trunc=depth_trunc,
        convert_rgb_to_intensity=False
    )

    # Créer point cloud
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, intrinsic)

    # Créer dossier de sortie s'il n'existe pas
    os.makedirs(output_folder, exist_ok=True)

    # Sauvegarder
    out_path = os.path.join(output_folder, f"cloud_cam{camera_id}.ply")
    o3d.io.write_point_cloud(out_path, pcd)
    print(f"Point cloud sauvegardé pour caméra {camera_id} sous {out_path}")

    return pcd


if __name__ == "__main__":
    base_path = "/home/hmc/gaussian-splatting/GS_projects/data/Home"
    output_folder = os.path.join(base_path, "pointclouds_all_cameras")

    # Liste des caméras à traiter
    cameras_to_process = [0,1,2,3,4,5,6,7,8,9]  # adapte selon tes données

    all_pcds = []
    for cam_id in cameras_to_process:
        pcd = generate_pointcloud_for_camera(cam_id, base_path, output_folder)
        if pcd is not None:
            all_pcds.append(pcd)

    print(f"{len(all_pcds)} point clouds générés.")
