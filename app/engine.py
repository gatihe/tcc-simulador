import pandas as pd
import numpy as np
import random
import os
import time
import datetime
import xml.etree.ElementTree as ET
import tempfile
import shutil
from pathlib import Path
import json

#defining parameters
# bast_param = [0,5] #ba prefix for below average student
# avst_param = [5,7] #av prefix for average student
# aast_param = [7,10] #aa prefix for above average student
# sorted_sabotage = [3, 3]
# semoffers = []
# cat_info = []
# hardPasses = []
# easyPasses = []
# anos_inicio = []
#defining parameters 2
#menu_keep = 0
#params = ["Below Average", 0, 5, 10, "Average", 5, 7, 10, "Above Average", 7, 10, 10]
#params_total = len(params)/4
#factors = []
#students_data = []
maxCompletionTime = 12
students = []
#ja_simulou = 0
#ja_importou = 0
#importou_config = 0
#realFinalToolExport = []
#subjectsFinalExport = []
#barrosToolExport = []
#gradeSabRecFactors = [0,0,0] #will withdraw from total grade, should be editable in flask
#frequencySabRecFactors = [0,0,0] #will withdraw from total frequency, should be editable in flask
#factorsEasyHard = [0,0]
from app import *

#Defining Subjects



#prereqs = ["SI100", "SI250"]

def scrambled(orig):
    dest = orig[:]
    random.shuffle(dest)
    return dest


def exporting_to_tool(simulationArray, evenSemSubjAmount,oddSemSubjAmount, subjectsAsHeader):
    toolExportLine = []
    toolExportFull = []
    subsExportLine = []
    realFinalToolExport = []
    #getting all subjects
    semesterCounter = 1
    newInitialSemesterIndex = 0
    newFinalSemesterIndex = -1
    semesterCounter = 1
    beginingSemester = 0
    endSemester = 0

    while (semesterCounter<=maxCompletionTime):
        newInitialSemesterIndex = newFinalSemesterIndex + 1
        if semesterCounter % 2 == 0:
            newFinalSemesterIndex = newFinalSemesterIndex + (evenSemSubjAmount * 3) #3 = APENAS NOTA POR ISSO 1
        if semesterCounter % 2 != 0:
            newFinalSemesterIndex = newFinalSemesterIndex + (oddSemSubjAmount * 3)
        beginingSemester = newInitialSemesterIndex
        endSemester = newFinalSemesterIndex
        while (beginingSemester <= endSemester ):
            subsExportLine.append(subjectsAsHeader[beginingSemester+1]+"_"+str(semesterCounter))
            beginingSemester = beginingSemester + 3
        semesterCounter = semesterCounter + 1

    #passing all grades to array
    l = 0
    c = 1
    while (l < len(students)):
        c = 1
        toolExportLine = []
        while(c<len(subjectsAsHeader)):
            toolExportLine.append(simulationArray[l][c])
            c = c + 3
        toolExportFull.append(toolExportLine)
        l = l+1
    #cleaning subs with no students:
    finalExport = np.array(toolExportFull)
    columnsToCheck = []
    c = 0
    l = 0
    no_students = 0
    columnsToDelete = []
    by_columns = []
    while(c<len(toolExportFull[0])):
        l = 0
        columnsToCheck = []
        while(l<len(students)):
            columnsToCheck.append(toolExportFull[l][c])
            l = l+1
        by_columns.append(columnsToCheck)
        c = c +1

    subs_as_np = np.array(subsExportLine)
    l = 0
    c = 0

    while(l<len(by_columns)):
        if all(isinstance(item, str) for item in by_columns[l]) is True and by_columns[l][0] == '--':
            columnsToDelete.append(l)
        l = l+1
    subjectsFinalExport = np.delete(subs_as_np, columnsToDelete)
    realFinalToolExport = np.delete(finalExport, columnsToDelete, 1)
    l = 0
    c = 0
    while(l<len(students)):
        c = 0
        while(c<len(subjectsFinalExport)):
            if realFinalToolExport[l][c] == '--':
                realFinalToolExport[l][c] = 'undefined'
            else:
                realFinalToolExport[l][c] = float(realFinalToolExport[l][c])
            c = c+1
        l = l+1

    return realFinalToolExport, subjectsFinalExport


def sorteio_de_turmas_dificeis_e_faceis(subjects, maxCompletionTime, even_semester, odd_semester):
    #define how many subjects
    raffleEasyHard = []


    #set a number from 0 to 10
    amountOfOcurrences = random.randint(0,10)
    #cont 0 to 10:
    cont = 0
    while(cont<amountOfOcurrences):
        raffledSubject = subjects[random.randint(1,len(subjects))-1]
        raffleEasyHard.append(raffledSubject)
        if raffledSubject in even_semester:
            raffledSemester = random.randrange(2, maxCompletionTime +1, 2)
        if raffledSubject in odd_semester:
            raffledSemester = random.randrange(1, maxCompletionTime +1, 2)
        raffleEasyHard.append(raffledSemester)
        raffleEasyHard.append(random.randint(0,1))
        cont = cont+1
    #decide wheter its good (0) or bad (1)
    return raffleEasyHard

def sorteio_altera_desempenho(students):
    alteredStudentPerformances = []
    studentAmount = random.randint(0, len(students))
    affectedStudents = random.sample(students, studentAmount)

    alteredStudentPerformances.append(studentAmount)
    for student in affectedStudents:
        alteredStudentPerformances.append(student)
        alteredStudentPerformances.append(random.randint(0,1))
        alteredStudentPerformances.append(random.randint(2,6))
    return alteredStudentPerformances

def getting_subjects_config_from_file(filename):
    parsedSubjects = []
    tree = ET.parse(filename)
    root = tree.getroot()
    parsedSubjects = []
    for parsedSubjs in root.findall('subjects'):
        for subject in parsedSubjs.findall('subject'):
            for id in subject.findall('id'):
                parsedSubjects.append(id.text)
    return parsedSubjects

def getting_catalog_info_from_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    parsedCurriculumInfo = []
    for cat in root.findall('cat_info'):
        for courseIds in cat.findall('course_id'):
            parsedCurriculumInfo.append(int(courseIds.text))
        for year in cat.findall('year'):
            parsedCurriculumInfo.append(int(year.text))
        for maxYears in cat.findall('max_years'):
            parsedCurriculumInfo.append(int(maxYears.text))
    return parsedCurriculumInfo


def export_subjects(subjects,credits, cat_info):
    subjCredCatInfo = []
    j = 0
    while(j<len(subjects)):
        individualSubjInfoLine = []
        subjCredCatInfo.append(individualSubjInfoLine)
        individualSubjInfoLine.append(subjects[j])
        individualSubjInfoLine.append(cat_info[1])
        individualSubjInfoLine.append(credits[j])
        individualSubjInfoLine.append('N')
        j = j+1
    return subjCredCatInfo

def Convert(lst):
    res_dct = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
    return res_dct

def rank_students(crs_list):
    return positions

def export_student_data(students, maxCompletionTime, oddSemSubjAmount, evenSemSubjAmount, simulationArray, subjectsAsHeader, subjects, credits, startingYear, cat_info):
    l = 0
    students_data = []
    while (l<len(students)):
        c = 1
        individualStudentData = []
        individualStudentData.append(students[l])
        individualStudentData.append(0)
        newInitialSemesterIndex = 0
        newFinalSemesterIndex = -1
        semesterCounter = 1
        beginingSemester = 0
        endSemester = 0
        while (semesterCounter<=maxCompletionTime):
            newInitialSemesterIndex = newFinalSemesterIndex + 1
            if semesterCounter % 2 == 0:
                newFinalSemesterIndex = newFinalSemesterIndex + (evenSemSubjAmount * 3) #3 = TURMA, NOTA, FREQ
            if semesterCounter % 2 != 0:
                newFinalSemesterIndex = newFinalSemesterIndex + (oddSemSubjAmount * 3)
            beginingSemester = newInitialSemesterIndex
            endSemester = newFinalSemesterIndex
            while (beginingSemester <= endSemester ):
                if simulationArray[l][beginingSemester] != '--':
                    individualStudentData.append(subjectsAsHeader[beginingSemester+1])
                    individualStudentData.append(simulationArray[l][beginingSemester+1])
                    individualStudentData.append(simulationArray[l][beginingSemester+2])
                    individualStudentData.append(semesterCounter)
                    individualStudentData.append(credits[subjects.index(subjectsAsHeader[beginingSemester+1])])
                beginingSemester = beginingSemester + 3
            semesterCounter = semesterCounter + 1
        students_data.append(individualStudentData)
        l = l +1

    crs, med_crs, desv_padrao = calc_std_crs(students_data)

    info_std = []
    stdIndividualInfo = []
    l = 0
    while(l<len(students_data)):
        accomplishedCredits = 0
        stdIndividualInfo = []
        m = 0
        courseTotalCredits = 0
        while (m<len(credits)):
            courseTotalCredits = courseTotalCredits + credits[m]
            m = m +1
        j = 2


        #crp
        performanceCoefficient = crs[crs.index(students_data[l][j-2])+1]
        standardPerformanceCoefficient = ((performanceCoefficient - med_crs)/desv_padrao)


        stdIndividualInfo.append(students_data[l][j-2]) #RA                  (0)
        stdIndividualInfo.append(startingYear[0]) #ANOING             (1)
        stdIndividualInfo.append(2) #PINGR POR ENQUANTO SERA 2               (2)
        stdIndividualInfo.append(cat_info[1]) #DANOCAT = ANOCATALOGO         (3)
        stdIndividualInfo.append(cat_info[0]) #numero do CURSO               (4)
        stdIndividualInfo.append(startingYear[0]) #ANOING             (5)
        stdIndividualInfo.append(cat_info[1]) #ANO_CATALOGO = ANOCATALOGO    (6)
        stdIndividualInfo.append(round(crs[crs.index(students_data[l][j-2])+1],3)) #CR - VAI SER CALCULADO DEPOIS           (7)
        stdIndividualInfo.append(0) #CP -           (8)
        stdIndividualInfo.append(0) #CP FUTURO  (9)
        stdIndividualInfo.append(crs[crs.index(students_data[l][j-2])-1]) #POSICAO_ALUNO_NA_TURMA(10)
        stdIndividualInfo.append(round(standardPerformanceCoefficient,3)) #CR PADRAO - VAI SER CALCULADO DEPOIS    (11)
        stdIndividualInfo.append(round(med_crs,3)) #CR MEDIO - VAI SER CALCULADO DEPOIS    (12)
        stdIndividualInfo.append(round(desv_padrao,3)) #DESVIO_PADRAO_TURMA                     (13)
        stdIndividualInfo.append(len(students))  #TOTAL_ALUNOS_TURMA         (14)
        while(j<len(students_data[l])):
            if students_data[l][j+1] >= 5 and students_data[l][j+2] >= 75:
                accomplishedCredits = accomplishedCredits + students_data[l][j+4]
            j = j+5
        stdIndividualInfo[8] = round(accomplishedCredits/courseTotalCredits,3)
        stdIndividualInfo[9] = round(accomplishedCredits/courseTotalCredits,3)
        info_std.append(stdIndividualInfo)
        l = l+1

    return info_std, students_data

def calc_desvio_padrao():
    return desvio_padrao

def calc_cr(std_data):
    teste = get_students_records(students_data)
    print(teste)
    return teste

def calc_stdinfo(subjects, students, gradeslc, subjectsAsHeader):
    j = 0
    stdinfo = []
    while j < len(students):
        i = 0
        while i < len(subjectsAsHeader):

            i = i+1
        j = j+1
    return stdinfo

def getting_turmas_config_from_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    parsed_turmas = []
    for config_param in root.findall('subjects'):
        for subject in config_param.findall('subject'): # access each subject
            individual_qtde_turmas = subject.findall('classes_no')
            for x in individual_qtde_turmas:
                parsed_turmas.append(int(x.text))
    return parsed_turmas

def getting_credits_config_from_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    parsed_credits = []
    for config_param in root.findall('subjects'):
        for subject in config_param.findall('subject'): # access each subject
            individual_qtde_credits = subject.findall('credits')
            for x in individual_qtde_credits:
                parsed_credits.append(int(x.text))
    return parsed_credits

def getting_semoffer_config_from_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    parsed_semoffers = []
    for config_param in root.findall('subjects'):
        for subject in config_param.findall('subject'): # access each subject
            individual_semoffer = subject.findall('sem_offer')
            for x in individual_semoffer:
                parsed_semoffers.append(int(x.text))
    return parsed_semoffers

def getting_prereqs_config_from_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    parsed_prereqs = []
    for config_param in root.findall('subjects'):
        for subject in config_param.findall('subject'):
            individual_parsed_prereq = subject.findall('pre_reqs')
            individual_parsed_subject_id = subject.findall('id')
            for x in individual_parsed_prereq:
                    if x.text is not None:
                        #prereq to add is equal to pre_reqs tag's text inside the current subject being parsed
                        parsed_prereqs.append(x.text)
                        parsed_prereqs.append(individual_parsed_subject_id[0].text)
    return parsed_prereqs

def getting_prereq_report_from_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    parsed_anos_inicio = []
    report_prereqs = []
    for config_param in root.findall('subjects'):
        for subject in config_param.findall('subject'):

            individual_parsed_ano_inicio = subject.findall('ano_inicio')
            individual_parsed_ano_fim = subject.findall('ano_fim')
            individual_parsed_subject_id = subject.findall('id')
            individual_parsed_tipo_nivel_ativ_mae = subject.findall('tipo_nivel_atividade_mae')
            individual_parsed_prerequinho = subject.findall('pre_reqs')
            individual_parsed_cadeia_prereqs = subject.findall('no_cadeia_pre_requisito')
            individual_parsed_tipo_prereq = subject.findall('tipo_pre_requisito')
            individual_parsed_tipo_nivel_atividade_exigida = subject.findall('tipo_nivel_atividade_exigida')
            for (x,y,z,w,v, u) in zip(individual_parsed_prerequinho, individual_parsed_ano_inicio, individual_parsed_ano_fim, individual_parsed_cadeia_prereqs, individual_parsed_tipo_prereq, individual_parsed_tipo_nivel_atividade_exigida):
                    if x.text is not None:
                        parsed_anos_inicio = []
                        parsed_anos_inicio.append(individual_parsed_tipo_nivel_ativ_mae[0].text)
                        parsed_anos_inicio.append(individual_parsed_subject_id[0].text)
                        parsed_anos_inicio.append(y.text)
                        if z.text == '0':
                            parsed_anos_inicio.append('')
                        else:
                            parsed_anos_inicio.append(z.text)
                        parsed_anos_inicio.append(w.text)
                        parsed_anos_inicio.append(v.text)
                        parsed_anos_inicio.append(x.text)
                        parsed_anos_inicio.append(u.text)
                        report_prereqs.append(parsed_anos_inicio)
    return report_prereqs


def getting_hard_pass_from_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    parsed_hard_pass = []
    for config_param in root.findall('subj_dificulty'):
        for hp in config_param.findall('hard_pass'):
            individual_hp = hp.findall('sub_id')
            for x in individual_hp:
                    if x.text is not None:
                        parsed_hard_pass.append(x.text)
    return parsed_hard_pass

def getting_easy_pass_from_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    parsed_easy_pass = []
    for config_param in root.findall('subj_dificulty'):
        for hp in config_param.findall('easy_pass'):
            individual_ep = hp.findall('sub_id')
            for x in individual_ep:
                    if x.text is not None:
                        parsed_easy_pass.append(x.text)
    return parsed_easy_pass

def getting_params_config_from_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    parsed_params = []
    for config_param in root.findall('parameters'):
        for parameter in config_param.findall('parameter'):
            individual_parameter_name = parameter.findall('parameter_name')
            parsed_params.append(individual_parameter_name[0].text)
            individual_parameter_min_grade = parameter.findall('min_grade')
            parsed_params.append(float(individual_parameter_min_grade[0].text))
            individual_parameter_max_grade = parameter.findall('max_grade')
            parsed_params.append(float(individual_parameter_max_grade[0].text))
            individual_parameter_qtde_alunos = parameter.findall('qtde')
            parsed_params.append(int(individual_parameter_qtde_alunos[0].text))
    return parsed_params

def getting_factors_config_from_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    parsed_factors = []
    for config_factor in root.findall('factors'):
        easy_pass_factor = config_factor.findall('easy_pass_factor')
        parsed_factors.append(float(easy_pass_factor[0].text))
        hard_pass_factor = config_factor.findall('hard_pass_factor')
        parsed_factors.append(float(hard_pass_factor[0].text))
    return parsed_factors

def getting_generic_info_from_file(filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        parsed_info = []
        for generic_info in root.findall('generic_info'):
            ano_ingresso = generic_info.findall('ano_ingresso')
            parsed_info.append(int(ano_ingresso[0].text))
        return parsed_info

def listar_disciplinas():
    print("Disciplinas cadastradas:\n")
    for x in subjects:
        print(x)
    print("\n")
    return

def ask_for_input_to_Continue():
    try:
        input("Pressione qualquer tecla para continuar.")
    except SyntaxError:
        pass
    return

def get_students_records(students_data, startingYear):
    #EXPORT STUDENTS RECORDS
    all_records = []
    individual_grade_on_record = []
    j = 0
    while(j< len(students_data)):
      m = 2
      while(m<len(students_data[j])):
        individual_grade_on_record = []
        individual_grade_on_record.append(students_data[j][0]) #0
        individual_grade_on_record.append(int(startingYear[0]+(students_data[j][m+3]/2))) #1
        individual_grade_on_record.append(students_data[j][m+3])#2
        individual_grade_on_record.append(students_data[j][m])#3
        individual_grade_on_record.append(students_data[j][m+1])#4
        individual_grade_on_record.append(students_data[j][m+2])#5
        if students_data[j][m+1] >= 5 and students_data[j][m+2] >= 75:
            individual_grade_on_record.append(4)#6
        if students_data[j][m+1] < 5 and students_data[j][m+2] >= 75:
            individual_grade_on_record.append(5)#6
        if students_data[j][m+2] < 75:
            individual_grade_on_record.append(6)#6
        if individual_grade_on_record[6] == 4:
            individual_grade_on_record.append("APROVADO POR NOTA/CONCEITO E FREQ")
        if individual_grade_on_record[6] == 5:
            individual_grade_on_record.append("REPROVADO POR NOTA/CONCEITO")
        if individual_grade_on_record[6] == 6:
            individual_grade_on_record.append("REPROVADO POR FREQUENCIA")
        individual_grade_on_record.append(1)
        individual_grade_on_record.append(students_data[j][m+4])
        individual_grade_on_record.append('REGULAR')
        all_records.append(individual_grade_on_record)
        m = m+5
      j = j+1
    return all_records

def calc_std_crs(std_data):
    l = 0
    std_total_credits = 0
    std_total_grades = 0
    nici = 0
    contador = 0
    std_crs = []
    pure_crs = [] #only crs in order to calc class standard deviation
    while(l<len(std_data)):
        c = 2
        while(c<len(std_data[l])):
            individual_nici = 0
            std_total_credits = std_total_credits + std_data[l][c+4]
            std_total_grades = std_total_grades + std_data[l][c+1]
            individual_nici = std_data[l][c+1] * std_data[l][c+4]
            contador = contador + 1
            nici = nici + individual_nici
            c = c+5

        cr = round(nici/(10*std_total_credits),3)
        std_crs.append(std_data[l][0])
        std_crs.append(cr)
        pure_crs.append(cr)
        l = l+1


    to_rank = std_crs
    positions = []
    counter = 1
    while (len(to_rank)>1):
        c = 1
        stored_highest_value = -1
        stored_highest_index = -1
        while (c<len(to_rank)):
            if stored_highest_value < to_rank[c]:
                stored_highest_value = to_rank[c]
                stored_highest_index = c
            c = c +2
        positions.append(counter)
        positions.append(std_crs[stored_highest_index-1])
        positions.append(stored_highest_value)
        to_rank.pop(stored_highest_index)
        to_rank.pop(stored_highest_index-1)
        counter = counter+1

#average class cr
    m = 2
    crs_sum = 0
    instances = 0
    while(m<len(positions)):
        crs_sum = crs_sum+positions[m]
        instances = instances+1
        m = m+3

    med_crs = crs_sum/instances

    desv_padrao = np.std(pure_crs)
    desv_padrao = desv_padrao
    print("positions")
    print(positions)
    return positions, med_crs, desv_padrao
    #crs, med_crs, desv_padrao = calc_std_crs(students_data)


#counters and variable for grades creation
a = 0
b = 0
newgradeline = []
grade = []

#cut is the min grade to be aproved
cut = 5
even_semester = []
odd_semester = []

def check_for_prereq(subject_to_check, prereqs_list):
    cont1 = 0
    prereqs_for_subject = []
    while (cont1 < len(prereqs_list)):
        if prereqs_list[cont1] == subject_to_check and cont1 % 2 != 0:
            prereqs_for_subject.append(prereqs_list[cont1 - 1])
        cont1 = cont1 + 1
    return prereqs_for_subject

def arrange_semesters(subjects, semoffers, even_semester, odd_semester):
    i = 0
    j = 0
    even_semester.clear()
    odd_semester.clear()
    for i, j in zip(semoffers, subjects):
        if i % 2 == 0:
            even_semester.append(j)
        if i % 2 != 0:
            odd_semester.append(j)
    return


def sort_turmas(subjects, turmas):
    sub = 0
    run_turma = 0
    subs_with_turmas = []
    subs_with_turmas.clear()
    while (sub < len(subjects)):
        subs_with_turmas.append('Turma')
        subs_with_turmas.append(subjects[sub])
        subs_with_turmas.append('Freq')
        sub = sub +1
    return subs_with_turmas

def check_prereqs_are_ok(disciplinas, alreadyPassedSubjects): #if 1 ok if 0 not ok
    counter = 0
    ok_or_not = 1
    while(counter<len(disciplinas)):
        if disciplinas[counter] not in alreadyPassedSubjects:
            ok_or_not = 0
    return ok_or_not

def sort_sab_rec(students, maxCompletionTime, sab_rec_factors):
    qtty_students_to_be_affected = int(np.ceil(len(students)*sab_rec_factors[0]))
    counter = 0
    sab_rec = []
    students_to_be_affected = random.sample(students, qtty_students_to_be_affected)
    while (counter < len(students_to_be_affected)):
        positive_negative_sort = random.randint(0,1)
        initial_semester = random.randint(1,maxCompletionTime) #considering everyone is fine in first semester
        will_return_to_initial_state = random.randint(0,5) #0,1 wont go back, if > 1 then will go back to normal grades
        if will_return_to_initial_state <=1:
            final_semester = maxCompletionTime
        else:
            final_semester = initial_semester + random.randint(0,maxCompletionTime-initial_semester)

        sab_rec.append(students_to_be_affected[counter])
        sab_rec.append(initial_semester)
        sab_rec.append(final_semester)
        sab_rec.append(positive_negative_sort)

        counter = counter+1

    return sab_rec # = [sorted_student, initial_semester, final_semester, impact (0 for negative, 1 for positive)]

def get_report_sab_rec(sab_rec):
    student_qtty = len(sab_rec)/4
    counter = 3
    positive_qtty = 0
    negative_qtty = 0
    sab_rec_report = []
    while (counter < len(sab_rec)):
        if sab_rec[counter] == 0:
            negative_qtty = negative_qtty + 1
        if sab_rec[counter] == 1:
            positive_qtty = positive_qtty + 1
        counter = counter + 4
    sab_rec_report.append(student_qtty)
    sab_rec_report.append(negative_qtty)
    sab_rec_report.append(positive_qtty)
    return sab_rec_report


def new_simulation(params, factors, hardPasses, easyPasses, startingYear, subjects, turmas, prereqs, semoffers, credits, cat_info, prereqReport, gradeSabRecFactors, frequencySabRecFactors, factorsEasyHard):

    #ja_simulou = 1
    arrange_semesters(subjects, semoffers, even_semester, odd_semester)
    max_years = 6
#interperse semesters to create an offer grid
    all_subs = []
    all_subs.clear()
    i = 0
    while (i < 6):
        for odd_sem in odd_semester:
            all_subs.append(odd_sem)
        for even_sem in even_semester:
            all_subs.append(even_sem)
        i = i+1
    #print(all_subs)
    subjectsAsHeader = []
    subjectsAsHeader.clear()
    subjectsAsHeader = sort_turmas(all_subs, turmas)



    grade.clear()
    students.clear()
    params_sort = [x for x in params if not isinstance(x, str)] #returns params as [param1_min_grade, param1_max_grade, param1_qty_students, param2min_grade,....]



    #st_total will count how many students should be created for each parameter based on configs
    st_total = 0
    counterX = 3
    while(counterX < len(params)):
        total = params[counterX]
        st_total = st_total + total
        counterX = counterX + 4
    #creating students and grades
#counter for students ids creation
    i = 0
    j = 2

    while(i < st_total):
        newstudent = random.randint(100000,199999)
        #excluding duplicates
        if newstudent not in students:
            students.append(newstudent)
            i = i+1
    #now grades
    while(j<len(params_sort)):
        a = 0
        while(a < params_sort[j]):
            b = 0
            newgradeline = []
            grade.append(newgradeline)
            while(b < len(subjectsAsHeader)):
                #gen_grade = round(random.uniform(params_sort[j-2],params_sort[j-1]),2)
                gen_grade = -1
                newgradeline.append(gen_grade)
                b = b +1
            a = a +1
        j = j + 3

    ##this code snippet creates an array [subj, credits] that will be used to compose "pending" array
    m = 0
    subj_credits = []
    subj_credits.clear()
    while(m<len(subjects)):
        subj_credits.append(subjects[m])
        subj_credits.append(credits[m])
        m = m+1


#emptying values and sorting classes (turmas)
    l = 0
    while(l < len(students)):
        c = 0
        while (c < len(subjectsAsHeader)):
            if subjectsAsHeader[c] in subjects:
                classInstance = subjects.index(subjectsAsHeader[c])
                sorteio_de_turma = 0
                raffledClass = random.randint(0,turmas[classInstance]-1)
                raffledClass = raffledClass + 65
                grade[l][c-1] = chr(raffledClass)
            c = c + 1
        l = l+1

    l = 0
    c = 0
    creditsLimit = 28
    #grades_to_handle = []
    alreadyPassedSubjects = []
    pendingSubjects = []
    evenSemSubjAmount = len(even_semester)
    oddSemSubjAmount = len(odd_semester)
    subjectAtributesQty = 8 #nome, turma, nota, creditos, semestre de oferta, liberado
    currentlyEnrolledCredits = 0
    currentSemester = []
    maxCompletionTime = 12
    line = []
    alldata = []
    parametersDistribuitionOverStdQty = []
    all_grades = []


    raffledStdd = random.randint(0, len(students)-1)
    gradesRaffleSabRec = sort_sab_rec(students, maxCompletionTime,gradeSabRecFactors)#0.5 aleatory, will be editable in flask interface
    frequencyRaffleSabRec = sort_sab_rec(students, maxCompletionTime, frequencySabRecFactors)#0.3 aleatory, will be editable in flask interface


    easyHardSubjects = sorteio_de_turmas_dificeis_e_faceis(subjects, maxCompletionTime, even_semester, odd_semester)

    #distributing parameters according to amount of students
    #2 on parameter1 and 1 on parameter2 =
    # = [parameter1 min, parameter1 max, parameter1 min, parameter1 max, parameter2 min, parameter2 max]
    counterX = 2
    while(counterX < len(params_sort)):
        counterY = 0
        while(counterY<params_sort[counterX]):
            parametersDistribuitionOverStdQty.append(params_sort[counterX-2])
            parametersDistribuitionOverStdQty.append(params_sort[counterX-1])
            counterY = counterY + 1
        counterX = counterX + 3

    paramListCounter = 0




    l = 0
    while(l<len(students)):
        #applying prereqs
        semInitialIndex = 0
        semFinalIndex = -1
        beginingSemester = 0
        semCounter = 1
        line.clear()
        pendingSubjects.clear()
        c = 1
        alreadyPassedSubjects.clear()
        subjCredIndex = 0
        #grades_to_handle.clear()

        while(c<len(subjectsAsHeader)):
            pendingSubjects.append(subjectsAsHeader[c]) #name
            pendingSubjects.append(grade[l][c-1]) #class
            pendingSubjects.append(grade[l][c]) #grade
            subjCredIndex = subj_credits.index(subjectsAsHeader[c])
            pendingSubjects.append(subj_credits[subjCredIndex+1]) #credits
            if subjectsAsHeader[c] in even_semester:
                pendingSubjects.append(2) #semester of offer, 1 odd, 2 even
            else:
                pendingSubjects.append(1)
            pendingSubjects.append(1) #able to enroll or not (0 is no and set as default, 1 is yes)
            pendingSubjects.append(-1) #frequency
            #if true grade will be impacted
            pendingSubjects.append(students[l])
            c = c +3

        j = 0
        #instancias_eb101 = [i for i,d in enumerate(pendingSubjects) if d=='EB101']
        #instancias_eb102 = [i for i,d in enumerate(pendingSubjects) if d=='EB102']
        while(semCounter<=maxCompletionTime):
            semInitialIndex = semFinalIndex + 1
            if semCounter % 2 == 0:
                semFinalIndex = semFinalIndex + (evenSemSubjAmount * subjectAtributesQty)
            if semCounter % 2 != 0:
                semFinalIndex = semFinalIndex + (oddSemSubjAmount * subjectAtributesQty)

            #go trough pending subjects included in semester counter
            beginingSemester = semInitialIndex
            endSemester = semFinalIndex
            currentSemester.clear()
            #dividing offers by semester
            while(beginingSemester<=endSemester):
                currentSemester.append(pendingSubjects[beginingSemester])
                beginingSemester = beginingSemester + 1

            #blocking subjects without prereqs done or that student has already been approved
            subjCounter = 0
            while(subjCounter<len(currentSemester)):
                if currentSemester[subjCounter] in alreadyPassedSubjects:
                    currentSemester[subjCounter + 5] = 0
                subjCounter = subjCounter + subjectAtributesQty
            subjCounter = 0
            while(subjCounter<len(currentSemester)):
                individualPrereqs = check_for_prereq(currentSemester[subjCounter], prereqs)
                if (len(individualPrereqs)>0):
                    novo_contador = 0
                    while(novo_contador<len(individualPrereqs)):
                        if individualPrereqs[novo_contador] not in alreadyPassedSubjects:
                            currentSemester[subjCounter+5] = 0
                        novo_contador = novo_contador + 1
                subjCounter = subjCounter + subjectAtributesQty

            currentlyEnrolledCredits = 0
            subjCounter = 0
            while(subjCounter<(len(currentSemester))):
                #test_creditos = 0
                freqInstance = 100
                if currentlyEnrolledCredits + currentSemester[subjCounter+3] < creditsLimit and currentSemester[subjCounter+5] == 1:
                    currentlyEnrolledCredits = currentlyEnrolledCredits+currentSemester[subjCounter+3]
                    #raffling grades
                    freqInstance = round(freqInstance - random.uniform(25,30),2)
                    subjectToSearchforClasses = subjects.index(currentSemester[subjCounter])
                    currentSemester[subjCounter+1] = chr(int(random.uniform(0,turmas[subjectToSearchforClasses])+65))
                    currentSemester[subjCounter+6] = freqInstance
                    currentSemester[subjCounter+2] = round(random.uniform(parametersDistribuitionOverStdQty[paramListCounter],parametersDistribuitionOverStdQty[paramListCounter+1]),2)

                    if currentSemester[subjCounter] in hardPasses:
                        currentSemester[subjCounter+2] = round(currentSemester[subjCounter+2] - random.uniform(0,factors[1]),2)
                    if currentSemester[subjCounter] in easyPasses:
                        currentSemester[subjCounter+2] = round(currentSemester[subjCounter+2] + random.uniform(0,factors[0]),2)
                    #sporadic difficult classes
                    #this code snippet gets array [subj, semester, subj, semester, ...] and changes the grade on a range from 1 to 3
                    # special cases using function sorteio_de_turmas_dificeis_e_faceis()
                    if currentSemester[subjCounter] in easyHardSubjects: #[EB101,1, 0, EB101, 3, 1]
                        subjectCases = [i for i,d in enumerate(easyHardSubjects) if d==currentSemester[subjCounter]]
                        new_counter = 0
                        while(new_counter < len(subjectCases)):
                            if(semCounter == easyHardSubjects[subjectCases[new_counter]+1]):
                                if easyHardSubjects[subjectCases[new_counter]+2] == 1:
                                    currentSemester[subjCounter + 2] = round(currentSemester[subjCounter + 2] - random.uniform(1,factorsEasyHard[0]),2)
                                if easyHardSubjects[subjectCases[new_counter]+2] == 0:
                                    currentSemester[subjCounter +2] = round(currentSemester[subjCounter + 2] + random.uniform(1,factorsEasyHard[1]),2)
                            new_counter = new_counter+1

                    # grade sabotage and recovery logic:
                    if currentSemester[subjCounter+7] in gradesRaffleSabRec:
                        raffledStudentIndex = gradesRaffleSabRec.index(currentSemester[subjCounter+7])
                        if semCounter in range(gradesRaffleSabRec[raffledStudentIndex+1], gradesRaffleSabRec[raffledStudentIndex+2]+1):
                            if gradesRaffleSabRec[raffledStudentIndex+3] == 0: #negative impact
                                currentSemester[subjCounter+2] = round(currentSemester[subjCounter+2] - random.uniform(1,gradeSabRecFactors[1]),2)# a good way to show this is working is to change impact values to very high and low values
                            else:
                                currentSemester[subjCounter+2] = round(currentSemester[subjCounter+2] + random.uniform(1,gradeSabRecFactors[2]),2) #positive impact

                    #frequency sabotage and recovery logic:
                    if currentSemester[subjCounter+7] in frequencyRaffleSabRec:
                        raffledStudentIndex = frequencyRaffleSabRec.index(currentSemester[subjCounter+7])
                        if semCounter in range(frequencyRaffleSabRec[raffledStudentIndex+1], frequencyRaffleSabRec[raffledStudentIndex+2]+1):
                            if frequencyRaffleSabRec[raffledStudentIndex+3] == 0: #negative impact
                                currentSemester[subjCounter+6] = round(currentSemester[subjCounter+6] - random.uniform(10,frequencySabRecFactors[1]),2)# a good way to show this is working is to change impact values to very high and low values
                            else:
                                currentSemester[subjCounter+6] = round(currentSemester[subjCounter+6] + random.uniform(10,frequencySabRecFactors[2]),2) #positive impact

                    #treating < 0 and > 10
                    if currentSemester[subjCounter+2] < 0:
                        currentSemester[subjCounter+2] = -1
                    if currentSemester[subjCounter+2] > 10:
                        currentSemester[subjCounter+2] = 10
                    #treating < 0 and > 100 freq
                    if currentSemester[subjCounter+6] < 0:
                        currentSemester[subjCounter+6] = 0
                    if currentSemester[subjCounter+6] > 100:
                        currentSemester[subjCounter+6] = 100

                    if currentSemester[subjCounter+2] >= 5 and currentSemester[subjCounter+6] > 74.99:
                        alreadyPassedSubjects.append(currentSemester[subjCounter])
                        currentSemester[subjCounter+5] = 0
                subjCounter = subjCounter + subjectAtributesQty


            count_line = 0
            while (count_line<len(currentSemester)):
                line.append(currentSemester[count_line + 1])
                alldata.append(currentSemester[count_line + 1])
                line.append(currentSemester[count_line + 2])
                alldata.append(currentSemester[count_line + 2])
                line.append(currentSemester[count_line+6])
                count_line = count_line + subjectAtributesQty

            semCounter = semCounter + 1
        ## get pendent array grades and return to regular grades array
        holder = 0
        while(holder<len(line)):
            all_grades.append(line[holder])
            holder = holder +1
        paramListCounter = paramListCounter+2
        l = l+1


    l = 0

    #removing -1 e classes that weren`t enrolled
    counterX = 1
    while(counterX<len(all_grades)):
        if all_grades[counterX] == -1:
            all_grades[counterX] = '--'
            all_grades[counterX-1] = '--'
        counterX = counterX + 1


    #going over all data
    position = 0
    lensub = len(subjectsAsHeader)
    print("students")
    print(students)

    while (l < len(students)):
        grade[l] = all_grades[position:position+len(subjectsAsHeader)]
        position = position + lensub
        l = l+1

    simulation = pd.DataFrame (scrambled(grade),index=students, columns=subjectsAsHeader)
    #ja_simulou = 1
    simulationArray = simulation.values.tolist()
    test = np.array(simulationArray)


    if len(simulation)>0:
        studentDfForReport, students_data = export_student_data(students, maxCompletionTime, oddSemSubjAmount, evenSemSubjAmount, simulationArray, subjectsAsHeader, subjects,credits, startingYear, cat_info)
        studentRecords = get_students_records(students_data, startingYear)
        realFinalToolExport, subjectsFinalExport = exporting_to_tool(simulationArray, evenSemSubjAmount,oddSemSubjAmount, subjectsAsHeader)






    if os.path.exists("demofile.txt"):
        os.remove("demofile.txt")
    else:
        f = open("app/imports/log.txt", "w")
        f.write('----------------------- DETALHES --------------------------\n')
        f.write('- Quantidade de alunos simulados: '+str(len(students))+'.\n')

        f.write('- Tempo máximo de integralização: '+ str(maxCompletionTime)+'.\n')
        f.write('- Máximo de créditos por semestre: '+ str(creditsLimit)+'.\n')
        f.write('-------------------------------------------------------------------\n')
        f.write('Disciplinas de baixa dificuldade (acréscimo na nota da turma):\n')
        j = 0
        while(j<len(easyPasses)):
            f.write('- '+easyPasses[j]+'\n')
            j = j+1

        f.write('Fator : + (0.0 à '+str(factors[0])+')\n')
        f.write('-------------------------------------------------------------------\n')
        f.write('Disciplinas de alta dificuldade (decréscimo na nota da turma):\n')
        j = 0
        while(j<len(hardPasses)):
            f.write('- '+hardPasses[j]+'\n')
            j = j+1
        f.write('Fator : - (0.0 à '+str(factors[1])+')\n')
        f.write('-------------------------------------------------------------------\n')
        f.write('Disciplinas sorteadas para haver alteração abrupta na nota da turma:')
        f.write('\nImpacto negativo: - 0 á '+str(factorsEasyHard[0]))
        f.write('\nImpacto positivo: + 0 á '+str(factorsEasyHard[1]))
        f.write('\n-------------------')
        j = 0
        while(j<len(easyHardSubjects)):
            if easyHardSubjects[j+2] == 0:
                impact = 'positivo.'
            else:
                impact = 'negativo.'
            f.write('\n-------------------\n- Disciplina: ' + str(easyHardSubjects[j])+';\n- Semestre sorteado: ' + str(easyHardSubjects[j+1]) + ';\n- Impacto: '+impact)
            j = j+3

        grade_report_sab_rec = get_report_sab_rec(gradesRaffleSabRec)
        frequency_report_sab_rec = get_report_sab_rec(frequencyRaffleSabRec)
        f.write('\n-------------------')
        f.write('\n-------------------------------------------------------------------')
        f.write('\nSabotagem e recuperação de notas: ')
        f.write('\nQtde. de alunos: '+str(grade_report_sab_rec[0]))
        f.write('\nQtde. alunos com impacto negativo: '+str(grade_report_sab_rec[1]))
        f.write('\nFator de impacto negativo: - 0 à '+str(gradeSabRecFactors[1]))
        f.write('\nQtde. alunos com impacto positivo: '+str(grade_report_sab_rec[2]))
        f.write('\nFator de impacto positivo: + 0 à '+str(gradeSabRecFactors[2]))
        f.write('\n-------------------------------------------------------------------')
        f.write('\nSabotagem e recuperação de frequência: ')
        f.write('\nQtde. de alunos: '+str(frequency_report_sab_rec[0]))
        f.write('\nQtde. alunos com impacto negativo: '+str(frequency_report_sab_rec[1]))
        f.write('\nFator de impacto negativo: - 0 à '+str(frequencySabRecFactors[1]))
        f.write('\nQtde. alunos com impacto positivo: '+str(frequency_report_sab_rec[2]))
        f.write('\nFator de impacto positivo: + 0 à '+str(frequencySabRecFactors[2]))

        f.close()
######################
        try:
            f = open("app/exports/curso.csv")
            os.remove("app/exports/curso.csv")
        except IOError:
            f = open("app/exports/curso.csv", "+w")
        finally:
            f.close()
            simulation.to_csv(r'app/exports/curso.csv')

######################

        studentInfoToExport = pd.DataFrame (studentDfForReport,index=students, columns=['RA', 'ANOING', 'PINGR', 'DANOCAT', 'CURSO', 'ANO_INGRESSO', 'ANO_CATALOGO', 'CR', 'CP', 'CP_FUTURO', 'POSICAO_ALUNO_NA_TURMA', 'COEFICIENTE_RENDIMENTO_PADRAO', 'COEFICIENTE_RENDIMENTO_MEDIO', 'DESVIO_PADRAO_TURMA', 'TOTAL_ALUNOS_TURMA'])
        try:
            f = open("app/exports/info_std.csv")
            os.remove("app/exports/info_std.csv")
        except IOError:
            f = open("app/exports/info_std.csv", "+w")
        finally:
            f.close()
            studentInfoToExport.to_csv(r"app/exports/info_std.csv")
#####################
        writableStudentRecords = pd.DataFrame (studentRecords, columns=['RA', 'ANO', 'PERIODO', 'DISCIPLINA', 'NOTA', 'FREQUENCIA', 'SITUACAO', 'DESCRICAO_SITUACAO','CURRICULARIDADE', "CREDITO_DISCIPLINA", 'COMO_FOI_CURSADA'])
        try:
            f = open("app/exports/historicos.csv")
            os.remove("app/exports/historicos.csv")
        except IOError:
            f = open("app/exports/historicos.csv", "+w")
        finally:
            f.close()
            writableStudentRecords.to_csv(r'app/exports/historicos.csv')
######################
        writablePrereqReport = pd.DataFrame(prereqReport, columns = ['TIPO_NIVEL_ATIVIDADE_MAE', "DISCIPLINA", "ANO_INICIO", "ANO_FIM", "NO_CADEIA_PRE_REQUISITO", "TIPO_PRE_REQUISITO", "DISCIPLINA_EXIGIDA", "TIPO_NIVEL_ATIVIDADE_EXIGIDA"])
        try:
            f = open("app/exports/prerequisitos.csv")
            os.remove("app/exports/prerequisitos.csv")
        except IOError:
            f = open("app/exports/prerequisitos.csv", "+w")
        finally:
            f.close()
            writablePrereqReport.to_csv(r'app/exports/prerequisitos.csv')
######################
        barrosToolExport = pd.DataFrame (realFinalToolExport,index=students, columns=subjectsFinalExport)
        barrosToolExport.index.name = 'RA'
        barrosToolExport.insert(0,'CLASS',startingYear[0])
        try:
            f = open("app/static/usr_viz/export_visualizacao.csv")
            os.remove("app/static/usr_viz/export_visualizacao.csv")
        except IOError:
            f = open("app/static/usr_viz/export_visualizacao.csv", "+w")
        finally:
            f.close()
            barrosToolExport.to_csv(r'app/static/usr_viz/export_visualizacao.csv', sep=';')
        with open('app/static/usr_viz/export_visualizacao.csv', 'r') as original: data = original.read()
        with open('app/static/usr_viz/export_visualizacao.csv', 'w') as modified: modified.write(";\n2\nCLASS\n" + data)
######################
        barrosToolCsv = pd.read_csv('app/static/usr_viz/export_visualizacao.csv', index_col=False)
        barrosToolJson = barrosToolCsv.to_json(orient="split")
        parsed = json.loads(barrosToolJson)

    return simulation, simulationArray, maxCompletionTime, oddSemSubjAmount, evenSemSubjAmount, subjectsAsHeader, students_data, writablePrereqReport, writableStudentRecords, studentInfoToExport, realFinalToolExport, students, subjectsFinalExport

####running ,,

def allocate_temp_viz(visualizacao_df, students, subjectsFinalExport, startingYear, storage, timestamp, user_id):
    tempDir = tempfile.TemporaryDirectory()
    vizTempFile = tempDir.name+"/viz.csv"
    barrosToolExport = pd.DataFrame (visualizacao_df,index=students, columns=subjectsFinalExport)
    barrosToolExport.index.name = 'RA'
    barrosToolExport.insert(0,'CLASS',startingYear[0])
    try:
        f = open(vizTempFile)
        os.remove(vizTempFile)
    except IOError:
        f = open(vizTempFile, "+w")
    finally:
        f.close()
        p = Path(tempDir.name)
        barrosToolExport.to_csv(Path(p,'viz.csv'),  sep=';')
    with open(vizTempFile, 'r') as original: data = original.read()
    with open(vizTempFile, 'w') as modified: modified.write(";\n2\nCLASS\n" + data)
    lastViz = user_id+"/temp_viz/"+timestamp+"_viz.csv"
    storage.child(lastViz).put(vizTempFile)
    vizPathFile = storage.child(user_id+"/temp_viz/"+timestamp+"_viz.csv").get_url(None)
    return vizPathFile, lastViz

def read_temp_viz(vizPathFile):
    tempViz = pd.read_csv('app/static/usr_viz/export_visualizacao.csv', index_col=False)

    barrosToolJson = tempViz.to_json(orient="split")
    tempVizJson = json.loads(barrosToolJson)
    return tempVizJson

def del_temp_viz():
    return
