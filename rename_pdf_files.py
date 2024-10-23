import os

def rename_pdfs(folder_path):
    files = []
    for f in os.listdir(folder_path):
        if f.endswith('.pdf'):
            files.append(f)
    files.sort()
    for i in range(len(files)):
        file = files[i]  
        old_path = os.path.join(folder_path, file)
        new_path = os.path.join(folder_path, f"{i + 1}.pdf")
        os.rename(old_path, new_path)
        print(f"Renamed: {file} -> {i + 1}.pdf")
