"""
Front-End: open in Blender
Derived from 
* D230201/AutoPlateV10.py
* D230203/AutoBridgeV1.py (2024/02/10)

Refactoring
"""

print('\n' + '-'*80)
print('# Front-End script')

import time
print('    Current time:', time.ctime())
   

import bpy

import os
s_cwd = os.getcwd()
print('    Current working directory =', s_cwd)


# Locate working path
import pathlib

script_path = __file__
print(f"    Script file = {__file__}")

# Check if we are running from the Blender Text Editor
if bpy.context.space_data != None and bpy.context.space_data.type == 'TEXT_EDITOR':
    # Get the path to the SAVED script when running from Blender
    script_path = bpy.context.space_data.text.filepath
#    print('   * bpy.context.space_data.text.filepath =', script_path)

script_dir = pathlib.Path(script_path).resolve().parent
#print(f" * script directory = {script_dir}")

work_path = str(script_dir)
#work_path = r"C:\Y2024\iDNAM\D230203"

###################
## Read setup.json
###################

import json

fsetup='setup.json' 
psetup = os.path.join(work_path,fsetup)

# Read configuration and parameters
setup_vars = {} 

with open(psetup) as f:
   setup_vars = json.load(f)

####################
# Add working path
####################

import sys
sys.path.append(work_path)

print("    * Append working path:", work_path)

####################
# Add scipy path
####################

# Path for scipy
packages_path = setup_vars["scipy_path"]
sys.path.insert(0, packages_path )

print("    * Set-up scipy path:", packages_path)

#print("      Working path content:")
#print('      * ', os.listdir(work_path))

import DTPanelV5 as dt             # GUI
import BUtilsV5 as uu                # General blender utils
import RidgeIdenV3 as ri           # Ridge identification
import ShapeApproxV4 as sa         # Shape approximation
import CrossSecApproxV5 as csa     # Cross-section approximation

import importlib
importlib.reload(dt)
importlib.reload(uu)
importlib.reload(ri)
importlib.reload(sa)
importlib.reload(csa)



#############################
# BEGIN MAIN
#############################    


if __name__ == '__main__':


   print('\n# Main')

   cfg='conf.json' 
   pcfg = os.path.join(work_path, cfg)
   print(f'  * Read cfg: {pcfg}')
   

   # Read configuration and parameters
   pvars = {} 

   with open(pcfg) as f:
      # Read pvars from cfg
      pvars = json.load(f)
      assert len(pvars) > 0, f"Configuration file ({pcfg}) error"

   logfile = os.path.join(work_path, pvars['log'])

   # Clear log
   uu.clear_log(logfile)

   # Start a new log
   uu.log(f'AutoBridge: Read configuration {cfg}', logfile)


   # Set-up DT Panel 
   print(f'  * Set-up DT Panel')
    
   dt.wpath=work_path 
   
   # Aj Wasu's params
   dt.vert_double_threshold = 0.1   # per 3D printer capability
   dt.dissolve_threshold = 0.01
   
   # TK's params
   dt.config_file = pcfg
   dt.pvars = pvars
   dt.logfile = logfile

   dt.register()
#   dt.unregister()

   uu.log('AutoBridge: Set-up DT panel', logfile)


   # Set-up BUtils   
   uu.CODE = {"T": "T1", "Tp": "T1'", "C": "C1",
              "RO": "RO", "RI": "RI",
              "target": "SCAN"} 

   print(f'  * Set-up object names:', uu.CODE)

   uu.log('AutoBridge: Set-up object names', logfile)


   print('  * DT Status =', dt.status)

   print('\n# End Main')
   print('-'*80 + '\n')
   
   

#############################
# END MAIN
#############################    

