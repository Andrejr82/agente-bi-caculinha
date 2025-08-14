import os

project_root = r'T:\Meu Drive\Caçula\Langchain\Agent_BI'

def remove_file(file_name):
    file_path = os.path.join(project_root, file_name)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f'Removed file: {file_path}')
        except OSError as e:
            print(f'Error removing {file_path}: {e}')
    else:
        print(f'File not found: {file_path}')

remove_file('cleanup_script.py')
remove_file('run_cleanup.bat')
remove_file('run_cleanup_final.bat')
remove_file('temp_cleanup.py')
remove_file('final_cleanup_temp.py')

print('Final cleanup complete.')
