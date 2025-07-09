import os

sparse_dir = "/home/hmc/gaussian-splatting/GS_projects/data/NewFVV/sparse/0"
input_file = os.path.join(sparse_dir, "cameras.txt")
backup_file = os.path.join(sparse_dir, "cameras_backup.txt")
output_file = os.path.join(sparse_dir, "cameras.txt")

# Sauvegarde de l'ancien fichier
os.rename(input_file, backup_file)

with open(backup_file, "r") as fin, open(output_file, "w") as fout:
    for line in fin:
        if line.startswith("#") or line.strip() == "":
            fout.write(line)
        elif "SIMPLE_PINHOLE" in line:
            print("Avant conversion :", line.strip())
            line = line.replace("SIMPLE_PINHOLE", "PINHOLE")
            parts = line.strip().split()
            fx = parts[4]
            params = [fx, fx, parts[5], parts[6]]
            new_line = " ".join(parts[:4] + params)
            fout.write(new_line + "\n")
            print("Après conversion :", new_line)
        else:
            fout.write(line)

print("Conversion SIMPLE_PINHOLE -> PINHOLE terminée.")
print(f"Ancien fichier sauvegardé sous : {backup_file}")
