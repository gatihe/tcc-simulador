from flask import Flask, redirect, url_for, render_template, request, session, flash, send_file, Response
import pyrebase
from datetime import datetime
from datetime import timedelta
import numpy as np
import pandas as pd
from app.new_engine import *
from app.input_handling import *
import os
import random
import time
import datetime
import xml.etree.ElementTree as ET

config = {
    "apiKey": "AIzaSyDaNLLMVZgXPenWO3JMGjKt9TtIEcfDGkk",
    "authDomain": "simulador-75b51.firebaseapp.com",
    "databaseURL": "https://simulador-75b51.firebaseio.com",
    "projectId": "simulador-75b51",
    "storageBucket": "simulador-75b51.appspot.com",
    "messagingSenderId": "381390670054",
    "appId": "1:381390670054:web:a376551235a8d4f88b9327",
    "measurementId": "G-ZH6T8K1388",
    "serviceAccount": "app/imports/configs/simulador-75b51-firebase-adminsdk-cv8yl-ee6529fce6.json"
    }
firebase = pyrebase.initialize_app(config)

auth = firebase.auth()
storage = firebase.storage()
user_uid = ''

app = Flask(__name__)
a = False
app.secret_key="hello"
app.permanent_session_lifetime = timedelta(minutes=30)
simulation_lock = True
params =[]
factors=[]
hard_passes=[]
easy_passes=[]
generic_config_info=[]
subjects=[]
turmas=[]
prereqs=[]
semoffers=[]
credits=[]
cat_info=[]
prereq_report=[]
email = ''
user_default_files = ['not_set','not_set']



def empty_session():
    if auth.current_user is None:
        session.pop("user",None)
    return

@app.route("/")
def home():
    global user_default_files
    global simulation_lock
    if user_uid in session:
            return render_template('index.html',array_test = [0,2,4,6], simulation_lock = simulation_lock, user_default_files = user_default_files, uid = user_uid)
    return render_template('index.html',array_test = [0,2,4,6], simulation_lock = simulation_lock, user_default_files = user_default_files, uid = user_uid)

@app.route('/login/', methods=['POST', 'GET'])
def login():
    global user_uid
    global simulation_lock
    global email
    if request.method == "POST":
        session.permanent = True
        user = request.form['email']
        email = request.form['email']
        password = request.form['password']
        try:
            email = auth.sign_in_with_email_and_password(email,password)
            auth.get_account_info(email['idToken'])
            user_uid = email['localId']
            #session["user"] = email['localId']
            session[user_uid] = email['localId']
            print(user_uid)
        except:
            return "Please check your credentials"
        return redirect(url_for("user"))
    else:
        if user_uid in session:
            return redirect(url_for("user"))
        return render_template("login.html",simulation_lock = simulation_lock)

@app.route('/user/')
def user():
    global user_uid
    global simulation_lock
    if user_uid in session:
        return redirect(url_for("home"))
        #return ('<h1>'+user+'</h1>')
    else:
        return redirect(url_for("login"))



@app.route('/importacoes/', methods=['GET','POST'])
def importacoes():
    global simulation_lock
    global params
    global factors
    global hard_passes
    global easy_passes
    global generic_config_info
    global subjects
    global turmas
    global prereqs
    global semoffers
    global credits
    global cat_info
    global prereq_report
    global email
    global user_default_files
    global storage
    available_config_imports = []
    available_catalogo_imports = []
    if user_uid in session:
        print(session)
        user = session[user_uid]
        global simulation_lock
        available_config_imports, available_catalogo_imports = list_imports(user_uid, user_default_files)
        #return ('<h1>'+user+'</h1>')
        if request.method == 'POST':
            if request.files:
                if "importar" in request.form:
                    timestamp = datetime.datetime.now().strftime("%d-%m_%I-%M-%S_%p")
                    try:
                        catalogo = request.files['catalogo']
                        #catalogo.save('app/imports/uploads/catalogo.xml')
                        storage.child(user_uid+"/"+timestamp+"_catalogo.xml").put(catalogo)
                        print(user_uid)
                        print('importou')
                    except UnboundLocalError:
                        pass
                    try:
                        configs = request.files['configs']
                        #configs.save('app/imports/uploads/configs.xml')
                        print(user_uid)
                        storage.child(user_uid+"/"+timestamp+"_configs.xml").put(configs)
                        print('importou')
                        #current_config = storage.child(user_uid+"/configs.xml").download("usr/"+user_uid[-5:]+"/"+timestamp+"current_config.xml")
                        #current_catalogo = storage.child(user_uid+"/configs.xml").download("usr/"+user_uid[-5:]+"/"+user_uid[-5:]+"current_catalogo.xml")
                    except UnboundLocalError:
                        pass
                    available_config_imports, available_catalogo_imports = list_imports(user_uid,user_default_files)
                    return render_template("importacoes.html", catalogo = catalogo, configs = configs, simulation_lock = simulation_lock, available_config_imports = available_config_imports, available_catalogo_imports = available_catalogo_imports, user_default_files = user_default_files)
            if "del_catalogo" in request.form:
                catalogo = request.form['current_catalogo']
                delete_catalogo(catalogo, user_uid)
            if "del_config" in request.form:
                config = request.form['current_config']
                delete_config(config, user_uid)
            if "set_current_catalogo" in request.form:
                current_catalogo = request.form['current_catalogo']
                user_default_files[0] = current_catalogo
                available_config_imports, available_catalogo_imports = list_imports(user_uid, user_default_files)
            if "set_current_config" in request.form:
                current_config = request.form['current_config']
                user_default_files[1] = current_config
                available_config_imports, available_catalogo_imports = list_imports(user_uid, user_default_files)
            available_config_imports, available_catalogo_imports = list_imports(user_uid,user_default_files)
            return render_template("importacoes.html", simulation_lock = simulation_lock, available_config_imports = available_config_imports, available_catalogo_imports = available_catalogo_imports, user_default_files = user_default_files)
        return render_template("importacoes.html", simulation_lock = simulation_lock, available_config_imports = available_config_imports, available_catalogo_imports = available_catalogo_imports, user_default_files = user_default_files)
    else:
        return redirect(url_for("login"))

@app.route('/reset_configs/')
def reset_configs():
    global simulation_lock
    global user_uid
    global params
    global factors
    global hard_passes
    global easy_passes
    global generic_config_info
    global subjects
    global turmas
    global prereqs
    global semoffers
    global credits
    global cat_info
    global prereq_report
    global user_default_files
    subjects, turmas, prereqs, semoffers, credits, cat_info, prereq_report, params, factors, hard_passes, easy_passes, generic_config_info = reset_all(subjects, turmas, prereqs, semoffers, credits, cat_info, prereq_report, params, factors, hard_passes, easy_passes, generic_config_info)
    return render_template("disciplinas.html", simulation_lock = simulation_lock, subjects = subjects)



@app.route('/disciplinas/', methods=['GET','POST'])
def disciplinas():
    global simulation_lock
    global user_uid
    global params
    global factors
    global hard_passes
    global easy_passes
    global generic_config_info
    global subjects
    global turmas
    global prereqs
    global semoffers
    global credits
    global cat_info
    global prereq_report
    global user_default_files
    if "user" in session:
        user = session["user"]
        #return render_template("disciplinas.html", params = subjects, simulation_lock = simulation_lock)
        if request.method == 'POST':
            if "new_subject" in request.form:
                new_subj = request.form.get('subject_to_be_Added')
                qty_turmas = request.form.get('qty_turmas')
                ideal_sem = request.form.get('ideal_sem')
                qty_credits = request.form.get('qty_credits')
                set_new_subject(subjects, turmas, semoffers, credits, new_subj, qty_turmas, ideal_sem, qty_credits)
                return render_template("disciplinas.html", simulation_lock = simulation_lock, subjects = subjects, user_default_files = user_default_files)
            if "remove_subjects" in request.form:
                subjects_to_remove = request.form.getlist('subj_rmv')
                for subject_removed in subjects_to_remove:
                    subjects, turmas, semoffers, credits = del_subject(subjects, turmas, semoffers, credits, subject_removed)
                return render_template("disciplinas.html", simulation_lock = simulation_lock, subjects = subjects, user_default_files = user_default_files)
            if "set_net_classes_no" in request.form:
                subject_to_change_classes_no = request.form.get('subject_to_change_Classes_No')
                new_classes_no = request.form.get('new_classes_no')
                subjects, turmas = edit_turmas(subjects, turmas, subject_to_change_classes_no, new_classes_no)
                return render_template("disciplinas.html", simulation_lock = simulation_lock, subjects = subjects, user_default_files = user_default_files)
        else:
            return render_template("disciplinas.html", simulation_lock = simulation_lock, subjects = subjects, user_default_files = user_default_files)
    else:
        return redirect(url_for("login"))

@app.route('/pre_requisitos/', methods=['GET','POST'])
def pre_requisitos():
    global simulation_lock
    global user_uid
    global params
    global factors
    global hard_passes
    global easy_passes
    global generic_config_info
    global subjects
    global turmas
    global prereqs
    global semoffers
    global credits
    global cat_info
    global prereq_report
    global user_default_files
    selected_subjects = []
    allprereqs = []
    teste = []
    prereqs_dict = {}
    if "user" in session:
        user = session["user"]
        if request.method == 'POST':
            if "list_prereqs" in request.form:
                selected_subjects = request.form.getlist('selected_subjects')
                for selected_subject in selected_subjects:
                    teste.append(list_prereqs(prereqs, subjects, selected_subject))
                prereqs_dict = dict(zip(selected_subjects, teste))
                return render_template("pre_requisitos.html", selected_subjects = selected_subjects, simulation_lock = simulation_lock, teste = teste, subjects = subjects, prereqs_dict = prereqs_dict, user_default_files = user_default_files)
            if "add_subject" in request.form:
                subject_to_add_as_prereq = request.form.get('subj')
                subject_to_have_prereq_added = request.form.get('pre_req_will_be_Added')
                add_prereqs(subjects, prereqs, subject_to_have_prereq_added, subject_to_add_as_prereq)
                return render_template("pre_requisitos.html", selected_subjects = selected_subjects, simulation_lock = simulation_lock, teste = teste, subjects = subjects, prereqs_dict = prereqs_dict, user_default_files = user_default_files)
            if "clear_prereqs" in request.form:
                subject_to_remove_prereqs = request.form.get('pre_req_will_be_Added')
                clear_prereqs(subjects, prereqs, subject_to_remove_prereqs)
                return render_template("pre_requisitos.html", selected_subjects = selected_subjects, simulation_lock = simulation_lock, teste = teste, subjects = subjects, prereqs_dict = prereqs_dict, user_default_files = user_default_files)
        else:
            return render_template("pre_requisitos.html", subjects = subjects, simulation_lock = simulation_lock, teste = teste)
    else:
        return redirect(url_for("login"))

@app.route('/parametros/', methods=['GET','POST'])
def parametros():
    global simulation_lock
    global user_uid
    global params
    global factors
    global hard_passes
    global easy_passes
    global generic_config_info
    global subjects
    global turmas
    global prereqs
    global semoffers
    global credits
    global cat_info
    global prereq_report
    global user_default_files
    param_names = listar_parametros(params)
    single_param_dict = {}
    params_dict = {}
    selected_params = []
    if "user" in session:
        user = session["user"]
        if request.method == 'POST':
            if "get_params_info" in request.form:
                selected_params = request.form.getlist('selected_params')
                print(selected_params)
                for i in selected_params:
                    print (i)
                for selected_param in selected_params:
                    print(selected_param)
                    single_param_dict = {}
                    single_param_dict = list_params_values(params, selected_param)
                    params_dict[selected_param] = single_param_dict
                    print(params_dict)
            if "edit_name" in request.form:
                selected_param = request.form.get('param_to_edit')
                new_value = request.form.get('new_param_value')
                params = change_parameter_name(params, selected_param, new_value)
            if "edit_min" in request.form:
                try:
                    selected_param = request.form.get('param_to_edit')
                    new_value = request.form.get('new_param_value')
                    params = change_parameter_min(params, selected_param, new_value)
                except ValueError:
                    pass
            if "edit_max" in request.form:
                try:
                    selected_param = request.form.get('param_to_edit')
                    new_value = request.form.get('new_param_value')
                    print(selected_param)
                    params = change_parameter_max(params, selected_param, new_value)
                except ValueError:
                    pass
            if "edit_qty" in request.form:
                try:
                    selected_param = request.form.get('param_to_edit')
                    new_value = request.form.get('new_param_value')
                    params = change_parameter_qty(params, selected_param, new_value)
                except ValueError:
                    pass
            if "del_param" in request.form:
                try:
                    removed_param_name = request.form.get('param_to_edit')
                    params = del_parameter(params, removed_param_name)
                    param_names = listar_parametros(params)
                    return render_template("parametros.html", param_names = param_names, simulation_lock = simulation_lock, user_default_files = user_default_files)
                except ValueError:
                    pass
            if "new_param" in request.form:
                try:
                    param_names = listar_parametros(params)
                    new_param_name = request.form.get('new_param_name')
                    new_param_qtd = request.form.get('new_param_qtd')
                    new_param_min = request.form.get('new_param_min')
                    new_param_max = request.form.get('new_param_max')
                    selected_param = new_param_name
                    params = set_new_parameter(params, new_param_name, new_param_qtd, new_param_min, new_param_max)
                    single_param_dict = list_params_values(params, selected_param)
                    params_dict[selected_param] = single_param_dict
                    param_names = listar_parametros(params)
                except ValueError:
                    pass
            return render_template("parametros.html", param_names = param_names, simulation_lock = simulation_lock, params_dict = params_dict, selected_params = selected_params, selected_param = selected_param, user_default_files = user_default_files)
        else:
            return render_template("parametros.html", param_names = param_names, simulation_lock = simulation_lock, params_dict = params_dict, user_default_files = user_default_files)
    else:
        return redirect(url_for("login"))

@app.route('/configuracoes_adicionais/', methods=['GET','POST'])
def configuracoes_adicionais():
    global simulation_lock
    global user_uid
    global params
    global factors
    global hard_passes
    global easy_passes
    global generic_config_info
    global subjects
    global turmas
    global prereqs
    global semoffers
    global credits
    global cat_info
    global prereq_report
    global grade_sab_rec_factors
    global frequency_sab_rec_factors
    global easy_hard_factors
    global user_default_files
    if "user" in session:
        user = session["user"]
        if request.method == 'POST':
            if "set_easy_hard_passes" in request.form:
                min_value = request.form.get('easy_factor')
                max_value = request.form.get('hard_factor')
                factors.clear()
                factors.append(float(min_value))
                factors.append(float(max_value))
                print(factors)
            if "set_sab_rec_grade" in request.form:
                positive_impact = request.form.get('positive_impact')
                negative_impact = request.form.get('negative_impact')
                students_percentage = request.form.get('grade_percentage_affected')
                grade_sab_rec_factors.clear()
                grade_sab_rec_factors.append(float(students_percentage))
                grade_sab_rec_factors.append(float(positive_impact))
                grade_sab_rec_factors.append(float(negative_impact))
            if "set_sab_rec_frequency" in request.form:
                positive_impact = request.form.get('positive_impact')
                negative_impact = request.form.get('negative_impact')
                students_percentage = request.form.get('frequency_percentage_affected')
                frequency_sab_rec_factors.clear()
                frequency_sab_rec_factors.append(float(students_percentage))
                frequency_sab_rec_factors.append(float(positive_impact))
                frequency_sab_rec_factors.append(float(negative_impact))
            if "set_abrupt_alteration" in request.form:
                positive_impact = request.form.get('easy_hard_factors_easy')
                negative_impact = request.form.get('easy_hard_factors_hard')
                easy_hard_factors.clear()
                easy_hard_factors.append(float(negative_impact))
                easy_hard_factors.append(float(positive_impact))
            return render_template("configuracoes_adicionais.html",simulation_lock = simulation_lock, user_default_files = user_default_files)
        return render_template("configuracoes_adicionais.html",simulation_lock = simulation_lock, user_default_files = user_default_files)
    else:
        return redirect(url_for("login"))



@app.route("/simulacao/", methods=['POST', 'GET'])
def simulacao():
    global params
    global factors
    global hard_passes
    global easy_passes
    global generic_config_info
    global subjects
    global turmas
    global prereqs
    global semoffers
    global credits
    global cat_info
    global prereq_report
    if "user" in session:
        user = session["user"]
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
        simulation, simulation_array, tempo_max_integralizacao, qtde_de_disciplinas_semestre_impar, qtde_de_disciplinas_semestre_par, subss, students_data, prereqs_report_export, std_records, std_info_export, file = new_simulation(params, factors, hard_passes, easy_passes, generic_config_info, subjects, turmas, prereqs, semoffers, credits, cat_info, prereq_report, grade_sab_rec_factors, frequency_sab_rec_factors, easy_hard_factors)
        #with open("app/imports/log.txt", "r") as f:
            #content = f.read()
        a_file = open("app/imports/log.txt", "r")
        lines = a_file.readlines()
        return render_template('simulacao.html', simulation_table=[simulation.to_html(classes='table table-striped table-sm', header="false",justify="left", border="0", index=False)], prereqs_table=[prereqs_report_export.to_html(classes='table table-striped table-sm', header="false",justify="left", border="0", index=False)],std_records_table=[std_records.to_html(classes='table table-striped table-sm', header="false",justify="left", border="0", index=False)],std_info_table=[std_info_export.to_html(classes='table table-striped table-sm', header="false",justify="left", border="0", index=False)],params = subjects, simulation_lock = simulation_lock, lines = lines)
    else:
        return redirect(url_for("login"))

@app.route("/logout/")
def logout():
    empty_session()
    global simulation_lock
    auth.current_user = None
    if "user" in session:
        user = session["user"]
        flash("you have been logged out", "info")
    session.pop("user",None)
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


def delete_catalogo(catalogo, user_uid):
    global storage
    global user_default_files
    all_files = storage.list_files()
    for files in all_files:
        full_file_path = storage.child(files.name).get_url(None)
        print(full_file_path)
        if user_uid in full_file_path:
            if catalogo in full_file_path:
                storage.delete(user_uid+"/"+catalogo)
                if catalogo in user_default_files:
                    user_default_files[0] = 'not_set'
    return

def delete_config(config, user_uid):
    global storage
    global user_default_files
    all_files = storage.list_files()
    for files in all_files:
        full_file_path = storage.child(files.name).get_url(None)
        print(full_file_path)
        if user_uid in full_file_path:
            if config in full_file_path:
                storage.delete(user_uid+"/"+config)
                if config in user_default_files:
                    user_default_files[1] = 'not_set'
    return

def list_imports(user_uid, user_default_files):
    global storage
    global subjects
    global turmas
    global prereqs
    global semoffers
    global credits
    global cat_info
    global prereq_report
    global params
    global factors
    global hard_passes
    global easy_passes
    global generic_config_info
    all_files = storage.list_files()
    available_config_imports = []
    available_catalogo_imports = []
    for file in all_files:
        full_file_path = storage.child(file.name).get_url(None)
        print(full_file_path)
        directory_path = full_file_path[74:-10]
        # 74 + 3 (%2F)
        if user_uid in directory_path:
            file_name = full_file_path[77+len(user_uid):-10]
            print(file_name)
            if "config" in file_name:
                if file_name not in available_config_imports:
                    available_config_imports.append(file_name)
                    if file_name in user_default_files:
                        default_config_path = user_uid+"/"+file_name
                        default_config_path = default_config_path.replace('%2F','/')
                        params, factors, hard_passes, easy_passes, generic_config_info = set_config_as_default(storage, user_uid, default_config_path)
            if "catalogo" in file_name:
                if file_name not in available_catalogo_imports:
                    print(full_file_path)
                    print(file_name)
                    available_catalogo_imports.append(file_name)
                    if file_name in user_default_files:
                        default_catalogo_path = user_uid+"/"+file_name
                        default_catalogo_path = default_catalogo_path.replace('%2F','/')
                        subjects, turmas, prereqs, semoffers, credits, cat_info, prereq_report = set_catalogo_as_default(storage, user_uid, default_catalogo_path)

    return available_config_imports, available_catalogo_imports


def list_imports(user_uid, user_default_files):
    global storage
    global subjects
    global turmas
    global prereqs
    global semoffers
    global credits
    global cat_info
    global prereq_report
    global params
    global factors
    global hard_passes
    global easy_passes
    global generic_config_info
    all_files = storage.list_files()
    available_config_imports = []
    available_catalogo_imports = []
    for file in all_files:
        full_file_path = storage.child(file.name).get_url(None)

        directory_path = full_file_path[74:-10]
        # 74 + 3 (%2F)
        if user_uid in directory_path:
            file_name = full_file_path[77+len(user_uid):-10]

            if "config" in file_name:
                if file_name not in available_config_imports:
                    available_config_imports.append(file_name)
                    if file_name in user_default_files:
                        default_config_path = user_uid+"/"+file_name
                        default_config_path = default_config_path.replace('%2F','/')
                        params, factors, hard_passes, easy_passes, generic_config_info = set_config_as_default(storage, user_uid, file_name)
            if "catalogo" in file_name:
                if file_name not in available_catalogo_imports:
                    available_catalogo_imports.append(file_name)
                    if file_name in user_default_files:
                        default_catalogo_path = user_uid+"/"+file_name
                        default_catalogo_path = default_catalogo_path.replace('%2F','/')
                        subjects, turmas, prereqs, semoffers, credits, cat_info, prereq_report = set_catalogo_as_default(storage, user_uid, file_name)

    return available_config_imports, available_catalogo_imports

# @app.route("/admin/")
# def admin():
#     if a:
#         return 'adm'
#     return redirect(url_for("user", name ="Admin!!!"))
#
# @app.route('/<name>/')
# def user(name):
#     return ('Hello '+name)

if __name__ == '__main__':
    app.run(debug=True)





#functions being called
