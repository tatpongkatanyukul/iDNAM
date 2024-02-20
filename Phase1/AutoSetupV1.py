##############################################
## Pre-amble: path
##############################################

print("\n\nAutoSetup: ...")

try:
    import bpy
except Exception as err:
    print("AutoSetup: Error: ", err)
    print("AutoSetup: Run this script with Blender: Scripting.")
    raise Exception("Incorrect setting.")

# Locate working path
import pathlib

script_path = __file__
print(f"AutoSetup: Script file = {__file__}")

# Check if we are running from the Blender Text Editor
if bpy.context.space_data != None and bpy.context.space_data.type == 'TEXT_EDITOR':
    # Get the path to the SAVED script when running from Blender
    script_path = bpy.context.space_data.text.filepath
#    print('   * bpy.context.space_data.text.filepath =', script_path)

script_dir = pathlib.Path(script_path).resolve().parent
#print(f" * script directory = {script_dir}")

work_path = str(script_dir)
print(f"AutoSetup: Work path = {work_path}")

import sys
sys.path.append(work_path)

##############################################
## Install scipy
##############################################

import subprocess
import sys
import json
import time
import os

if __name__ == '__main__':

    # python -m pip install scipy
    
    lcmd = [sys.executable, "-m", "pip", "install", "scipy", 
            f"--target={work_path}"]
    print("Running ", lcmd, '\n')
#    lcmd = [sys.executable, 
#        r"C:\Users\tatpong\Desktop\2024\Phase1\test.py"]
    x = subprocess.run(lcmd, capture_output=True)
 
    print(x)
    str_sout = str(x.stdout, encoding='utf-8')
#    print(x.stdout)

##    print("type(x.stdout)=", type(x.stdout))
#    
#    
#    i = str_sout.find(" in ")
#    scut = str_sout[i:].strip()
##    print(">>", scut)

#    i = scut.find(" ")
#    scut = scut[i:].strip()
##    print(">>", scut)

#    i = scut.find(" ")
#    scut = scut[:i].strip()
##    print(">>", scut)    

#    sp_path = scut
#    
#    print("\nsp_path =", sp_path, '\n')

#    assert Exception("STOP")


    if len(x.stderr) > 0:
        print(x.stderr)
    else:
        
        try:
            import scipy as sp
            print(f'Scipy version {sp.__version__} has been successfully installed.')
        except Exception as err:
            print("Test run fails. Error:", err)
            


#    exe_path = pathlib.Path(sys.executable).resolve().parent
#    print('exe path =', exe_path)

    # Data to be written
    rst = {
        "date": time.ctime(),
        "command": str(lcmd),
        "stdout": str_sout,
        "stderr": str(x.stderr),
        "scipy_path": work_path
    }
    
#    print('rst =', rst)
     
    # Serializing json
    json_object = json.dumps(rst, indent=4)
     
    # Writing to sample.json
    path_json = os.path.join(work_path, "rst.json")
    with open(path_json, "w") as outfile:
        outfile.write(json_object) 

    print()

# def install(package):
#     subprocess.check_call([sys.executable, "-m", "pip", "install", package])
#     # Code needing to capture stdout or stderr should use run() instead:

# def learn_run():
#     x = subprocess.run([sys.executable, "-m", "pip", "--help"], capture_output=True)
#     # print('x =', x)
#     print('type(x) =', type(x))
#     print(vars(x))


# def install_scipy():    
#     x = subprocess.run([sys.executable, "-m", "pip", "install", package], capture_output=True)
#     print('x =', x)


####################################
def test_z80():
    # https://pypi.org/project/z80/
    install("z80")
