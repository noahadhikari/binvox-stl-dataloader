import os
import glob

#get all files, recursively, in the data directory

for file in glob.glob('data/**', recursive=True):
    # if file contains but your computer or network may be sending automated queries. To protect our users, we can't process your request right now.
    # then remove it
    if not os.path.isdir(file):
        if "but your computer or network may be sending automated queries. To protect our users, we can't process your request right now." in open(file, errors="ignore").read():
            os.remove(file)
            print(f"Removed {file}")
            