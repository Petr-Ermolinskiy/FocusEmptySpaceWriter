import os
import shutil

def clean():
    print("Cleaning build artifacts...")
    
    # Remove directories (excluding dist)
    dirs_to_remove = ['build', '__pycache__', 'src/__pycache__', 'tests/__pycache__']
    for dir_path in dirs_to_remove:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"Removed {dir_path}")
            except Exception as e:
                print(f"Error removing {dir_path}: {e}")
    
    # Remove spec files
    spec_files = [f for f in os.listdir('.') if f.endswith('.spec')]
    for spec_file in spec_files:
        try:
            os.remove(spec_file)
            print(f"Removed {spec_file}")
        except Exception as e:
            print(f"Error removing {spec_file}: {e}")

if __name__ == '__main__':
    clean() 