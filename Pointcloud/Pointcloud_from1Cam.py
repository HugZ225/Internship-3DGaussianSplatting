import open3d as o3d
import numpy as np
import cv2

# Charger avec OpenCV
color_cv = cv2.imread("/home/hmc/gaussian-splatting/GS_projects/data/Home/images/Cam4.png", cv2.IMREAD_COLOR)
color_cv = cv2.cvtColor(color_cv, cv2.COLOR_BGR2RGB)  # Convertir BGR -> RGB

depth_cv = cv2.imread("/home/hmc/gaussian-splatting/GS_projects/data/Home/depths/Cam4.png", cv2.IMREAD_UNCHANGED)

# Convertir en open3d Image
color_o3d = o3d.geometry.Image(color_cv)
depth_o3d = o3d.geometry.Image(depth_cv)

# Charger la caméra 0 (intrinsèques)
with open("/home/hmc/gaussian-splatting/GS_projects/data/Home/sparse/0/cameras.txt", "r") as f:
    for line in f:
        if line.startswith("0 "):
            parts = line.strip().split()
            fx = float(parts[4])
            cx = float(parts[5])
            cy = float(parts[6])
            width = int(parts[2])
            height = int(parts[3])
            break

intrinsic = o3d.camera.PinholeCameraIntrinsic(width, height, fx, fx, cx, cy)

# Créer l'image RGBD
rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
    color_o3d,
    depth_o3d,
    depth_scale=1000.0,
    depth_trunc=1000,
    convert_rgb_to_intensity=False
)

print("RGBD image créée.")

# Créer le point cloud
pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, intrinsic)

print(f"Point cloud créé avec {len(pcd.points)} points.")

# Visualiser
o3d.visualization.draw_geometries([pcd])

o3d.io.write_point_cloud("cloud.ply", pcd)
print("Nuage sauvegardé sous cloud.ply")