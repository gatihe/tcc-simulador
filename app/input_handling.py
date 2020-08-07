import os
from app.engine import *
#######INPUT ERROR HANDLING

####Special error types:
class Error(Exception):
    pass

#option not available
class NotInScope(Error):
    pass

#grade input impossible (x<0 or x>10)
class NotPossibleGrade(Error):
    pass

#maxgrade < mingrade
class InvalidMaxGrade(Error):
    pass

class DuplicateParameter(Error):
    pass

class InvalidParameter(Error):
    pass

class InvalidSubjectCode(Error):
    pass

class NotASubject(Error):
    pass

class NoPrereqs(Error):
    pass

####Check for error functions:
def save_viz(storage, user_uid, file_name, timestamp, filename):
    temp_dir = tempfile.TemporaryDirectory()
    viz_path_file = temp_dir.name+"/"+"temp_viz.csv"
    full_file_path = file_name
    full_file_path = full_file_path.replace('%2F','/')
    print(viz_path_file)
    print(full_file_path)
    current_viz = storage.child(full_file_path).download(viz_path_file)
    if filename is not None:
        target_path = user_uid+"/saved_viz/"+filename+".csv"
    else:
        target_path = user_uid+"/saved_viz/"+timestamp+".csv"
    storage.child(target_path).put(viz_path_file)
    return




def set_catalogo_as_default(storage, user_uid, file_name):
    temp_dir = tempfile.TemporaryDirectory()
    catalog_path_file = temp_dir.name+"/"+"default_catalog.xml"
    full_file_path = user_uid+"/"+file_name
    full_file_path = full_file_path.replace('%2F','/')
    print(catalog_path_file)
    print(full_file_path)
    current_config = storage.child(full_file_path).download(catalog_path_file)
    filename=current_config

    if filename is not None or file_name is not 'not_set':
        try:
            f=open(catalog_path_file, 'r')
            subjects = getting_subjects_config_from_file(catalog_path_file)
            turmas = getting_turmas_config_from_file(catalog_path_file)
            prereqs = getting_prereqs_config_from_file(catalog_path_file)
            semoffers = getting_semoffer_config_from_file(catalog_path_file)
            credits = getting_credits_config_from_file(catalog_path_file)
            cat_info = getting_catalog_info_from_file(catalog_path_file)
            prereq_report = getting_prereq_report_from_file(catalog_path_file)
            f.close()
            temp_dir.cleanup()
            importou_config = 1
            print(subjects)
        except SyntaxError:
            print("\nProblema identificado ao importar. Verifique seu arquivo "+filename+".")
            pass
        except IOError:
            print("\nProblema identificado ao importar. Verifique seu arquivo "+filename+".")
            pass

    else:
        print("\nImportação de catálogo cancelada.")
    return subjects, turmas, prereqs, semoffers, credits, cat_info, prereq_report

def set_config_as_default(storage, user_uid, file_name):
    temp_dir = tempfile.TemporaryDirectory()
    config_path_file = temp_dir.name+"/"+"default_config.xml"
    full_file_path = user_uid+"/"+file_name
    full_file_path = full_file_path.replace('%2F','/')
    print(config_path_file)
    print(full_file_path)
    current_config = storage.child(full_file_path).download(config_path_file)
    filename=current_config

    if filename is not None or file_name is not 'not_set':
        try:
            f=open(config_path_file, 'r')
            params = getting_params_config_from_file(config_path_file)
            factors = getting_factors_config_from_file(config_path_file)
            hard_passes = getting_hard_pass_from_file(config_path_file)
            easy_passes = getting_easy_pass_from_file(config_path_file)
            generic_config_info = getting_generic_info_from_file(config_path_file)
            f.close()
            temp_dir.cleanup()
            importou_config = 1
            print(params)
        except SyntaxError:
            print("\nProblema identificado ao importar. Verifique seu arquivo "+filename+".")
            pass
        except IOError:
            print("\nProblema identificado ao importar. Verifique seu arquivo "+filename+".")
            pass

    else:
        print("\nImportação de catálogo cancelada.")
    return params, factors, hard_passes, easy_passes, generic_config_info


def reset_all(subjects, turmas, prereqs, semoffers, credits, cat_info, prereq_report, params, factors, hard_passes, easy_passes, generic_config_info):

    return subjects, turmas, prereqs, semoffers, credits, cat_info, prereq_report, params, factors, hard_passes, easy_passes, generic_config_info


def listar_parametros(params):
    p = 0
    q = 0
    param_names = []
    print('Parâmetros configurados:\n')
    while(p<len(params)/4):
        while(q < len(params)):
            print("Parametro: " + str(params[q]))
            param_names.append(params[q])
            q = q +1
            print("Mínimo: " + str(params[q]))
            q = q +1
            print("Máximo: " + str(params[q]))
            q = q+1
            print("Qtde de alunos: " + str(params[q])+"\n\n")
            q = q+1
        p = p + 1
    return param_names



def clear_prereqs(subjects, prereqs, subject_to_remove_prereqs):
    if subject_to_remove_prereqs is not '':
        subject_occurrences = [ i for i in range(len(prereqs)) if prereqs[i] == subject_to_remove_prereqs and i%2 != 0]
        x = len(subject_occurrences)-1
        while(x>-1):
            del prereqs[subject_occurrences[x]-1:subject_occurrences[x]+1]
            x = x -1
    else:
        cls()
        print("Operação cancelada.")
    return prereqs


def add_prereqs(subjects, prereqs, subject_to_add_prereq, subject_new_prereq):
    try:
        if subject_to_add_prereq is not '':
            if subject_to_add_prereq not in subjects:
                raise NotASubject
            if subject_new_prereq is not '':
                if subject_new_prereq not in subjects:
                    raise NotASubject
                prereqs.append(subject_new_prereq)
                prereqs.append(subject_to_add_prereq)
                cls()
                #TODO: Implementar list_prereqs_for_subject()
                print("Pré-requisito adicionado com sucesso.")
            else:
                cls()
                print("Operação cancelada.")
                subject_new_prereq = ''
                pass
        else:
            cls()
            print("Operação cancelada.")
    except NotASubject:
        print("Disciplina não existe")
    except ValueError:
        print("Disciplina inválida")
    return prereqs

def list_prereqs(prereqs, subjects, subject_to_list_prereqs):
    prerequisitos = []
    try:
        subject_to_list_prereqs = subject_to_list_prereqs.upper()
        if subject_to_list_prereqs not in subjects:
            raise NotASubject
        if subject_to_list_prereqs not in prereqs:
            raise NoPrereqs
        cls()
        first_occurrence = prereqs.index(subject_to_list_prereqs)
        subject_occurrences = [ i for i in range(len(prereqs)) if prereqs[i] == subject_to_list_prereqs and i%2 != 0]
        x = len(subject_occurrences)-1
        individual_prereqs = []
        while(x>-1):
            individual_prereqs.append(prereqs[subject_occurrences[x]-1])
            x = x -1
        if len(individual_prereqs) != 0 and individual_prereqs[0] ==None:
            prerequisitos.append('teste')
        if len(individual_prereqs) != 0:
            prerequisitos.append(individual_prereqs)
        else:
            prerequisitos.append('Não há pre-requisitos')
        return prerequisitos
    except ValueError:
        print("Insira um valor válido.")
    except NotASubject:
        print("Disciplina não existe")
    except NoPrereqs:
        print("Não há pré-requisitos para a disciplina")


def list_params_values(params, param_name):
    param_index = params.index(param_name)
    dict = {}
    dict["name"] = params[param_index]
    dict["max_grade"] = params[param_index+2]
    dict["min_grade"] = params[param_index+1]
    dict["qty_students"] = params[param_index+3]
    return dict

def change_parameter_name(params, selected_param, new_value):
    index_to_change = params.index(selected_param)
    params[index_to_change] = new_value
    return params

def change_parameter_max(params, selected_param, new_value):
    index_to_change = params.index(selected_param) + 2
    params[index_to_change] = round(float(new_value),2)
    return params

def change_parameter_min(params, selected_param, new_value):
    index_to_change = params.index(selected_param) + 1
    params[index_to_change] = round(float(new_value),2)
    return params

def change_parameter_qty(params, selected_param, new_value):
    index_to_change = params.index(selected_param) + 3
    params[index_to_change] = int(new_value)
    return params

def edit_turmas(subjects, turmas, subject_to_edit_turmas, new_turmas_qtt):
    try:
        if subject_to_edit_turmas is not '':
            if subject_to_edit_turmas in subjects:
                index_to_edit_turmas = subjects.index(subject_to_edit_turmas)
                turmas[index_to_edit_turmas] = int(new_turmas_qtt)
                print("Quantidade de turmas alterada com sucesso. Nova quantidade de turmas para "+str(subject_to_edit_turmas)+": "+str(turmas[index_to_edit_turmas]))
            else:
                print("Disciplina não encontrada.")
    except ValueError:
        print("Valor inválido. Operação cancelada.")
    return subjects, turmas

def del_subject(subjects, turmas, semoffers, credits, subject_removed):
    try:
        if subject_removed is not '':
            if subject_removed in subjects:
                subject_index = subjects.index(subject_removed)
                turmas.pop(subject_index)
                semoffers.pop(subject_index)
                credits.pop(subject_index)
                subjects.remove(subject_removed)
                print("\n\nDisciplina removida com sucesso.")
            else:
                print("Erro. Disciplina não encontrada.")
        else:
            cls()
            print("Operação cancelada.")
    except ValueError:
        print("Operação inválida.")
    return subjects, turmas, semoffers, credits

def set_new_subject(subjects, turmas, semoffers, credits,new_subject, no_turmas, semoffer, qtt_credit):
    try:
        if len(new_subject) != 5:
            raise InvalidSubjectCode
        new_subject = new_subject.upper()
        print(new_subject)
        int(new_subject[-3:])
        if new_subject not in subjects and new_subject is not '':
            subjects.append(new_subject)
            turmas.append(abs(int(no_turmas)))
            semoffers.append(abs(int(semoffer)))
            credits.append(abs(int(qtt_credit)))
            print("Disciplina adicionada com sucesso.")
        elif new_subject in subjects:
            print("Disciplina já cadastrada.")
    except ValueError:
        print("Valor inválido. Operação cancelada.")
    except InvalidSubjectCode:
        print("Código de disciplina inválido. Operação cancelada.")
    return subjects, turmas, semoffers, credits

def set_new_parameter(params, new_param_name, new_param_qtd, new_param_min, new_param_max):
    try:
        if new_param_name not in params and new_param_name is not '':
            float(new_param_min)
            float(new_param_max)
            int(new_param_qtd)
            params.append(new_param_name)
            params.append(float(new_param_min))
            params.append(float(new_param_max))
            params.append(int(new_param_qtd))

        elif new_param_name in params:
            raise DuplicateParameter
        else:
            cls()
            print("Operação cancelada")
    except DuplicateParameter:
        cls()
        print("Este parâmetro já existe")
    except ValueError:
        cls()
        print("Valor inserido inválido")
    return params

def del_parameter(params, removed_param_name):
    try:
        if removed_param_name not in params and removed_param_name is not '':
            raise InvalidParameter
        elif removed_param_name is '':
            print("Operação cancelada.")
        elif removed_param_name in params:
            rm_index = [i for i, x in enumerate(params) if x == str(removed_param_name)]
            print(rm_index[0])
            params.pop(rm_index[0]+3)
            params.pop(rm_index[0]+2)
            params.pop(rm_index[0]+1)
            params.pop(rm_index[0])
            cls()
            print("Parâmetro removido com sucesso.")
    except InvalidParameter:
        cls()
        print("Parâmetro não existe.")
    return params

def change_parameter(params):
    try:
        altered_param_name = input("Insira o nome do parâmetro à ser alterado ou enter para cancelar. \n\nEntrada do usuário: ")
        if altered_param_name not in params and altered_param_name is not '':
            raise InvalidParameter
        elif altered_param_name is '':
            print("Operação cancelada.")
        elif altered_param_name in params:
            cls()
            print("Parâmetro encontrado.")
            rm_index = [i for i, x in enumerate(params) if x == str(altered_param_name)]
            paramindex = rm_index[0]
            param_new_name = input("Insira o novo nome para o parâmetro ou ENTER para manter o nome.\nEntrada do usuário: ")
            param_new_min = input("Insira a nova nota mínima para o parâmetro ou -1 para mantê-la.\nEntrada do usuário: ")
            float(param_new_min)
            param_new_max = input("Insira a nova nota máxima para o parâmetro ou -1 para mantê-la.\nEntrada do usuário: ")
            float(param_new_max)
            param_new_std = input("Insira a nova quantidade de alunos para o parâmetro ou -1 para mantê-la.\nEntrada do usuário: ")
            int(param_new_std)
            ## gravando alterações
            if param_new_name is not '':
                params[paramindex] = param_new_name
            if float(param_new_min) != -1.0:
                params[paramindex+1] = float(param_new_min)
            if float(param_new_max) != -1.0:
                params[paramindex+2] = float(param_new_max)
            if int(param_new_std) != -1:
                params[paramindex+3] = int(param_new_std)
    except ValueError:
        print("Valor inválido. Operação cancelada.")
    except InvalidParameter:
        print("Parâmetro não existe.")
    return params



def check_input_in_scope (a,b,user_input):
    try:
        menu_input = int(user_input)
        if menu_input < a or menu_input > b:
            raise NotInScope
    except NotInScope:
        new_param_checklist = 1
        print("Insira uma opção válida")
        ask_for_input_to_Continue()
    except ValueError:
        new_param_checklist = 1
        print("Insira uma opção válida")
        ask_for_input_to_Continue()
    return
########

#check for int between params
def check_for_int(a):
    try:
        menu_input = int(a)
    except ValueError:
        new_param_checklist = 1
        print("Insira uma opção válida!")
    return


def ask_for_input_to_Continue():
    try:
        input("Pressione qualquer tecla para continuar.")
    except SyntaxError:
        pass
    return


def cls():
    os.system('cls' if os.name=='nt' else 'clear')
