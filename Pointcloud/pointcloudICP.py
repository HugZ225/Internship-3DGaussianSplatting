import open3d as o3d
import numpy as np
import cv2
#quelques petites duplication pas aligné mais pas les 9 
def load_intrinsics(cam_id, cameras_txt_path):
    with open(cameras_txt_path, "r") as f:
        for line in f:
            if line.startswith(f"{cam_id} "):
                parts = line.strip().split()
                width = int(parts[2])
                height = int(parts[3])
                fx = float(parts[4])
                cx = float(parts[5])
                cy = float(parts[6])
                return o3d.camera.PinholeCameraIntrinsic(width, height, fx, fx, cx, cy)
    raise ValueError(f"Camera {cam_id} intrinsics not found.")

def create_point_cloud(color_path, depth_path, intrinsic):
    color_cv = cv2.imread(color_path, cv2.IMREAD_COLOR)
    color_cv = cv2.cvtColor(color_cv, cv2.COLOR_BGR2RGB)

    depth_cv = cv2.imread(depth_path, cv2.IMREAD_UNCHANGED)

    color_o3d = o3d.geometry.Image(color_cv)
    depth_o3d = o3d.geometry.Image(depth_cv)

    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
        color_o3d,
        depth_o3d,
        depth_scale=1000.0,
        depth_trunc=10000.0,
        convert_rgb_to_intensity=False
    )

    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_image, intrinsic)
    return pcd

# Chemins
base_path = "/home/hmc/gaussian-splatting/GS_projects/data/Home/"
cameras_txt_path = base_path + "sparse/0/cameras.txt"

cam_ids = [0,1,2,3]

# Charger les nuages sans pose (sans extrinsics)
pcds = []
for cam_id in cam_ids:
    color_path = f"{base_path}/images/Cam{cam_id}.png"
    depth_path = f"{base_path}/depths/Cam{cam_id}.png"
    intrinsic = load_intrinsics(cam_id, cameras_txt_path)
    pcd = create_point_cloud(color_path, depth_path, intrinsic)
    print(f"Point cloud caméra {cam_id} : {len(pcd.points)} points.")
    pcds.append(pcd)

# Aligner les nuages avec ICP sur la première caméra (cam0)
# pcd_aligned = pcds[0]
# for i in range(1, len(pcds)):
#     print(f"Alignement ICP caméra {i} vers caméra 0 ...")
#     threshold = 0.05  # ajuster selon l'échelle de ton nuage
#     trans_init = np.identity(4)
#     reg_p2p = o3d.pipelines.registration.registration_icp(
#         pcds[i], pcd_aligned, threshold, trans_init,
#         o3d.pipelines.registration.TransformationEstimationPointToPoint()
#     )
#     print(f"Transformation caméra {i} :\n", reg_p2p.transformation)
#     pcds[i].transform(reg_p2p.transformation)

# Fusionner tous les nuages alignés
merged_pcd = pcds[0]
for pcd in pcds[1:]:
    merged_pcd += pcd

print(f"Nuage fusionné : {len(merged_pcd.points)} points.")

# Visualiser
o3d.visualization.draw_geometries([merged_pcd])

# Sauvegarder
o3d.io.write_point_cloud("merged_cloud_icp.ply", merged_pcd)
print("Nuage fusionné sauvegardé sous merged_cloud_icp.ply.")
