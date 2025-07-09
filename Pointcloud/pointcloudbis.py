def create_pointcloud(color_path, depth_path, camera_file, output_path):
    import open3d as o3d
    import numpy as np
    import cv2

    # Chargement images
    color_cv = cv2.imread(color_path, cv2.IMREAD_COLOR)
    color_cv = cv2.cvtColor(color_cv, cv2.COLOR_BGR2RGB)
    depth_cv = cv2.imread(depth_path, cv2.IMREAD_UNCHANGED)

    if color_cv.shape[:2] != depth_cv.shape:
        raise ValueError("Dimensions couleur et profondeur non compatibles.")

    color_o3d = o3d.geometry.Image(color_cv)
    depth_o3d = o3d.geometry.Image(depth_cv)

    # Intrinsèques
    with open(camera_file, "r") as f:
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

    # RGBD image
    depth_scale = 1000.0
    depth_trunc = 10000.0
    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
        color_o3d, depth_o3d, depth_scale=depth_scale, depth_trunc=depth_trunc, convert_rgb_to_intensity=False
    )

    # Point cloud
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, intrinsic)

    # Nettoyage
    pcd, _ = pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)

    # Visualisation
    o3d.visualization.draw_geometries([pcd])

    # Sauvegarde
    o3d.io.write_point_cloud(output_path, pcd)

    print(f"Point cloud créé avec {len(pcd.points)} points, sauvegardé sous {output_path}.")

# Exemple d'utilisation
create_pointcloud(
    "/home/hmc/gaussian-splatting/GS_projects/data/Desert/images/Cam0.png",
    "/home/hmc/gaussian-splatting/GS_projects/data/Desert/depths/Cam0.png",
    "/home/hmc/gaussian-splatting/GS_projects/data/Desert/sparse/0/cameras.txt",
    "cloud.ply"
)
