import numpy as np
import sys,os,inspect
from time import sleep
import matplotlib.pyplot as plt
import fastest_lap
import json



def run_optimal_laptime(track_name, track_path, vehicle_path, print_level = 5):

    # Loading track
    track=track_name
    fastest_lap.create_track_from_xml(track,track_path)
    s = fastest_lap.track_download_data(track,"arclength")

    # Loading vehicle
    vehicle = "car"
    fastest_lap.create_vehicle_from_xml(vehicle,vehicle_path)

    # Defining and setting options
    options  = "<options>"
    options += "    <output_variables>"
    options += "        <prefix>run/</prefix>"
    options += "    </output_variables>"
    options += f"    <print_level> {print_level} </print_level>"
    options += "</options>"

    # Running t he simulation and storing the results in run
    run = fastest_lap.download_variables(*fastest_lap.optimal_laptime(vehicle, track, s, options))

    # Writting the results on a file
    with open("run_data.json", "x") as f:
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

