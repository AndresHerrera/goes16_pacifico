import os
import shutil

def list_files_by_mtime(folder_path, extension):
    # Get the list of all files in the directory
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.endswith(extension)]

    # Sort the files by modification time in descending order
    files.sort(key=os.path.getmtime, reverse=True)

    return files

def purge_folder(folder_path, extension, deltatime):
    # Get all files in the directory
    files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file)) and file.endswith(extension)]
    
    # Sort files by modification time (most recent first)
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    # Keep the 4 most recent files, delete the rest
    files_to_delete = files[deltatime:]
    
    for file in files_to_delete:
        os.remove(file)
        print(f"Deleted: {file}")
    return True