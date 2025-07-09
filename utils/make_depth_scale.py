import numpy as np
import argparse
import cv2
from joblib import delayed, Parallel
import json
import os
import open3d as o3d
from read_write_model import *


def read_points3D_from_ply(ply_path):
    """
    Lit un nuage de points depuis un fichier PLY et retourne les points sous forme de numpy array.
    """
    pcd = o3d.io.read_point_cloud(ply_path)
    points = np.asarray(pcd.points)
    return points


def get_scales(key, cameras, images, points3d_ordered, args):
    image_meta = images[key]
    cam_intrinsic = cameras[image_meta.camera_id]

    pts_idx = image_meta.point3D_ids

    mask = pts_idx >= 0
    mask *= pts_idx < len(points3d_ordered)

    pts_idx = pts_idx[mask]
    valid_xys = image_meta.xys[mask]

    if len(pts_idx) > 0:
        if np.max(pts_idx) >= len(points3d_ordered):
            print(f"Warning: {image_meta.name} — some point3D_ids exceed PLY points count.")
            return None
        pts = points3d_ordered[pts_idx]
    else:
        pts = np.array([[0, 0, 0]])

    R = qvec2rotmat(image_meta.qvec)
    pts = np.dot(pts, R.T) + image_meta.tvec

    invcolmapdepth = 1. / pts[..., 2]
    n_remove = len(image_meta.name.split('.')[-1]) + 1
    invmonodepthmap = cv2.imread(f"{args.depths_dir}/{image_meta.name[:-n_remove]}.png", cv2.IMREAD_UNCHANGED)

    if invmonodepthmap is None:
        return None

    if invmonodepthmap.ndim != 2:
        invmonodepthmap = invmonodepthmap[..., 0]

    invmonodepthmap = invmonodepthmap.astype(np.float32) / 6000

    s = invmonodepthmap.shape[0] / cam_intrinsic.height

    maps = (valid_xys * s).astype(np.float32)
    valid = (
        (maps[..., 0] >= 0) *
        (maps[..., 1] >= 0) *
        (maps[..., 0] < cam_intrinsic.width * s) *
        (maps[..., 1] < cam_intrinsic.height * s) * (invcolmapdepth > 0)
    )

    print(f"{image_meta.name}: valid pixels = {valid.sum()}, invcolmapdepth range = {invcolmapdepth.max() - invcolmapdepth.min()}")

    if valid.sum() > 10 and (invcolmapdepth.max() - invcolmapdepth.min()) > 1e-5:
        maps = maps[valid, :]
        invcolmapdepth = invcolmapdepth[valid]
        invmonodepth = cv2.remap(invmonodepthmap, maps[..., 0], maps[..., 1],
                                 interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)[..., 0]

        t_colmap = np.median(invcolmapdepth)
        s_colmap = np.mean(np.abs(invcolmapdepth - t_colmap))

        t_mono = np.median(invmonodepth)
        s_mono = np.mean(np.abs(invmonodepth - t_mono))

        scale = s_colmap / s_mono
        offset = t_colmap - t_mono * scale
    else:
        scale = 0
        offset = 0

    return {"image_name": image_meta.name[:-n_remove], "scale": scale, "offset": offset}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--base_dir', default="../data/big_gaussians/standalone_chunks/campus")
    parser.add_argument('--depths_dir', default="../data/big_gaussians/standalone_chunks/campus/depths_any")
    parser.add_argument('--model_type', default="bin")
    parser.add_argument('--ply_path', default="cloud_global_clean.ply", help="Nom du fichier .ply contenant le nuage de points")

    args = parser.parse_args()

    cam_intrinsics, images_metas, _ = read_model(os.path.join(args.base_dir, "sparse", "0"), ext=f".{args.model_type}")

    ply_file_path = os.path.join(args.base_dir, "sparse", "0", args.ply_path)
    points3d_ordered = read_points3D_from_ply(ply_file_path)

    depth_param_list = Parallel(n_jobs=-1, backend="threading")(
        delayed(get_scales)(key, cam_intrinsics, images_metas, points3d_ordered, args)
        for key in images_metas
    )

    depth_params = {
        depth_param["image_name"]: {"scale": depth_param["scale"], "offset": depth_param["offset"]}
        for depth_param in depth_param_list if depth_param is not None
    }

    output_path = os.path.join(args.base_dir, "sparse", "0", "depth_params.json")
    with open(output_path, "w") as f:
        json.dump(depth_params, f, indent=2)

    print(f"✅ Depth parameters written to {output_path}")
