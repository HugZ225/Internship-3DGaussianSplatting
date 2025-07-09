import open3d as o3d


ply_path = "/home/hmc/gaussian-splatting/GS_projects/data/Desert/sparse/0/points3D.ply"
pcd = o3d.io.read_point_cloud(ply_path)
if pcd.is_empty():
    print("⚠️ Point cloud vide après lecture.")
else:
    print(pcd)
    o3d.visualization.draw_geometries([pcd])
