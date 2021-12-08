import json
import os
import shutil

from app_utils import util

"""
A project .json file contains the following:
{
    "name": string - the name of the project, must match root catalogue,
    "lat": float - the latitude the model lies at,
    "long": float - the longitude the model lies at,
    "start_date": string - the start date of the simulation, YYYY-mm-dd
    "end_date": string - the end date of the simulation, YYYY-mm-dd,
    "spin_up": float - how many days of hydrus simulation should be ignored,
    "rows": int - the amount of rows in the model grid,
    "cols": int - the amount of columns in the model grid,
    "grid_unit": string - the unit in which the model grid size is represented; "feet", "meters", "centimeters" or null,
    "row_cells": List<Float> - the heights of the model's consecutive rows,
    "col_cells": List<Float> - the widths of the model's consecutive columns,
    "modflow_model": string - the name of the folder containing the modflow model,
    "hydrus_models": List<String> - a list of names of folders containing the hydrus models
}
"""


def create(project: dict):
    """
    Creates a new project in the workspace. The project consists of a root directory, which contains
    a modflow folder for the modflow model, a hydrus folder for the hydrus models, and a JSON file
    containing information about the project, as described above.

    :param project: dictionary, the representation of the project's JSON file
    :return: None
    """
    # create catalogue structure
    # TODO - check for collision?
    project_root = os.path.join(util.workspace_dir, project['name'])
    hydrus_folder = os.path.join(project_root, 'hydrus')
    modflow_folder = os.path.join(project_root, 'modflow')
    os.mkdir(project_root)
    os.mkdir(hydrus_folder)
    os.mkdir(modflow_folder)

    # save project JSON file
    file_path = os.path.join(project_root, project['name']+'.json')
    file = open(file_path, 'w+')
    json.dump(project, file)


def read(project_name: str):
    """
    Reads and returns the JSON file for the project with the specified name.

    :param project_name: string, the name of the project whose JSON file we want to retrieve
    :return: the project's JSON file
    """
    return json.load(open(os.path.join(util.workspace_dir, project_name, project_name+".json")))


def read_all():
    """
    Returns a list of names of all projects existing in the system.

    :return: a list of strings, the project names
    """
    return [name for name in os.listdir(util.workspace_dir) if os.path.isdir(os.path.join(util.workspace_dir, name))]


def update(project_name: str, changed_fields: dict):
    """
    Updates the given fields in a given project, leaving the rest unchanged. The name field cannot be modified.
    If the project that was updated was currently loaded, the app utility will be given this updated object as well.

    :param project_name: string, the project whose fields to update
    :param changed_fields: dict, the fields to be updated
    :return: None
    """
    # read and update project file
    project = read(project_name)
    for field in changed_fields.keys():
        if field != "name":
            project[field] = changed_fields[field]

    # if that project is currently loaded, and it probably is, update the record in the utility
    if util.loaded_project and util.loaded_project["name"] == project_name:
        util.loaded_project = project

    # write the updated project into the JSON file
    file = open(os.path.join(util.workspace_dir, project_name, project_name+".json"), "w")
    json.dump(project, file)


def remove_model(model_type: str, model_name: str):
    """
    Removes an already loaded model from the project.

    :param model_type: string, the type of model to delete, "hydrus" or "modflow"
    :param model_name: string, the name of the model to delete
    :return: None
    """
    model_path = os.path.join(util.workspace_dir, util.loaded_project["name"], model_type, model_name)
    if os.path.isdir(model_path):
        shutil.rmtree(model_path)
        if model_type == 'modflow':
            update(util.loaded_project["name"], {"modflow_model": None})
        else:
            new_list = util.loaded_project["hydrus_models"]
            new_list.remove(model_name)
            print(new_list)
            if new_list is None:
                new_list = []
            update(util.loaded_project["name"], {"hydrus_models": new_list})


def remove_project(project_name: str):
    """
    Removes an existing project from the workspace

    :param project_name: the name of the project to be removed
    :return: None
    """
    project_path = os.path.join(util.workspace_dir, project_name)

    # remove project
    if os.path.isdir(project_path):
        shutil.rmtree(project_path)

    # if project was currently loaded, remove it and reset util fields
    if util.loaded_project is not None and util.loaded_project['name'] == project_name:
        util.reset_project_data()


def update_hydrus_model(model_name: str, data: dict):
    """
    Enriches the target hydrus model with weather file data.

    :param model_name: the name of the model to modify
    :param data: a dictionary with the loaded weather data
    :return: None
    """
    model_dir = os.path.join(util.get_hydrus_dir(), model_name)
    meteo_file_path = os.path.join(model_dir, "METEO.IN")
    meteo_file = open(meteo_file_path, "rw")

    old_file_lines = meteo_file.readlines()
    new_file_lines = []

    # update latitude and altitude
    i = 0
    while True:
        curr_line = old_file_lines[i]
        new_file_lines.append(curr_line)
        if "Latitude" in curr_line:
            # write the updated values and break
            new_file_lines.append(f"   {data['Latitude']}   {data['Elevation']}\n")
            i += 1
            break

    # update the day-by-day conditions
    # check which fields we have data about
    replace_rad = "Solar" in data.keys()
    replace_tmax = "Max Temperature" in data.keys()
    replace_tmin = "Min Temperature" in data.keys()
    replace_rhmin = "Relative Humidity" in data.keys()
    replace_wind = "Wind" in data.keys()
    replace_rain = "Precipitation" in data.keys()
    # navigate to table start
    while True:
        curr_line = old_file_lines[i]
        new_file_lines.append(curr_line)
        if "Daily values" in curr_line:
            i += 1
            new_file_lines.append(old_file_lines[i])  # skip field descriptions line
            i += 1
            new_file_lines.append(old_file_lines[i])  # skip units line
            i += 1
            break
    # write new table values, only change columns for which we have data
    while True:

        # break if reached end of file
        curr_line = old_file_lines[i]
        if "end" in curr_line:
            new_file_lines.append(curr_line)
            break

        curr_row = old_file_lines[i].split()
        if replace_rad:
            curr_row[1] = data["Solar"][i]
        if replace_tmax:
            curr_row[2] = data["Max Temperature"][i]
        if replace_tmin:
            curr_row[3] = data["Min temperature"][i]
        if replace_rhmin:
            curr_row[4] = data["Relative Humidity"][i]
        if replace_wind:
            curr_row[5] = data["Wind"][i]

        new_line = "   "
        for item in curr_row:
            new_line += f"{item}    "
        new_line += "\n"
        new_file_lines.append(new_line)

        i += 1

    # overwrite meteo file
    meteo_file.writelines(new_file_lines)
    meteo_file.close()

    # TODO - figure out where precipitation data goes and write it there
    if replace_rain:
        pass
