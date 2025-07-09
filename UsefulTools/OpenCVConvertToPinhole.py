import os

sparse_dir = "/home/hmc/gaussian-splatting/GS_projects/data/Desert/sparse/0"
input_file = os.path.join(sparse_dir, "cameras.txt")
backup_file = os.path.join(sparse_dir, "cameras_OpenCV.txt")
output_file = os.path.join(sparse_dir, "cameras.txt")

os.rename(input_file, backup_file)

with open(backup_file, "r") as fin, open(output_file, "w") as fout:
    for line in fin:
        if line.startswith("#") or line.strip() == "":
            fout.write(line)
        else:
            parts = line.strip().split()
            if parts[1] == "OPENCV":
                parts[1] = "PINHOLE"
                # Ne pas tronquer à 8, garder fx, fy, cx, cy (index 4 à 7)
                # On réécrit avec juste 8 premiers paramètres : CAMERA_ID, MODEL, WIDTH, HEIGHT, fx, fy, cx, cy
                parts = parts[:4] + parts[4:8]
            fout.write(" ".join(parts) + "\n")

print("Conversion OPENCV -> PINHOLE terminée.")
print(f"Ancien fichier sauvegardé sous : {backup_file}")
print(f"Nouveau fichier écrit sous : {output_file}")
