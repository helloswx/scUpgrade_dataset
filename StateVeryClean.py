import os

def delete_empty_subfolders(folder):
    for subfolder in os.listdir(folder):
        subfolder_path = os.path.join(folder, subfolder)
        if os.path.isdir(subfolder_path):
            files = os.listdir(subfolder_path)
            if not files:  # if the subfolder is empty
                os.rmdir(subfolder_path)
            elif len(files) == 1:  # if the subfolder contains only one file
                os.remove(os.path.join(subfolder_path, files[0]))  # delete the file
                os.rmdir(subfolder_path)  # delete the subfolder

delete_empty_subfolders('StateVeryClean')
