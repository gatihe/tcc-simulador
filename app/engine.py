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
#studentsData = []
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


def sorteio_de_turmas_dificeis_e_faceis(subjects, maxCompletionTime, evenSemester, oddSemester):
    #define how many subjects
    raffleEasyHard = []


    #set a number from 0 to 10
    amountOfOcurrences = random.randint(0,10)
    #cont 0 to 10:
    cont = 0
    while(cont<amountOfOcurrences):
        raffledSubject = subjects[random.randint(1,len(subjects))-1]
        raffleEasyHard.append(raffledSubject)
        if raffledSubject in evenSemester:
            raffledSemester = random.randrange(2, maxCompletionTime +1, 2)
        if raffledSubject in oddSemester:
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
        for maxYears in cat.findall('yearsLimit'):
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
    studentsData = []
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
        studentsData.append(individualStudentData)
        l = l +1

    crs, medCrs, standardDeviation = calc_std_crs(studentsData)

    info_std = []
    stdIndividualInfo = []
    l = 0
    while(l<len(studentsData)):
        accomplishedCredits = 0
        stdIndividualInfo = []
        m = 0
        courseTotalCredits = 0
        while (m<len(credits)):
            courseTotalCredits = courseTotalCredits + credits[m]
            m = m +1
        j = 2


        #crp
        performanceCoefficient = crs[crs.index(studentsData[l][j-2])+1]
        standardPerformanceCoefficient = ((performanceCoefficient - medCrs)/standardDeviation)


        stdIndividualInfo.append(studentsData[l][j-2]) #RA                  (0)
        stdIndividualInfo.append(startingYear[0]) #ANOING             (1)
        stdIndividualInfo.append(2) #PINGR POR ENQUANTO SERA 2               (2)
        stdIndividualInfo.append(cat_info[1]) #DANOCAT = ANOCATALOGO         (3)
        stdIndividualInfo.append(cat_info[0]) #numero do CURSO               (4)
        stdIndividualInfo.append(startingYear[0]) #ANOING             (5)
        stdIndividualInfo.append(cat_info[1]) #ANO_CATALOGO = ANOCATALOGO    (6)
        stdIndividualInfo.append(round(crs[crs.index(studentsData[l][j-2])+1],3)) #CR - VAI SER CALCULADO DEPOIS           (7)
        stdIndividualInfo.append(0) #CP -           (8)
        stdIndividualInfo.append(0) #CP FUTURO  (9)
        stdIndividualInfo.append(crs[crs.index(studentsData[l][j-2])-1]) #POSICAO_ALUNO_NA_TURMA(10)
        stdIndividualInfo.append(round(standardPerformanceCoefficient,3)) #CR PADRAO - VAI SER CALCULADO DEPOIS    (11)
        stdIndividualInfo.append(round(medCrs,3)) #CR MEDIO - VAI SER CALCULADO DEPOIS    (12)
        stdIndividualInfo.append(round(standardDeviation,3)) #DESVIO_PADRAO_TURMA                     (13)
        stdIndividualInfo.append(len(students))  #TOTAL_ALUNOS_TURMA         (14)
        while(j<len(studentsData[l])):
            if studentsData[l][j+1] >= 5 and studentsData[l][j+2] >= 75:
                accomplishedCredits = accomplishedCredits + studentsData[l][j+4]
            j = j+5
        stdIndividualInfo[8] = round(accomplishedCredits/courseTotalCredits,3)
        stdIndividualInfo[9] = round(accomplishedCredits/courseTotalCredits,3)
        info_std.append(stdIndividualInfo)
        l = l+1

    return info_std, studentsData

def calc_desvio_padrao():
    return desvio_padrao

def calc_cr(stdData):
    testCalcCR = get_students_records(studentsData)
    return testCalcCR

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
    parsedClasses = []
    for parseArray in root.findall('subjects'):
        for subject in parseArray.findall('subject'): # access each subject
            individualClassesQty = subject.findall('classes_no')
            for x in individualClassesQty:
                parsedClasses.append(int(x.text))
    return parsedClasses

def getting_credits_config_from_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    parsedCredits = []
    for parseArray in root.findall('subjects'):
        for subject in parseArray.findall('subject'): # access each subject
            individualAmountOfCredits = subject.findall('credits')
            for x in individualAmountOfCredits:
                parsedCredits.append(int(x.text))
    return parsedCredits

def getting_semoffer_config_from_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    parsedSemOffers = []
    for parseArray in root.findall('subjects'):
        for subject in parseArray.findall('subject'): # access each subject
            individualSemOffer = subject.findall('sem_offer')
            for x in individualSemOffer:
                parsedSemOffers.append(int(x.text))
    return parsedSemOffers

def getting_prereqs_config_from_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    parsedPreRqs = []
    for parseArray in root.findall('subjects'):
        for subject in parseArray.findall('subject'):
            individualParsedPreReq = subject.findall('pre_reqs')
            individualParsedSubjectId = subject.findall('id')
            for x in individualParsedPreReq:
                    if x.text is not None:
                        #prereq to add is equal to pre_reqs tag's text inside the current subject being parsed
                        parsedPreRqs.append(x.text)
                        parsedPreRqs.append(individualParsedSubjectId[0].text)
    return parsedPreRqs

def getting_prereq_report_from_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    allStartingYears = []
    reportPrereqs = []
    for parseArray in root.findall('subjects'):
        for subject in parseArray.findall('subject'):

            individualParsedInitialYear = subject.findall('ano_inicio')
            individualParsedFinalYear = subject.findall('ano_fim')
            individualParsedSubjectId = subject.findall('id')
            individualParsedStartingYear = subject.findall('tipo_nivel_atividade_mae')
            individualParsedPreRqs = subject.findall('pre_reqs')
            individualParsedPreqrsGroup = subject.findall('no_cadeia_pre_requisito')
            individualParsedPreqrsType = subject.findall('tipo_pre_requisito')
            individualParsedActivityType = subject.findall('tipo_nivel_atividade_exigida')
            for (x,y,z,w,v, u) in zip(individualParsedPreRqs, individualParsedInitialYear, individualParsedFinalYear, individualParsedPreqrsGroup, individualParsedPreqrsType, individualParsedActivityType):
                    if x.text is not None:
                        allStartingYears = []
                        allStartingYears.append(individualParsedStartingYear[0].text)
                        allStartingYears.append(individualParsedSubjectId[0].text)
                        allStartingYears.append(y.text)
                        if z.text == '0':
                            allStartingYears.append('')
                        else:
                            allStartingYears.append(z.text)
                        allStartingYears.append(w.text)
                        allStartingYears.append(v.text)
                        allStartingYears.append(x.text)
                        allStartingYears.append(u.text)
                        reportPrereqs.append(allStartingYears)
    return reportPrereqs


def getting_hard_pass_from_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    parsed_hard_pass = []
    for parseArray in root.findall('subj_dificulty'):
        for hp in parseArray.findall('hard_pass'):
            individual_hp = hp.findall('sub_id')
            for x in individual_hp:
                    if x.text is not None:
                        parsed_hard_pass.append(x.text)
    return parsed_hard_pass

def getting_easy_pass_from_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    parsed_easy_pass = []
    for parseArray in root.findall('subj_dificulty'):
        for hp in parseArray.findall('easy_pass'):
            individual_ep = hp.findall('sub_id')
            for x in individual_ep:
                    if x.text is not None:
                        parsed_easy_pass.append(x.text)
    return parsed_easy_pass

def getting_params_config_from_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    parsedParams = []
    for parseArray in root.findall('parameters'):
        for parameter in parseArray.findall('parameter'):
            individualParameterName = parameter.findall('parameter_name')
            parsedParams.append(individualParameterName[0].text)
            individualParameterMinGrade = parameter.findall('min_grade')
            parsedParams.append(float(individualParameterMinGrade[0].text))
            individualParameterMaxGrade = parameter.findall('max_grade')
            parsedParams.append(float(individualParameterMaxGrade[0].text))
            individualParameterStdAmount = parameter.findall('qtde')
            parsedParams.append(int(individualParameterStdAmount[0].text))
    return parsedParams

def getting_factors_config_from_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    parsedFactors = []
    for configFactor in root.findall('factors'):
        easyPassFactor = configFactor.findall('easy_pass_factor')
        parsedFactors.append(float(easyPassFactor[0].text))
        hardPassFactor = configFactor.findall('hard_pass_factor')
        parsedFactors.append(float(hardPassFactor[0].text))
    return parsedFactors

def getting_generic_info_from_file(filename):
        tree = ET.parse(filename)
        root = tree.getroot()
        parsedInfo = []
        for generic_info in root.findall('generic_info'):
            enrollmentYear = generic_info.findall('ano_ingresso')
            parsedInfo.append(int(enrollmentYear[0].text))
        return parsedInfo

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

def get_students_records(studentsData, startingYear):
    #EXPORT STUDENTS RECORDS
    allRecords = []
    individualGradeOnRecord = []
    j = 0
    while(j< len(studentsData)):
      m = 2
      while(m<len(studentsData[j])):
        individualGradeOnRecord = []
        individualGradeOnRecord.append(studentsData[j][0]) #0
        individualGradeOnRecord.append(int(startingYear[0]+(studentsData[j][m+3]/2))) #1
        individualGradeOnRecord.append(studentsData[j][m+3])#2
        individualGradeOnRecord.append(studentsData[j][m])#3
        individualGradeOnRecord.append(studentsData[j][m+1])#4
        individualGradeOnRecord.append(studentsData[j][m+2])#5
        if studentsData[j][m+1] >= 5 and studentsData[j][m+2] >= 75:
            individualGradeOnRecord.append(4)#6
        if studentsData[j][m+1] < 5 and studentsData[j][m+2] >= 75:
            individualGradeOnRecord.append(5)#6
        if studentsData[j][m+2] < 75:
            individualGradeOnRecord.append(6)#6
        if individualGradeOnRecord[6] == 4:
            individualGradeOnRecord.append("APROVADO POR NOTA/CONCEITO E FREQ")
        if individualGradeOnRecord[6] == 5:
            individualGradeOnRecord.append("REPROVADO POR NOTA/CONCEITO")
        if individualGradeOnRecord[6] == 6:
            individualGradeOnRecord.append("REPROVADO POR FREQUENCIA")
        individualGradeOnRecord.append(1)
        individualGradeOnRecord.append(studentsData[j][m+4])
        individualGradeOnRecord.append('REGULAR')
        allRecords.append(individualGradeOnRecord)
        m = m+5
      j = j+1
    return allRecords

def calc_std_crs(stdData):
    l = 0
    studentTotalCredits = 0
    studentTotalGrades = 0
    nici = 0
    counter = 0
    studentsCrs = []
    pureCrs = [] #only crs in order to calc class standard deviation
    while(l<len(stdData)):
        c = 2
        while(c<len(stdData[l])):
            individual_nici = 0
            studentTotalCredits = studentTotalCredits + stdData[l][c+4]
            studentTotalGrades = studentTotalGrades + stdData[l][c+1]
            individual_nici = stdData[l][c+1] * stdData[l][c+4]
            counter = counter + 1
            nici = nici + individual_nici
            c = c+5

        cr = round(nici/(10*studentTotalCredits),3)
        studentsCrs.append(stdData[l][0])
        studentsCrs.append(cr)
        pureCrs.append(cr)
        l = l+1


    toRank = studentsCrs
    positions = []
    counter = 1
    while (len(toRank)>1):
        c = 1
        storedHighestValue = -1
        storedHighestIndex = -1
        while (c<len(toRank)):
            if storedHighestValue < toRank[c]:
                storedHighestValue = toRank[c]
                storedHighestIndex = c
            c = c +2
        positions.append(counter)
        positions.append(studentsCrs[storedHighestIndex-1])
        positions.append(storedHighestValue)
        toRank.pop(storedHighestIndex)
        toRank.pop(storedHighestIndex-1)
        counter = counter+1

#average class cr
    m = 2
    crsSum = 0
    instances = 0
    while(m<len(positions)):
        crsSum = crsSum+positions[m]
        instances = instances+1
        m = m+3

    medCrs = crsSum/instances

    standardDeviation = np.std(pureCrs)
    standardDeviation = standardDeviation
    return positions, medCrs, standardDeviation
    #crs, medCrs, standardDeviation = calc_std_crs(studentsData)


#counters and variable for grades creation
a = 0
b = 0
newgradeline = []
grade = []

#cut is the min grade to be aproved
cut = 5
evenSemester = []
oddSemester = []

def check_for_prereq(subjectToCheck, prereqsList):
    counter = 0
    subjectPrereqs = []
    while (counter < len(prereqsList)):
        if prereqsList[counter] == subjectToCheck and counter % 2 != 0:
            subjectPrereqs.append(prereqsList[counter - 1])
        counter = counter + 1
    return subjectPrereqs

def arrange_semesters(subjects, semoffers, evenSemester, oddSemester):
    i = 0
    j = 0
    evenSemester.clear()
    oddSemester.clear()
    for i, j in zip(semoffers, subjects):
        if i % 2 == 0:
            evenSemester.append(j)
        if i % 2 != 0:
            oddSemester.append(j)
    return


def sort_turmas(subjects, turmas):
    sub = 0
    run_turma = 0
    subjectsAndClasses = []
    subjectsAndClasses.clear()
    while (sub < len(subjects)):
        subjectsAndClasses.append('Turma')
        subjectsAndClasses.append(subjects[sub])
        subjectsAndClasses.append('Freq')
        sub = sub +1
    return subjectsAndClasses

def check_prereqs_are_ok(subj, alreadyPassedSubjects): #if 1 ok if 0 not ok
    counter = 0
    okOrNot = 1
    while(counter<len(subj)):
        if subj[counter] not in alreadyPassedSubjects:
            okOrNot = 0
    return okOrNot

def sort_sab_rec(students, maxCompletionTime, sabRecFactors):
    qttyStudentsToAffect = int(np.ceil(len(students)*sabRecFactors[0]))
    counter = 0
    sabotageAndRecuperations = []
    studentsToBeAffected = random.sample(students, qttyStudentsToAffect)
    while (counter < len(studentsToBeAffected)):
        rafflePositiveNegative = random.randint(0,1)
        initialSemester = random.randint(1,maxCompletionTime) #considering everyone is fine in first semester
        willReturnToInitialState = random.randint(0,5) #0,1 wont go back, if > 1 then will go back to normal grades
        if willReturnToInitialState <=1:
            finalSemester = maxCompletionTime
        else:
            finalSemester = initialSemester + random.randint(0,maxCompletionTime-initialSemester)

        sabotageAndRecuperations.append(studentsToBeAffected[counter])
        sabotageAndRecuperations.append(initialSemester)
        sabotageAndRecuperations.append(finalSemester)
        sabotageAndRecuperations.append(rafflePositiveNegative)

        counter = counter+1

    return sabotageAndRecuperations # = [sorted_student, initialSemester, finalSemester, impact (0 for negative, 1 for positive)]

def get_report_sab_rec(sabotageAndRecuperations):
    amountOfStudents = len(sabotageAndRecuperations)/4
    counter = 3
    positiveQty = 0
    negativeQty = 0
    reportSabRec = []
    while (counter < len(sabotageAndRecuperations)):
        if sabotageAndRecuperations[counter] == 0:
            negativeQty = negativeQty + 1
        if sabotageAndRecuperations[counter] == 1:
            positiveQty = positiveQty + 1
        counter = counter + 4
    reportSabRec.append(amountOfStudents)
    reportSabRec.append(negativeQty)
    reportSabRec.append(positiveQty)
    return reportSabRec


def new_simulation(params, factors, hardPasses, easyPasses, startingYear, subjects, turmas, prereqs, semoffers, credits, cat_info, prereqReport, gradeSabRecFactors, frequencySabRecFactors, factorsEasyHard):

    #ja_simulou = 1
    arrange_semesters(subjects, semoffers, evenSemester, oddSemester)
    yearsLimit = 6
#interperse semesters to create an offer grid
    allSubjects = []
    allSubjects.clear()
    i = 0
    while (i < 6):
        for oddSem in oddSemester:
            allSubjects.append(oddSem)
        for evenSem in evenSemester:
            allSubjects.append(evenSem)
        i = i+1
    #print(allSubjects)
    subjectsAsHeader = []
    subjectsAsHeader.clear()
    subjectsAsHeader = sort_turmas(allSubjects, turmas)



    grade.clear()
    students.clear()
    paramsSort = [x for x in params if not isinstance(x, str)] #returns params as [param1_min_grade, param1_max_grade, param1_qty_students, param2min_grade,....]



    #studentsTotal will count how many students should be created for each parameter based on configs
    studentsTotal = 0
    counterX = 3
    while(counterX < len(params)):
        total = params[counterX]
        studentsTotal = studentsTotal + total
        counterX = counterX + 4
    #creating students and grades
#counter for students ids creation
    i = 0
    j = 2

    while(i < studentsTotal):
        newstudent = random.randint(100000,199999)
        #excluding duplicates
        if newstudent not in students:
            students.append(newstudent)
            i = i+1
    #now grades
    while(j<len(paramsSort)):
        a = 0
        while(a < paramsSort[j]):
            b = 0
            newgradeline = []
            grade.append(newgradeline)
            while(b < len(subjectsAsHeader)):
                #gen_grade = round(random.uniform(paramsSort[j-2],paramsSort[j-1]),2)
                gen_grade = -1
                newgradeline.append(gen_grade)
                b = b +1
            a = a +1
        j = j + 3

    ##this code snippet creates an array [subj, credits] that will be used to compose "pending" array
    m = 0
    subjectCredits = []
    subjectCredits.clear()
    while(m<len(subjects)):
        subjectCredits.append(subjects[m])
        subjectCredits.append(credits[m])
        m = m+1


#emptying values and sorting classes (turmas)
    l = 0
    while(l < len(students)):
        c = 0
        while (c < len(subjectsAsHeader)):
            if subjectsAsHeader[c] in subjects:
                classInstance = subjects.index(subjectsAsHeader[c])
                classRaffle = 0
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
    evenSemSubjAmount = len(evenSemester)
    oddSemSubjAmount = len(oddSemester)
    subjectAtributesQty = 8 #nome, turma, nota, creditos, semestre de oferta, liberado
    currentlyEnrolledCredits = 0
    currentSemester = []
    maxCompletionTime = 12
    line = []
    alldata = []
    parametersDistribuitionOverStdQty = []
    allGrades = []


    raffledStdd = random.randint(0, len(students)-1)
    gradesRaffleSabRec = sort_sab_rec(students, maxCompletionTime,gradeSabRecFactors)#0.5 aleatory, will be editable in flask interface
    frequencyRaffleSabRec = sort_sab_rec(students, maxCompletionTime, frequencySabRecFactors)#0.3 aleatory, will be editable in flask interface


    easyHardSubjects = sorteio_de_turmas_dificeis_e_faceis(subjects, maxCompletionTime, evenSemester, oddSemester)

    #distributing parameters according to amount of students
    #2 on parameter1 and 1 on parameter2 =
    # = [parameter1 min, parameter1 max, parameter1 min, parameter1 max, parameter2 min, parameter2 max]
    counterX = 2
    while(counterX < len(paramsSort)):
        counterY = 0
        while(counterY<paramsSort[counterX]):
            parametersDistribuitionOverStdQty.append(paramsSort[counterX-2])
            parametersDistribuitionOverStdQty.append(paramsSort[counterX-1])
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
            subjCredIndex = subjectCredits.index(subjectsAsHeader[c])
            pendingSubjects.append(subjectCredits[subjCredIndex+1]) #credits
            if subjectsAsHeader[c] in evenSemester:
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

                    #frequency sabotages and recovery logic:
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

            lineCounter = 0
            while (lineCounter<len(currentSemester)):
                line.append(currentSemester[lineCounter + 1])
                alldata.append(currentSemester[lineCounter + 1])
                line.append(currentSemester[lineCounter + 2])
                alldata.append(currentSemester[lineCounter + 2])
                line.append(currentSemester[lineCounter+6])
                lineCounter = lineCounter + subjectAtributesQty

            semCounter = semCounter + 1
        ## get pendent array grades and return to regular grades array
        holder = 0
        while(holder<len(line)):
            allGrades.append(line[holder])
            holder = holder +1
        paramListCounter = paramListCounter+2
        l = l+1
    l = 0

    #removing -1 e classes that weren`t enrolled
    counterX = 1
    while(counterX<len(allGrades)):
        if allGrades[counterX] == -1:
            allGrades[counterX] = '--'
            allGrades[counterX-1] = '--'
        counterX = counterX + 1


    #going over all data
    position = 0
    lensub = len(subjectsAsHeader)
    while (l < len(students)):
        grade[l] = allGrades[position:position+len(subjectsAsHeader)]
        position = position + lensub
        l = l+1
    simulation = pd.DataFrame (scrambled(grade),index=students, columns=subjectsAsHeader)
    simulationArray = simulation.values.tolist()
    if len(simulation)>0:
        studentDfForReport, studentsData = export_student_data(students, maxCompletionTime, oddSemSubjAmount, evenSemSubjAmount, simulationArray, subjectsAsHeader, subjects,credits, startingYear, cat_info)
        studentRecords = get_students_records(studentsData, startingYear)
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
        gradeSabRecReport = get_report_sab_rec(gradesRaffleSabRec)
        freqSabRecReport = get_report_sab_rec(frequencyRaffleSabRec)
        f.write('\n-------------------')
        f.write('\n-------------------------------------------------------------------')
        f.write('\nSabotagem e recuperação de notas: ')
        f.write('\nQtde. de alunos: '+str(gradeSabRecReport[0]))
        f.write('\nQtde. alunos com impacto negativo: '+str(gradeSabRecReport[1]))
        f.write('\nFator de impacto negativo: - 0 à '+str(gradeSabRecFactors[1]))
        f.write('\nQtde. alunos com impacto positivo: '+str(gradeSabRecReport[2]))
        f.write('\nFator de impacto positivo: + 0 à '+str(gradeSabRecFactors[2]))
        f.write('\n-------------------------------------------------------------------')
        f.write('\nSabotagem e recuperação de frequência: ')
        f.write('\nQtde. de alunos: '+str(freqSabRecReport[0]))
        f.write('\nQtde. alunos com impacto negativo: '+str(freqSabRecReport[1]))
        f.write('\nFator de impacto negativo: - 0 à '+str(frequencySabRecFactors[1]))
        f.write('\nQtde. alunos com impacto positivo: '+str(freqSabRecReport[2]))
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

    return simulation, simulationArray, maxCompletionTime, oddSemSubjAmount, evenSemSubjAmount, subjectsAsHeader, studentsData, writablePrereqReport, writableStudentRecords, studentInfoToExport, realFinalToolExport, students, subjectsFinalExport

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
