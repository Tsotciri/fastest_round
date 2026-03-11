import numpy as np
import sys,os,inspect
from time import sleep
import matplotlib.pyplot as plt
import fastest_lap
import json
import xml.etree.ElementTree as ET
import xml.etree.ElementTree as ET

def get_car_name(string: str):
    name = ""
    for char in string:
        if char.isalpha():
            name += char
        else:
            break
    return name

def run_optimal_laptime(track_name, track_path, vehicle_path, data_output_name ,print_level = 5):

    # Loading track
    track = track_name
    s = fastest_lap.track_download_data(track,"arclength")

    # Loading vehicle

    # Getting the name of the car from its filename
    vehicle = "car_" + get_car_name(os.path.basename(vehicle_path))

    fastest_lap.create_vehicle_from_xml(vehicle,vehicle_path)

    # Defining and setting options
    options  = "<options>"
    options += "    <output_variables>"
    options += "        <prefix>run/</prefix>"
    options += "    </output_variables>"
    options += f"    <print_level> {print_level} </print_level>"
    options += "</options>"

    print(f"Running simulation with vehicle: {vehicle} ({vehicle_path})")

    # Running t he simulation and storing the results in run
    run = fastest_lap.download_variables(*fastest_lap.optimal_laptime(vehicle, track, s, options))

    # Writting the results on a file
    with open(f"{data_output_name}.json", "x") as f:
        json.dump(run, f, indent=2)

def run_circuit_preproccessor(right_kml, left_kml, output_name, num_of_elemments = 1000, print_level = 5):

    # Defining and setting options
    options = "<options>"
    options += "    <kml_files>"
    options += f"        <left>{left_kml}</left>"
    options += f"        <right>{right_kml}</right>"
    options += "    </kml_files>"   
    options += "    <mode>equally-spaced</mode>"
    options += "    <is_closed>true</is_closed>"
    options += f"    <number_of_elements>{num_of_elemments}</number_of_elements>"
    options += f"    <xml_file_name>{output_name}</xml_file_name>"
    options += "    <output_variables>"
    options += "        <prefix>track/</prefix>"
    options += "    </output_variables>"
    options += f"    <print_level> {print_level} </print_level>"
    options += "</options>"
    
    print("Pre-proccessor running, this may take some time depending on the size of the track")

    # Calling the pre-proccessor
    try:
        fastest_lap.circuit_preprocessor(options)
    except:
        print("An error occured wile running the pre-proccessor")
    else:
        print("Complete!\a")

    input("Press enter to continue...")

# This function is made by gemini
def xml_scale(input_file, output_file, sf):
    tree = ET.parse(input_file)
    root = tree.getroot()

    # 1. Scale the Track Length in Header
    tl = root.find('.//track_length')
    if tl is not None:
        tl.text = str(float(tl.text) / sf)

    # 2. Iterate through EVERY single tag in the XML
    for elem in root.iter():
        # Case A: It's an array (like x, y, arclength, or a width array)
        if elem.text and ',' in elem.text:
            try:
                vals = [float(v.strip()) for v in elem.text.split(',')]
                
                if elem.tag == 'curvature':
                    # Curvature must increase to tighten the physics
                    new_vals = [str(v * sf) for v in vals]
                elif any(x in elem.tag.lower() for x in ['lat', 'lon', 'origin', 'earth']):
                    # Protect GPS origin data
                    continue
                else:
                    # Scale everything else down (x, y, arclength, widths)
                    new_vals = [str(v / sf) for v in vals]
   
                elem.text = ", ".join(new_vals)
                
            except ValueError:
                continue

        # Case B: It's a single number (This is likely where your width is hidden!)
        elif elem.text:
            try:
                val = float(elem.text)
                # We skip point counts (like 1200) or very small/large flags
                # This scales single values like <width_left>3.0</width_left>
                if 0.01 < val < 1000 and elem.tag != 'track_length':
                    if any(x in elem.tag.lower() for x in ['lat', 'lon', 'origin']):
                        continue
                    elem.text = str(val / sf)
            except ValueError:
                continue

    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    print(f"Track scaled by {sf} succesfully.")

