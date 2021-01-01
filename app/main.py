from flask import Flask, redirect, url_for, render_template, request, session, flash, send_file, Response, make_response
import pyrebase
from datetime import datetime
from datetime import timedelta
import numpy as np
import pandas as pd
from app.engine import *
from app.input_handling import *
import os
import random
import time
import datetime
import xml.etree.ElementTree as ET
import zipfile
from functools import wraps, update_wrapper
from datetime import datetime
from flask_cors import CORS, cross_origin
import flask_fs as fs
from app.pyrebase_config import *
import plotly
import plotly.graph_objects as go


firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
storage = firebase.storage()

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
a = False
app.secret_key="hello"
app.permanent_session_lifetime = timedelta(minutes=30)
simulation_lock = True
email = ''




def check_session():
    if auth.current_user is None:
        session.pop("user_id",None)
    return

def get_Saved_viz_path(storage, current_viz, user_id):
    file_path = user_id + "/saved_viz/" + current_viz
    viz_Url = storage.child(file_path).get_url(None)
    return viz_Url

@app.route("/", methods=['POST', 'GET'])
def home():
    check_session()
    if "user_id" in session:
        simulation_Enabled = check_for_current_Catalog_and_Config(session)
        if request.method == "POST":
            if "del_viz" in request.form:
                viz_current = request.form["viz_current"]
                session["current_viz"] = del_viz(session["user_id"], viz_current, session["current_viz"])
            if "set_viz" in request.form:
                session["current_viz"] = request.form.get('viz_current')
                file_path = get_Saved_viz_path(storage, session['current_viz'], session["user_id"])
                session["viz_path_file"] = file_path
                timestamp = datetime.now().strftime("%d-%m_%I-%M-%S_%p")
                return render_template("visualizacao.html", vizz_file = session["viz_path_file"], timestamp = timestamp)
        saved_viz_group = list_saved_viz(session["user_id"])
        #fator de sabotagem de notas
        pct_g, sb_g, rc_g = generate_graphic_sab_rec_grade(session["grade_sab_rec_factors"])
        pct_f, sb_f, rc_f = generate_graphic_sab_rec_frequency(session["frequency_sab_rec_factors"])
        easy_impact, hard_impact = generate_graphic_easy_hard_subjects(session["factors"])
        abrupt_positive, abrupt_negative = generate_graphic_abrupt_alteration(session["easy_hard_factors"])
        return render_template('index.html',array_test = [0,2,4,6], uid = session["user_id"], simulation_Enabled = simulation_Enabled, saved_viz_group = saved_viz_group)
    else:
        simulation_Enabled = False
        return render_template('index.html',array_test = [0,2,4,6], simulation_Enabled = simulation_Enabled)
    return render_template('index.html',array_test = [0,2,4,6], uid = None)

@app.route("/fatores")
def fatores():
    simulation_Enabled = check_for_current_Catalog_and_Config(session)
    pct_g, sb_g, rc_g = generate_graphic_sab_rec_grade(session["grade_sab_rec_factors"])
    pct_f, sb_f, rc_f = generate_graphic_sab_rec_frequency(session["frequency_sab_rec_factors"])
    easy_impact, hard_impact = generate_graphic_easy_hard_subjects(session["factors"])
    abrupt_positive, abrupt_negative = generate_graphic_abrupt_alteration(session["easy_hard_factors"])
    return render_template('fatores.html', simulation_Enabled = simulation_Enabled, pct_g = pct_g, sb_g = sb_g, rc_g = rc_g,pct_f =pct_f, sb_f=sb_f, rc_f=rc_f, easy_impact = easy_impact, hard_impact = hard_impact, abrupt_positive = abrupt_positive, abrupt_negative = abrupt_negative)

def del_viz(user_id, viz, current_viz):
    storage.delete(user_id+"/saved_viz/"+viz)
    if viz == current_viz:
        return 'not_set'
    else:
        return current_viz

@app.route('/login/', methods=['POST', 'GET'])
def login():
    check_session()
    if request.method == "POST":
        session.permanent = True
        user = request.form['email']
        email = request.form['email']
        password = request.form['password']
        try:
            email = auth.sign_in_with_email_and_password(email,password)
            auth.get_account_info(email['idToken'])
            app.secret_key = email['idToken']
            #session["user"] = email['localId']
            session["user_id"] = email['localId']
            if session.get('user_default_catalog') is None:
                session["user_default_catalog"] = "not_set"
            if session.get('user_default_config') is None:
                session["user_default_config"] = "not_set"
            if session.get('grade_sab_rec_factors') is None:
                session["grade_sab_rec_factors"] = [0.3,2,2]
            if session.get('frequency_sab_rec_factors') is None:
                session["frequency_sab_rec_factors"] = [0.3,40,40]
            if session.get('easy_hard_factors') is None:
                session["easy_hard_factors"] = [2,2]
            if session.get('factors') is None:
                session["factors"] = [2,2]
            if session.get('hard_passes') is None:
                session["hard_passes"] = []
            if session.get('easy_passes') is None:
                session["easy_passes"] = []
            if session.get('subjects') is None:
                session["subjects"] = []
            if session.get('turmas') is None:
                session["turmas"] = []
            if session.get('semoffers') is None:
                session["semoffers"] = []
            if session.get('credits') is None:
                session["credits"] = []

            session["current_catalogo"] = 'not_set'
            session["current_config"] = 'not_set'
            session["current_viz"] = 'not_set'
        except:
            return "Please check your credentials"
        return redirect(url_for("user"))
    else:
        simulation_Enabled = False
        return render_template("login.html", simulation_Enabled = simulation_Enabled)

@app.route('/user/')
def user():
    check_session()
    if "user_id" in session:
        simulation_Enabled = check_for_current_Catalog_and_Config(session)
        return redirect(url_for("home"))
        #return ('<h1>'+user+'</h1>')
    else:
        return redirect(url_for("login"))



@app.route('/importacoes/', methods=['GET','POST'])
def importacoes():
    check_session()
    if "user_id" in session:
        simulation_Enabled = check_for_current_Catalog_and_Config(session)
        global simulation_lock
        user_uid = session["user_id"]
        #return ('<h1>'+user+'</h1>')
        if request.method == 'POST':
            if request.files:
                if "importar" in request.form:
                    timestamp = datetime.now().strftime("%d-%m_%I-%M-%S_%p")
                    try:
                        catalogo = request.files['catalogo']
                        #catalogo.save('app/imports/uploads/catalogo.xml')
                        storage.child(user_uid+"/"+timestamp+"_catalogo.xml").put(catalogo)

                    except UnboundLocalError:
                        pass
                    try:
                        configs = request.files['configs']
                        #configs.save('app/imports/uploads/configs.xml')

                        storage.child(user_uid+"/"+timestamp+"_configs.xml").put(configs)

                        #current_config = storage.child(user_uid+"/configs.xml").download("usr/"+user_uid[-5:]+"/"+timestamp+"current_config.xml")
                        #current_catalogo = storage.child(user_uid+"/configs.xml").download("usr/"+user_uid[-5:]+"/"+user_uid[-5:]+"current_catalogo.xml")
                    except UnboundLocalError:
                        pass
            else:
                if "set_catalogo" in request.form:
                    catalog_current = request.form["catalog_current"]
                    session["current_catalogo"] = catalog_current
                    session["subjects"], session["turmas"], session["prereqs"], session["semoffers"], session["credits"], session["cat_info"], session["prereq_report"] = set_catalogo_as_default(storage, user_uid, session["current_catalogo"])
                if "set_config" in request.form:
                    config_current = request.form["config_current"]
                    session["current_config"] = config_current
                    session["params"], session["factors"], session["hard_passes"], session["easy_passes"], session["generic_config_info"] = set_config_as_default(storage, user_uid, session["current_config"])
                if "del_catalogo" in request.form:
                    catalog_current = request.form["catalog_current"]
                    session["current_catalogo"] = del_catalogo(user_uid, catalog_current, session["current_catalogo"])

                if "del_config" in request.form:
                    config_current = request.form["config_current"]
                    session["current_config"] = del_config(user_uid, config_current, session["current_config"])
                available_catalog_imports, available_config_imports = list_imports(user_uid)
                simulation_Enabled = check_for_current_Catalog_and_Config(session)
                return render_template("importacoes.html", available_catalog_imports = available_catalog_imports, available_config_imports = available_config_imports, user_default_config = session["current_config"], user_default_catalog = session["current_catalogo"], simulation_Enabled = simulation_Enabled)
        available_catalog_imports, available_config_imports = list_imports(user_uid)
        return render_template("importacoes.html", simulation_Enabled = simulation_Enabled, available_catalog_imports = available_catalog_imports, available_config_imports = available_config_imports, user_default_config = session["current_config"], user_default_catalog = session["current_catalogo"])
    else:
        return redirect(url_for("login"))

def del_catalogo(user_id, catalogo, current_catalogo):
    storage.delete(user_id+"/"+catalogo)
    if catalogo == current_catalogo:
        return 'not_set'
    else:
        return current_catalogo

def del_config(user_id, config, current_config):
    storage.delete(user_id+"/"+config)
    if config == current_config:
        return 'not_set'
    else:
        return current_config

def list_imports(user_id):
    all_imported_catalogs = []
    all_imported_configs = []
    all_files = storage.list_files()
    for file in all_files:
        full_file_path = storage.child(file.name).get_url(None)
        if user_id in full_file_path:
            if "config" in full_file_path:
                #https://firebasestorage.googleapis.com/v0/b/simulador-75b51.appspot.com/o/sEoW3983DKMgaEqnj5gjvh1cs462%2F05-08_03-05-34_AM_catalogo.xml?alt=media
                config_name = full_file_path[-39:-10]
                if config_name not in all_imported_configs:
                    all_imported_configs.append(config_name)
            if "catalogo" in full_file_path:
                catalog_name = full_file_path[-40:-10]
                if catalog_name not in all_imported_catalogs:
                    all_imported_catalogs.append(catalog_name)
    return all_imported_catalogs, all_imported_configs

def list_saved_viz(user_id):
    all_saved_viz = []
    all_imported_viz = []
    all_files = storage.list_files()
    for file in all_files:
        full_file_path = storage.child(file.name).get_url(None)
        if user_id in full_file_path:
            if "saved_viz" in full_file_path:
                viz_name = full_file_path[117:-10]
                if viz_name not in all_imported_viz:
                    all_imported_viz.append(viz_name)
    return all_imported_viz


@app.route('/reset_configs/')
def reset_configs():
    check_session()
    user_uid = session["user_id"]
    session["subjects"], session["turmas"], session["prereqs"], session["semoffers"], session["credits"], session["cat_info"], session["prereq_report"] = set_catalogo_as_default(storage, user_uid, session["current_catalogo"])
    session["params"], session["factors"], session["hard_passes"], session["easy_passes"], session["generic_config_info"] = set_config_as_default(storage, user_uid, session["current_config"])
    return redirect(url_for("importacoes"))

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

@app.route('/visualizacao/', methods=['GET','POST'])
@cross_origin()
def visualizacao():
    filename = None
    vizz_path_file = storage.child("sEoW3983DKMgaEqnj5gjvh1cs462/vizz/visualizacao (1).csv").get_url(None)
    #this is what vizz_path_file returns \/
    vizz_test = "https://firebasestorage.googleapis.com/v0/b/simulador-75b51.appspot.com/o/sEoW3983DKMgaEqnj5gjvh1cs462%2Fvizz%2Fvisualizacao%20%281%29.csv?alt=media"
    if request.method == 'POST':
        if "save_viz" in request.form:
            timestamp = "vis_"+ datetime.now().strftime("%d-%m_%I-%M-%S_%p")
            filename = request.form.get('filename')
            save_viz(storage, session["user_id"], session["current_viz"], timestamp, filename)
    else:
        filename = None
        timestamp = "vis_"+ datetime.now().strftime("%d-%m_%I-%M-%S_%p")
    return render_template("visualizacao.html", vizz_file = session["viz_path_file"], vizz_test = vizz_test, timestamp = timestamp)

@app.route('/disciplinas/', methods=['GET','POST'])
def disciplinas():
    check_session()
    if "user_id" in session:
        simulation_Enabled = check_for_current_Catalog_and_Config(session)
        if request.method == 'POST':
            if "new_subject" in request.form:
                new_subj = request.form.get('subject_to_be_Added')
                qty_turmas = request.form.get('qty_turmas')
                ideal_sem = request.form.get('ideal_sem')
                qty_credits = request.form.get('qty_credits')
                set_new_subject(session["subjects"], session["turmas"], session["semoffers"], session["credits"], new_subj, qty_turmas, ideal_sem, qty_credits)
                return render_template("disciplinas.html",  simulation_Enabled = simulation_Enabled, subjects = session["subjects"])
            if "remove_subjects" in request.form:
                subjects_to_remove = request.form.getlist('subj_rmv')
                for subject_removed in subjects_to_remove:
                    session["subjects"], session["turmas"], session["semoffers"], session["credits"] = del_subject(session["subjects"], session["turmas"], session["semoffers"], session["credits"], subject_removed)
                return render_template("disciplinas.html",  simulation_Enabled = simulation_Enabled, subjects = session["subjects"])
            if "set_net_classes_no" in request.form:
                subject_to_change_classes_no = request.form.get('subject_to_change_Classes_No')
                new_classes_no = request.form.get('new_classes_no')
                session["subjects"], session["turmas"] = edit_turmas(session["subjects"], session["turmas"], subject_to_change_classes_no, new_classes_no)
                return render_template("disciplinas.html",  simulation_Enabled = simulation_Enabled, subjects = session["subjects"], user_default_catalog = session["user_default_catalog"], user_default_config = session["user_default_config"])
        else:
            return render_template("disciplinas.html",  simulation_Enabled = simulation_Enabled, subjects = session["subjects"], user_default_catalog = session["user_default_catalog"], user_default_config = session["user_default_config"])
    else:
        return redirect(url_for("login"))

def check_for_current_Catalog_and_Config(session):
    simulation_Enabled = False
    handle = ""
    available_catalog_imports = []
    available_config_imports = []
    if "user_id" in session:
        if "current_catalogo" in session and "current_config" in session:
            available_catalog_imports, available_config_imports = list_imports(session["user_id"])
            if session["current_catalogo"] in available_catalog_imports and session["current_config"] in available_config_imports:
                #check if used params are populated
                if "params" in session and "factors" in session and "hard_passes" in session and "easy_passes" in session and "generic_config_info" in session and "subjects" in session and "turmas" in session and "prereqs" in session and "semoffers"  in session and "credits" in session and "cat_info" in session and "prereq_report" in session and "grade_sab_rec_factors" in session and "frequency_sab_rec_factors" in session and "easy_hard_factors" in session:
                    simulation_Enabled = True
    return simulation_Enabled

@app.route('/pre_requisitos/', methods=['GET','POST'])
def pre_requisitos():
    check_session()
    global simulation_lock
    selected_subjects = []
    allprereqs = []
    teste = []
    prereqs_dict = {}
    if "user_id" in session:
        simulation_Enabled = check_for_current_Catalog_and_Config(session)
        if request.method == 'POST':
            if "list_prereqs" in request.form:
                selected_subjects = request.form.getlist('selected_subjects')
                for selected_subject in selected_subjects:
                    teste.append(list_prereqs(session["prereqs"], session["subjects"], selected_subject))
                prereqs_dict = dict(zip(selected_subjects, teste))
                return render_template("pre_requisitos.html", simulation_Enabled = simulation_Enabled, selected_subjects = selected_subjects,  teste = teste, subjects = session["subjects"], prereqs_dict = prereqs_dict, user_default_catalog = session["user_default_catalog"], user_default_config = session["user_default_config"])
            if "add_subject" in request.form:
                subject_to_add_as_prereq = request.form.get('subj')
                subject_to_have_prereq_added = request.form.get('pre_req_will_be_Added')
                add_prereqs(session["subjects"], session["prereqs"], subject_to_have_prereq_added, subject_to_add_as_prereq)
                return render_template("pre_requisitos.html", simulation_Enabled = simulation_Enabled, selected_subjects = selected_subjects,  teste = teste, subjects = session["subjects"], prereqs_dict = prereqs_dict, user_default_catalog = session["user_default_catalog"], user_default_config = session["user_default_config"])
            if "clear_prereqs" in request.form:
                subject_to_remove_prereqs = request.form.get('pre_req_will_be_Added')
                clear_prereqs(session["subjects"], session["prereqs"], subject_to_remove_prereqs)
                return render_template("pre_requisitos.html", simulation_Enabled = simulation_Enabled, selected_subjects = selected_subjects,  teste = teste, subjects = session["subjects"], prereqs_dict = prereqs_dict, user_default_catalog = session["user_default_catalog"], user_default_config = session["user_default_config"])
        else:
            return render_template("pre_requisitos.html", simulation_Enabled = simulation_Enabled, subjects = session["subjects"],  teste = teste, user_default_catalog = session["user_default_catalog"], user_default_config = session["user_default_config"])
    else:
        return redirect(url_for("login"))

@app.route('/parametros/', methods=['GET','POST'])
def parametros():
    check_session()
    global simulation_lock
    if "user_id" in session:
        simulation_Enabled = check_for_current_Catalog_and_Config(session)
        param_names = listar_parametros(session["params"])
        single_param_dict = {}
        params_dict = {}
        selected_params = []
        if request.method == 'POST':
            if "get_params_info" in request.form:
                selected_params = request.form.getlist('selected_params')
                for selected_param in selected_params:
                    single_param_dict = {}
                    single_param_dict = list_params_values(session["params"], selected_param)
                    params_dict[selected_param] = single_param_dict
            if "edit_name" in request.form:
                selected_param = request.form.get('param_to_edit')
                new_value = request.form.get('new_param_value')
                session["params"] = change_parameter_name(session["params"], selected_param, new_value)
            if "edit_min" in request.form:
                try:
                    selected_param = request.form.get('param_to_edit')
                    new_value = request.form.get('new_param_value')
                    session["params"] = change_parameter_min(session["params"], selected_param, new_value)
                except ValueError:
                    pass
            if "edit_max" in request.form:
                try:
                    selected_param = request.form.get('param_to_edit')
                    new_value = request.form.get('new_param_value')
                    params = change_parameter_max(session["params"], selected_param, new_value)
                except ValueError:
                    pass
            if "edit_qty" in request.form:
                try:
                    selected_param = request.form.get('param_to_edit')
                    new_value = request.form.get('new_param_value')
                    session["params"] = change_parameter_qty(session["params"], selected_param, new_value)
                except ValueError:
                    pass
            if "del_param" in request.form:
                try:
                    removed_param_name = request.form.get('param_to_edit')
                    session["params"] = del_parameter(session["params"], removed_param_name)
                    param_names = listar_parametros(session["params"])
                    return render_template("parametros.html", simulation_Enabled = simulation_Enabled, param_names = param_names)
                except ValueError:
                    pass
            if "new_param" in request.form:
                try:
                    param_names = listar_parametros(session["params"])
                    new_param_name = request.form.get('new_param_name')
                    new_param_qtd = request.form.get('new_param_qtd')
                    new_param_min = request.form.get('new_param_min')
                    new_param_max = request.form.get('new_param_max')
                    selected_param = new_param_name
                    session["params"] = set_new_parameter(session["params"], new_param_name, new_param_qtd, new_param_min, new_param_max)
                    single_param_dict = list_params_values(session["params"], selected_param)
                    params_dict[selected_param] = single_param_dict
                    param_names = listar_parametros(session["params"])
                except ValueError:
                    pass
            return render_template("parametros.html", simulation_Enabled = simulation_Enabled, param_names = param_names,  params_dict = params_dict, selected_params = selected_params, selected_param = selected_param, user_default_catalog = session["user_default_catalog"], user_default_config = session["user_default_config"])
        else:
            return render_template("parametros.html", simulation_Enabled = simulation_Enabled, param_names = param_names,  params_dict = params_dict, user_default_catalog = session["user_default_catalog"], user_default_config = session["user_default_config"])
    else:
        return redirect(url_for("login"))

@app.route('/configuracoes_adicionais/', methods=['GET','POST'])
def configuracoes_adicionais():
    check_session()
    if "user_id" in session:
        simulation_Enabled = check_for_current_Catalog_and_Config(session)
        if request.method == 'POST':
            if "set_easy_hard_passes" in request.form:
                min_value = request.form.get('easy_factor')
                max_value = request.form.get('hard_factor')
                if len(session["factors"]) > 0:
                    session["factors"].clear()
                session["factors"].append(float(min_value))
                session["factors"].append(float(max_value))
            if "set_sab_rec_grade" in request.form:
                positive_impact = request.form.get('positive_impact')
                negative_impact = request.form.get('negative_impact')
                students_percentage = request.form.get('grade_percentage_affected')
                if len(session["grade_sab_rec_factors"]) > 0:
                    session["grade_sab_rec_factors"].clear()
                session["grade_sab_rec_factors"].append(float(students_percentage))
                session["grade_sab_rec_factors"].append(float(positive_impact))
                session["grade_sab_rec_factors"].append(float(negative_impact))
            if "set_sab_rec_frequency" in request.form:
                positive_impact = request.form.get('positive_impact')
                negative_impact = request.form.get('negative_impact')
                students_percentage = request.form.get('frequency_percentage_affected')
                if len(session["frequency_sab_rec_factors"]) > 0:
                    session["frequency_sab_rec_factors"].clear()
                session["frequency_sab_rec_factors"].append(float(students_percentage))
                session["frequency_sab_rec_factors"].append(float(positive_impact))
                session["frequency_sab_rec_factors"].append(float(negative_impact))
            if "set_abrupt_alteration" in request.form:
                positive_impact = request.form.get('easy_hard_factors_easy')
                negative_impact = request.form.get('easy_hard_factors_hard')
                if len(session["easy_hard_factors"]) > 0:
                    session["easy_hard_factors"].clear()
                session["easy_hard_factors"].append(float(negative_impact))
                session["easy_hard_factors"].append(float(positive_impact))
            if "remove_hard_pass" in request.form:
                hard_passes_to_remove = request.form.getlist('hp_rmv')
                for hard_pass in hard_passes_to_remove:
                    session["hard_passes"] = [x for x in session["hard_passes"] if x != hard_pass]
            if "remove_easy_pass" in request.form:
                easy_passes_to_remove = request.form.getlist('ep_rmv')
                for easy_pass in easy_passes_to_remove:
                    session["easy_passes"] = [x for x in session["easy_passes"] if x != easy_pass]
            return render_template("configuracoes_adicionais.html", simulation_Enabled = simulation_Enabled, user_default_catalog = session["user_default_catalog"], user_default_config = session["user_default_config"], hard_passes = session["hard_passes"], easy_passes = session["easy_passes"])
        return render_template("configuracoes_adicionais.html", simulation_Enabled = simulation_Enabled, user_default_catalog = session["user_default_catalog"], user_default_config = session["user_default_config"], hard_passes = session["hard_passes"], easy_passes = session["easy_passes"])
    else:
        return redirect(url_for("login"))



@app.route("/simulacao/", methods=['POST', 'GET'])
def simulacao():
    simulation_Enabled = check_for_current_Catalog_and_Config(session)
    check_session()
    if "user_id" in session:
    #     if request.method == "POST":
    #a
    #         user = request.form['email']
    #         email = request.form['email']
    #         password = request.form['password']
    #         try:
    #             email = auth.sign_in_with_email_and_password(email,password)
    #             auth.get_account_info(email['idToken'])
    #             session["user"] = email['idToken']
    #             user_uid = email['localId']
    #         except:
    #             return "Please check your credentials"
    #         return redirect(url_for("user"))
    #     global simulation_lock
        #delete all temp viz before simulation
        simulation, simulation_array, tempo_max_integralizacao, qtde_de_disciplinas_semestre_impar, qtde_de_disciplinas_semestre_par, subss, students_data, prereqs_report_export, std_records, std_info_export, toolExport, students, subs_final_export = new_simulation(session["params"], session["factors"], session["hard_passes"], session["easy_passes"], session["generic_config_info"], session["subjects"], session["turmas"], session["prereqs"], session["semoffers"], session["credits"], session["cat_info"], session["prereq_report"], session["grade_sab_rec_factors"], session["frequency_sab_rec_factors"], session["easy_hard_factors"])
        timestamp = datetime.now().strftime("%d-%m_%I-%M-%S_%p")
        session["viz_path_file"], session["current_viz"] = allocate_temp_viz(toolExport,students, subs_final_export, session["generic_config_info"], storage, timestamp, session["user_id"])

        #with open("app/imports/log.txt", "r") as f:
            #content = f.read()
        a_file = open("app/imports/log.txt", "r")
        lines = a_file.readlines()
        return render_template('simulacao.html', simulation_Enabled = simulation_Enabled, simulation_table=[simulation.to_html(classes='table table-striped table-sm', header="false",justify="left", border="0")], prereqs_table=[prereqs_report_export.to_html(classes='table table-striped table-sm', header="false",justify="left", border="0", index=False)],std_records_table=[std_records.to_html(classes='table table-striped table-sm', header="false",justify="left", border="0", index=False)],std_info_table=[std_info_export.to_html(classes='table table-striped table-sm', header="false",justify="left", border="0", index=False)],params = session["subjects"],  lines = lines, user_default_catalog = session["user_default_catalog"], user_default_config = session["user_default_config"], toolExport = toolExport)
    else:
        return redirect(url_for("login"))

@app.route("/logout/")
def logout():
    check_session()
    global simulation_lock
    auth.current_user = None
    if "user_id" in session:
        flash("Usuário desconectado", "info")
    session.pop("user_id",None)
    simulation_lock = True
    return redirect(url_for("login"))


@app.route('/download_curso/')
def download_curso():
    with open("app/exports/curso.csv") as fp:
        csv = fp.read()
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=curso.csv"})

@app.route('/download_info_std/')
def download_info_std():
    with open("app/exports/info_std.csv") as fp:
        csv = fp.read()
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=info_std.csv"})

@app.route('/download_historicos/')
def download_historicos():
    with open("app/exports/historicos.csv") as fp:
        csv = fp.read()
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=historicos.csv"})

@app.route('/download_prerequisitos/')
def download_prerequisitos():
    with open("app/exports/prerequisitos.csv") as fp:
        csv = fp.read()
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=prerequisitos.csv"})

@app.route('/download_visualizacao/')
def projeto_rafael():
    with open("app/exports/export_visualizacao.csv") as fp:
        csv = fp.read()
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=visualizacao.csv"})

@app.route('/download_all')
def download_all():
    zipf = zipfile.ZipFile('Name.zip','w', zipfile.ZIP_DEFLATED)
    for root,dirs, files in os.walk('exports/'):
        for file in files:
            zipf.write('app/'+file)
    zipf.close()
    return send_file('Name.zip',
            mimetype = 'zip',
            attachment_filename= 'Name.zip',
            as_attachment = True)

if __name__ == '__main__':
    app.run(debug=True)
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.context_processor
def utility_functions():
    def print_in_console(message):
        print(message)

    return dict(mdebug=print_in_console)



#functions being called
def generate_graphic_sab_rec_grade(sab_rec_factors):
    percentage_fig = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = sab_rec_factors[0]*100,
        mode = "gauge+number",
        title = {'text': "Alunos afetados"},
        delta = {'reference': 0},
        gauge = {'axis': {'range': [0, 100]},
                 'bar': {'color': 'gray'},
                 'steps' : [
                     {'range': [-100, 100], 'color': "rgba(0,0,0,0)"}]}))
    percentage_fig.update_layout(
        margin=dict(l=0, r=0, t=70, b=70),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    percentage = percentage_fig.to_html(default_height=250)
    sab_fig = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = sab_rec_factors[1]*-1,
        mode = "gauge+number",
        title = {'text': "Sabotagem"},
        delta = {'reference': 0},
        gauge = {'axis': {'range': [0, -10]},
                 'bar': {'color': 'gray'},
                 'steps' : [
                     {'range': [-10, 10], 'color': "rgba(0,0,0,0)"}]}))
    sab_fig.update_layout(
        margin=dict(l=0, r=0, t=70, b=70),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    sab = sab_fig.to_html(default_height=250)
    rec_fig = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = sab_rec_factors[2],
        mode = "gauge+number",
        title = {'text': "Recuperação"},
        delta = {'reference': 0},
        gauge = {'axis': {'range': [0, 10]},
                 'bar': {'color': 'gray'},
                 'steps' : [
                     {'range': [-10, 10], 'color': "rgba(0,0,0,0)"}]}))
    rec_fig.update_layout(
        margin=dict(l=0, r=0, t=70, b=70),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    rec = rec_fig.to_html(default_height=250)
    return percentage, sab, rec

def generate_graphic_sab_rec_frequency(sab_rec_factors):
    percentage_fig = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = sab_rec_factors[0]*100,
        mode = "gauge+number",
        title = {'text': "Alunos afetados"},
        delta = {'reference': 0},
        gauge = {'axis': {'range': [0, 100]},
                 'bar': {'color': 'gray'},
                 'steps' : [
                     {'range': [-100, 100], 'color': "rgba(0,0,0,0)"}]}))
    percentage_fig.update_layout(
        margin=dict(l=0, r=0, t=70, b=70),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    percentage = percentage_fig.to_html(default_height=250)
    sab_fig = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = sab_rec_factors[1]*-1,
        mode = "gauge+number",
        title = {'text': "Sabotagem"},
        delta = {'reference': 0},
        gauge = {'axis': {'range': [0, -100]},
                 'bar': {'color': 'gray'},
                 'steps' : [
                     {'range': [-100, 100], 'color': "rgba(0,0,0,0)"}]}))
    sab_fig.update_layout(
        margin=dict(l=0, r=0, t=70, b=70),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    sab = sab_fig.to_html(default_height=250)
    rec_fig = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = sab_rec_factors[2],
        mode = "gauge+number",
        title = {'text': "Recuperação"},
        delta = {'reference': 0},
        gauge = {'axis': {'range': [0, 100]},
                 'bar': {'color': 'gray'},
                 'steps' : [
                     {'range': [-100, 100], 'color': "rgba(0,0,0,0)"}]}))
    rec_fig.update_layout(
        margin=dict(l=0, r=0, t=70, b=70),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    rec = rec_fig.to_html(default_height=250)
    return percentage, sab, rec

def generate_graphic_easy_hard_subjects(easy_hard_factors):
    rec_fig = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = easy_hard_factors[0],
        mode = "gauge+number",
        title = {'text': "Impacto positivo"},
        delta = {'reference': 0},
        gauge = {'axis': {'range': [0, 10]},
                 'bar': {'color': 'gray'},
                 'steps' : [
                     {'range': [-10, 10], 'color': "rgba(0,0,0,0)"}]}))
    rec_fig.update_layout(
        margin=dict(l=0, r=0, t=70, b=70),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    rec = rec_fig.to_html(default_height=250)
    sab_fig = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = easy_hard_factors[1]*-1,
        mode = "gauge+number",
        title = {'text': "Impacto negativo"},
        delta = {'reference': 0},
        gauge = {'axis': {'range': [0, -10]},
                 'bar': {'color': 'gray'},
                 'steps' : [
                     {'range': [-10, 10], 'color': "rgba(0,0,0,0)"}]}))
    sab_fig.update_layout(
        margin=dict(l=0, r=0, t=70, b=70),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    sab = sab_fig.to_html(default_height=250)
    return rec, sab

def generate_graphic_abrupt_alteration(easy_hard_factors):
    rec_fig = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = easy_hard_factors[0],
        mode = "gauge+number",
        title = {'text': "Impacto positivo"},
        delta = {'reference': 0},
        gauge = {'axis': {'range': [0, 10]},
                 'bar': {'color': 'gray'},
                 'steps' : [
                     {'range': [-10, 10], 'color': "rgba(0,0,0,0)"}]}))
    rec_fig.update_layout(
        margin=dict(l=0, r=0, t=70, b=70),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    rec = rec_fig.to_html(default_height=250)
    sab_fig = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = easy_hard_factors[1]*-1,
        mode = "gauge+number",
        title = {'text': "Impacto negativo"},
        delta = {'reference': 0},
        gauge = {'axis': {'range': [0, -10]},
                 'bar': {'color': 'gray'},
                 'steps' : [
                     {'range': [-10, 10], 'color': "rgba(0,0,0,0)"}]}))
    sab_fig.update_layout(
        margin=dict(l=0, r=0, t=70, b=70),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    sab = sab_fig.to_html(default_height=250)
    return rec, sab
