import numpy as np
from flask import Flask, render_template, request, redirect, url_for, jsonify
from zipfile import ZipFile
from datapassing.shapeData import ShapeFileData, Shape

import flopy

import os
import json

from AppUtils import AppUtils
from simulation.SimulationService import SimulationService
import threading

util = AppUtils()
util.setup()
app = Flask("App")
simulation_service = SimulationService(hydrus_dir=util.hydrus_dir,
                                       modflow_dir=util.modflow_dir)


# ------------------- ROUTES -------------------
@app.route('/')
def start():
    return redirect(request.url + "home")


@app.route('/upload-modflow', methods=['GET', 'POST'])
def upload_modflow():
    if request.method == 'POST' and request.files:
        return upload_modflow_handler(request)
    else:
        return render_template('uploadModflow.html', model_names=util.loaded_modflow_models)


@app.route('/upload-hydrus', methods=['GET', 'POST'])
def upload_hydrus():
    if request.method == 'POST' and request.files:
        return upload_hydrus_handler(request)
    else:
        return render_template('uploadHydrus.html', model_names=util.loaded_hydrus_models)


@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/define-shapes/<hydrus_model_index>', methods=['GET', 'POST'])
def define_shapes(hydrus_model_index):
    if request.method == 'POST':
        return upload_shape_handler(request, int(hydrus_model_index))
    else:
        return next_model_redirect_handler(int(hydrus_model_index))


@app.route('/simulation', methods=['GET'])
def simulation():
    return render_template('simulation.html', modflow_proj=util.loaded_modflow_models,
                           shapes=util.loaded_shapes)


@app.route('/simulation-run')
def run_simulation():
    if (
            util.hydrus_dir is None or
            util.modflow_dir is None or
            util.loaded_modflow_models is None or not util.loaded_modflow_models or
            util.loaded_shapes is None or not util.loaded_shapes
    ):
        return jsonify(message="Some projects are missing"), 500

    sim = simulation_service.prepare_simulation()

    sim.set_modflow_project(modflow_project=util.loaded_modflow_models[0])
    sim.set_loaded_shapes(loaded_shapes=util.loaded_shapes)

    sim_id = sim.get_id()

    thread = threading.Thread(target=simulation_service.run_simulation, args=(sim_id, "default"))
    thread.start()
    return jsonify(id=sim_id)


@app.route('/simulation-check/<simulation_id>', methods=['GET'])
def check_simulation_status(simulation_id: int):
    hydrus_finished, passing_finished, modflow_finished = simulation_service.check_simulation_status(int(simulation_id))
    response = {'hydrus': hydrus_finished, 'passing': passing_finished, 'modflow': modflow_finished}
    return jsonify(response)


# ------------------- END ROUTES -------------------


# ------------------- HANDLERS -------------------

def upload_modflow_handler(req):
    project = req.files['archive-input']  # matches HTML input name

    if util.type_allowed(project.filename):

        # save, unzip, remove archive
        archive_path = os.path.join(util.workspace_dir, 'modflow', project.filename)
        project.save(archive_path)
        with ZipFile(archive_path, 'r') as archive:
            # get the project name and remember it
            project_name = project.filename.split('.')[0]
            util.loaded_modflow_models = [project_name]

            # create a dedicated catalogue and load the project into it
            project_path = os.path.join(util.workspace_dir, 'modflow', project_name)
            os.system('mkdir ' + project_path)
            archive.extractall(project_path)

            # validate model and get model size
            # TODO - validate model
            get_nam_file(project_path)
            get_model_size(project_path)

        print("Project uploaded successfully")
        os.remove(archive_path)
        return redirect(req.root_url + 'upload-modflow')

    else:
        print("Invalid archive format, must be one of: ", end='')
        print(util.allowed_types)
        return redirect(req.url)


def upload_hydrus_handler(req):
    project = req.files['archive-input']  # matches HTML input name

    if util.type_allowed(project.filename):

        # save, unzip, remove archive
        archive_path = os.path.join(util.workspace_dir, 'hydrus', project.filename)
        project.save(archive_path)
        with ZipFile(archive_path, 'r') as archive:

            # get the project name and remember it
            project_name = project.filename.split('.')[0]
            util.loaded_hydrus_models.append(project_name)

            # create a dedicated catalogue and load the project into it
            os.system('mkdir ' + os.path.join(util.workspace_dir, 'hydrus', project_name))
            archive.extractall(os.path.join(util.workspace_dir, 'hydrus', project_name))

        os.remove(archive_path)

        print("Project uploaded successfully")
        return redirect(req.root_url + 'upload-hydrus')

    else:
        print("Invalid archive format, must be one of: ", end='')
        print(util.allowed_types)
        return redirect(req.url)


def upload_shape_handler(req, hydrus_model_index):
    # if not yet done, initialize the shape arrays list to the amount of models
    if len(util.loaded_shapes) < len(util.loaded_hydrus_models):

        for hydrus_model in util.loaded_hydrus_models:
            util.loaded_shapes[hydrus_model] = None
        # util.loaded_shapes = [None for _ in range(len(util.loaded_hydrus_models))]

    # read the array from the request and store it
    shape_array = req.get_json(force=True)
    np_array_shape = np.array(shape_array)
    util.loaded_shapes[util.loaded_hydrus_models[hydrus_model_index]] = ShapeFileData(shape_mask_array=np_array_shape)

    return json.dumps({'status': 'OK'})


def next_model_redirect_handler(hydrus_model_index):
    # check if we still have models to go, if not, redirect to next section
    if hydrus_model_index >= len(util.loaded_hydrus_models):

        for key in util.loaded_shapes:
            print(key, '->', util.loaded_shapes[key].shape_mask)
        print(util.loaded_shapes)
        return simulation()

    else:
        return render_template(
            'defineShapes.html',
            rowAmount=util.modflow_rows,
            colAmount=util.modflow_cols,
            rows=[str(x) for x in range(util.modflow_rows)],
            cols=[str(x) for x in range(util.modflow_cols)],
            modelIndex=hydrus_model_index,
            modelName=util.loaded_hydrus_models[hydrus_model_index]
        )

# ------------------- END HANDLERS -------------------


# ------------------- MISC FUNCTIONS -------------------

def get_nam_file(project_path: str):
    for filename in os.listdir(project_path):
        filename = str(filename)
        if filename.endswith(".nam"):
            util.nam_file_name = filename
            return
    print("ERROR: invalid modflow model; missing .nam file")


def get_model_size(project_path: str):
    modflow_model = flopy.modflow.Modflow \
        .load(util.nam_file_name, model_ws=project_path, load_only=["rch"], forgive=True)
    util.modflow_rows = modflow_model.nrow
    util.modflow_cols = modflow_model.ncol

# ------------------- END MISC FUNCTIONS -------------------
