import open3d as o3d
import numpy as np
import cv2
from scipy.spatial.transform import Rotation as R

# utilise les extirnsics et renvoi des pointcloud séparé cloud_fusion_corrected
def load_extrinsics(image_path):
    extrinsics = {}
    with open(image_path, "r") as f:
        for line in f:
            if line.startswith("#") or len(line.strip()) == 0:
                continue
            parts = line.strip().split()
            img_name = parts[9]  # Nom image
            qw, qx, qy, qz = map(float, parts[1:5])
            tx, ty, tz = map(float, parts[5:8])

            rot = R.from_quat([qx, qy, qz, qw]).as_matrix()

            extrinsic = np.eye(4)
            extrinsic[:3, :3] = rot
            extrinsic[:3, 3] = [tx, ty, tz]

            # Inversion car souvent monde -> caméra dans Colmap
            #extrinsic = np.linalg.inv(extrinsic)

            extrinsics[img_name] = extrinsic
            print(f"{img_name}\n{extrinsic}\n")

    print(f"[INFO] Chargé {len(extrinsics)} matrices extrinsèques.")
    return extrinsics

def load_intrinsic(cam_id, camera_path):
    with open(camera_path, "r") as f:
        for line in f:
            if line.startswith(f"{cam_id*2} "):
                parts = line.strip().split()
                fx = float(parts[4])
                fy = float(parts[5])
                cx = float(parts[6])
                cy = float(parts[7])
                width = int(parts[2])
                height = int(parts[3])
                intrinsic = o3d.camera.PinholeCameraIntrinsic(width, height, fx, fy, cx, cy)
                print(intrinsic, fx, fy, cx, cy)
                return intrinsic
    raise ValueError(f"Caméra {cam_id} introuvable dans {camera_path}")

def create_pointcloud_for_camera(cam_id, extrinsics_dict, camera_path):
    color_path = f"/home/hmc/gaussian-splatting/GS_projects/data/Home/images/Cam{cam_id}.png"
    depth_path = f"/home/hmc/gaussian-splatting/GS_projects/data/Home/depths/Cam{cam_id}.png"

    color_cv = cv2.imread(color_path, cv2.IMREAD_COLOR)
    color_cv = cv2.cvtColor(color_cv, cv2.COLOR_BGR2RGB)
    depth_cv = cv2.imread(depth_path, cv2.IMREAD_UNCHANGED)

    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
        o3d.geometry.Image(color_cv),
        o3d.geometry.Image(depth_cv),
        depth_scale=1.0,
        depth_trunc=10000.0,
        convert_rgb_to_intensity=False
    )

    intrinsic = load_intrinsic(cam_id, camera_path)
    extrinsic = extrinsics_dict[f"Cam{cam_id}.png"]
    print(extrinsic)


    # Créer nuage de points
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(
        rgbd_image,
        intrinsic,
        extrinsic
    )

    # Appliquer extrinsic inverse (caméra vers monde)
#    extrinsic = extrinsics_dict[f"Cam{cam_id}.png"]
#    pcd.transform(extrinsic)

#     Repère de coordonnées pour chaque caméra
    frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.1)
    frame.transform(extrinsic)
    print(f"[INFO] Cam{cam_id}.ply number of points {len(pcd.points)}")
    return pcd, frame


def main():
    images_txt = "/home/hmc/gaussian-splatting/GS_projects/data/Home/sparse/0/images.txt"
    cameras_txt = "/home/hmc/gaussian-splatting/GS_projects/data/Home/sparse/0/cameras.txt"

    extrinsics_dict = load_extrinsics(images_txt)

    pointclouds = []
    frames = []

    for cam_id in range(9):
        pcd, frame = create_pointcloud_for_camera(cam_id, extrinsics_dict, cameras_txt)
        pointclouds.append(pcd)
        frames.append(frame)

    # Fusionner nuages
    pcd_combined = pointclouds[0]
    for pcd in pointclouds[1:]:
        pcd_combined += pcd

    # Sauvegarder fusion
    o3d.io.write_point_cloud("cloud_fusion_corrected.ply", pcd_combined)
    print(f"[INFO] Nuage fusionné sauvegardé sous cloud_fusion_corrected.ply")

    # Visualiser avec les repères caméra
   # o3d.visualization.draw_geometries([pcd_combined] + frames)

if __name__ == "__main__":
    main()
