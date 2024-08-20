"""
Julianna Reineks
2024 
Internship Project, Matching patients
"""
# Application to match and search for patients with specified criteria and studies

"""Quick ref example to use when testing
Studies --
metastatic_solid_tumors_mich_2017
mixed_allen_2018
Manual attributes --
Female and Non-Small Cell Lung Cancer
Patient info --
id: luad_mskcc_2015_22
study: mixed_allen_2018
CANCER_TYPE and SEX

Studies --
ntrk_msk_2019
lung_pdx_msk_2021
Manual Attributes --
Female, Non-Small Cell Lung Cancer, 
Patient MSK_LX239 lung_pdx_msk_2021
"""

import requests
import typer
from typing_extensions import Annotated
from rich import print
from rich.console import Console,Group
from rich.theme import Theme
from rich.live import Live
from rich.table import Table
from rich.panel import Panel

original_patient_id = None
original_study_id = None
custom_theme = Theme({
    "error" : "red",
    "prompt" : "yellow",
    "confirm" : "blue underline",
    "pid" : "green"
})
console = Console(theme = custom_theme)

# define lists of criteria 
# currently no efficent way to check, per patient, mutations (unavailable by searching w/ sample or patient Ids)
# mutationList = []
studyList = []
# os status and sex is under patient id, other stuff is under sampleid
# stores attributeIds
confirmedAttributeList = []
confirmedPatientAttributeList = []
# stores values to use to compare
compareValueList = []
comparePatientValueList = []

# Methods
# fetchPatientSamples uses requests to get all of a pateint's samples
# See requests status codes for error handling
def fetchPatientSamples(patientId: str, studyId: str):
    return requests.get(buildURL("samples", studyId, patientId, None, None)).json()  

# fetchSampleClinicalDataAttribute takes a sample and pulls only the specified attribute
def fetchSampleClinicalDataAttribute(studyId: str, sampleId: str, attribute: str):
    return requests.get(buildURL("clinical-data", studyId, None, sampleId, attribute)).json()

# fetchClinicalAttributesStudy gets a list of all clinical attribute fields in a study
def fetchClinicalAttributesStudy(studyId: str):
    return requests.get(buildURL("clinical-attributes", studyId, None, None, None)).json()

# fetchPatientList gets a list of all patients in a study (does not include detailed info)
def fetchPatientList(studyId: str):
    return requests.get(buildURL("patients", studyId, None, None, None)).json()

# fetchPatient fetches a patient to see if they exist; built in error detect
def fetchPatient(patientId: str, studyId: str):
    r = requests.get(buildURL("patients", studyId, patientId, None, None))
    if r.status_code != 200:
        console.print("PatientId or patient's study is invalid, please re-enter.", style = "error")
        return 1
    return 0

# fethes a study to confirm it exists
def fetchStudy(studyId: str):
    r = requests.get(buildURL("studies", studyId, None, None, None))
    if r.status_code != 200:
        console.print("StudyId is invalid, please re-enter.", style = "error")
        return 1
    return 0

# fetchPatientClinicalData gets a patient's clinical data (as opposed to a sample's clinical data)
def fetchPatientClinicalData(patientId: str, studyId: str, attribute: str):
    return requests.get(buildURL("patients", studyId, patientId, None, attribute)).json()

# fetchPatientPage
# URL structure is as follows: https://www.cbioportal.org/patient?studyId=STUDY&caseId=CASEID
# Case ID is patientID?
def fetchPatientPage(study: str, case: str):
    urlPrefix = "https://www.cbioportal.org/patient?"
    return f"{urlPrefix}studyId={study}&caseId={case}"

# Methods for lists of things (replaces global variables)

def getCancerTypeList():
    return ["Breast Cancer", "Non-Small Cell Lung Cancer", "Esophagogastric Cancer", "Colorectal Cancer", "Head and Neck Cancer", "Glioblastoma", "Prostate Cancer", "Leukemia", "Melanoma", "Bladder Cancer", "Renal Cell Carcinoma", "Pancreatic Cancer"]

def getOverallSurvivalStatusList():
    return ["Alive", "Deceased", "N/A"]

def getSampleTypeList():
    return ["Metastasis", "Primary", "Recurrence"]

def getGenderList():
    return ["Female", "Male", "Unidentified"]

def getAttributeIdList():
    return ["CANCER_TYPE", "SAMPLE_TYPE"]

def getPatientAttributeIdList():
    return ["SEX", "OS_STATUS"]

# IMPORTANT: how to get mutations from sampleID? It's not a part of patient or sample clinical data
# I checked the API, you cannot get mutation data by patient. You have to obtain a MolecularProfileId, which when
# entered into a mutation search will give a list of every mutation instance in the study by sample by patient 
# It actually might be under Gene Panel Data, but there are a lot of hoops to jump through; even then, it would jsut provide a
# a list of samples that have the narrowed criteria when you use the corect sampleListId

# prompts the user to enter a list of studies one at a time
def getStudyList():
    console.print("Please enter studyIDs to search through. Enter after each entry. Hit Enter when done.", style = "prompt")
    while True:
        list_input = input()
        if list_input == "":
            break
        else:
            # validate study using codes/ apifetch. 
            if errorCheckStudy(list_input) == 0:
                # add to list
                studyList.append(list_input)
    console.print("List complete\n", style = "confirm")
    return

# Possible to cut down further? 
# prompts the user for values, used when no patient specified.
# THIS SECTION IS ONLY USED WITH NON-PATIENT SEARCHES
def getCriteriaValues():
    # counter for ease
    console.print("Please specify the following criteria with the correct number. Hit Enter when you don't want to specify and continue.", style = "prompt")
    
    # Cancer Type
    console.print("Cancer Type: ", style = "prompt")
    attributePrinter(getCancerTypeList(), compareValueList, confirmedAttributeList, "CANCER_TYPE")
    
    # Sample type
    console.print("Sample Type: ", style = "prompt")
    attributePrinter(getSampleTypeList(), compareValueList, confirmedAttributeList, "SAMPLE_TYPE")

    # Gender
    console.print("Gender: ", style = "prompt")
    attributePrinter(getGenderList(), comparePatientValueList, confirmedPatientAttributeList, "SEX")

    # Survival Status
    console.print("Survival Status: ", style = "prompt")
    attributePrinter(getOverallSurvivalStatusList(), comparePatientValueList, confirmedPatientAttributeList, "OS_STATUS")

    # Print all values and confirm
    return confirmPromptManual([compareValueList, comparePatientValueList], [confirmedAttributeList, confirmedPatientAttributeList])

# prints out a list of available values for attributes, then saves the value to a comparison list
# ONLY USED IN NON-PATIENT SEARCHES
def attributePrinter(aList: list, assignValueList:list, assignAttributeList:list, attribute: str):
    counter = 1
    for type in aList:
        print(f"{counter} {type}")
        counter += 1
    user_input = input()
    if user_input != "" and user_input.isnumeric() == True:
        # input is valid; first add value to correct valuelist
        # then add data label/attribute to confirmedAttributeList or confirmedPatientAttributeList.
        assignValueList.append(aList[(int(user_input)) - 1])
        assignAttributeList.append(attribute)
    elif user_input != "" and user_input.isnumeric() != True:
        # input is not a number 
        console.print("Previous input does not correspond to a value.", style = "error")
    return

# chooseAttributes when patient is used as a base. ONLY THE LABELS NEED TO BE STORED HERE. FINDING PATIENT DETAILS IS ELSEWHERE.
# inputList is retireving the list of possible labels/attributes to choose
# outputList is storing the confirmed labels
# PATIENT SEARCHES
def chooseAttributes(labelList: list, aList: list):
    counter = 1
    console.print("Please enter the corresponding numbers for which criteria to use. Hit Enter to confirm selections.", style = "prompt")
    for item in labelList:
        print(f"{counter} {item}")
        counter += 1
    while True:
        user_input = input()
        if user_input == "":
            break
        else:
            aList.append(labelList[int(user_input) - 1])
    # confirm
    return confirmPromptPatient(aList)

# when confirming settings.
# this version is used when manual/nonpatient searching (need to confirm values and attributes at same time)
def confirmPromptManual(vLists: list[list], aLists: list[list]):
    console.print("Are the following values correct?(y/n)): ", style = "prompt")
    for typelist in vLists:
        for item in typelist:
            print(item)
    user_input = input()
    if user_input == "n":
        console.print("Resetting Values", style = "confirm")
        for typelist in vLists:
            typelist.clear()
        for typelist in aLists:
            typelist.clear()
        return 1
    console.print("Confirmed\n", style = "confirm")
    return 0

# when confirming settings.
# This verison is used for PATIENT SEARCHES (no need to save values here)
# aList is one list of attributes used in patient search to confirm
def confirmPromptPatient(aList: list):
    console.print("Are the following values correct?(y/n)", style = "prompt")
    for item in aList:
        print(item)
    user_input = input()
    if user_input == "n":
        console.print("Resetting Values", style = "confirm")
        aList.clear()
        return 1
    console.print("Confirmed\n", style = "confirm")
    return 0

def confirmCorrectSample(sampleList: list):
    counter = 1
    console.print("This patient has multiple samples. Which sample would you like to use?", style = "prompt")
    for sample in sampleList:
        print(f"{counter} : {sample['sampleId']}")
        counter +=  1
    snum = input()
    return (int(snum) - 1)


# error checks to catch when api calls fail
def errorCheckPatient(patientId: str, studyId: str):
    status = fetchPatient(patientId, studyId)
    return status   

def errorCheckStudy(studyId: str):
    status = fetchStudy(studyId)
    return status

# search
def search():
    universalcount = 0
    # intialize trackers/boolean confirms
    attributeTrack = 0
    sampleTracker = False
    patientTracker = False
    # table info
    status = console.status("Working...", spinner="dots")
    patientTable = Table()
    patientTable.add_column("Matched Patients", style="green")
    patientTable.add_column("Study")
    patientTable.add_column("Patient cBioPortal Page")
    with Live(Panel(Group(status, patientTable)), refresh_per_second=2, vertical_overflow="ellipsis"):
        # loop through studies
        for study in studyList:
            currentStudyAttributesList = fetchClinicalAttributesStudy(study)
            for attribute in confirmedAttributeList:
                for listAttribute in currentStudyAttributesList:
                    if attribute == listAttribute['clinicalAttributeId']:
                        attributeTrack += 1
                        print(f"{study} has attribute {attribute}")
            for attribute in confirmedPatientAttributeList:
                for listAttribute in currentStudyAttributesList:
                    if attribute == listAttribute['clinicalAttributeId']:
                        attributeTrack += 1
                        print(f"{study} has attribute {attribute}")
            if attributeTrack == (len(confirmedAttributeList) + len(confirmedPatientAttributeList)):
                attributeTrack = 0

                # get list of patients
                patientList = fetchPatientList(study)
                
                # loop through patients
                for patientInfo in patientList:
                    # get one patient's samples
                    currentPatientId = patientInfo['patientId']
                    currentPatientSamples = fetchPatientSamples(currentPatientId, study)

                    # start loop for sample attributes 
                    for x in range(len(confirmedAttributeList)):
                        if sampleDataCompare(currentPatientSamples, x, study) == 1:
                            break
                        # only confirms when ALL attributes have passed the break statement(x is correct); otherwise this prints for any pass instead of cumulative
                        if x == (len(confirmedAttributeList) - 1):
                            sampleTracker = True

                    # start loop for patient attributes
                    for y in range(len(confirmedPatientAttributeList)):
                        if patientDataCompare(currentPatientId, y, study) == 1:
                            break
                        if y == (len(confirmedPatientAttributeList) - 1):
                            patientTracker = True

                    # Failsafe trues if one of the lists is empty
                    if len(confirmedAttributeList) == 0:
                        sampleTracker = True
                    if len(confirmedPatientAttributeList) == 0:
                        patientTracker = True
                    # test if trues to print
                    if sampleTracker == True and patientTracker == True:
                        # TODO Add the url of the patient
                        # console.print(currentPatientId, style = "pid", highlight=False)
                        url = fetchPatientPage(study, currentPatientId)
                        patientTable.add_row(currentPatientId, study, url)
                        # 
                        universalcount += 1
                    sampleTracker = False
                    patientTracker = False
            else:
                console.print(f"cannot search {study}, missing attribute(s)", style = "error")   
            attributeTrack = 0
        status.update("Search Complete")
        print(f"total matched patients: {universalcount}")
    return 

# COMPARISON METHODS
# sample data search
# In both patient and non-patient searches, the attribute IDS are stored in confirmedAttributeList. The patient's data is stored in compareValueList
# Only tests one attribute per call
def sampleDataCompare(patientSampleList: list, num: int, study: str):
    for sample in patientSampleList:
        currentSampleId = sample['sampleId']
        currentSample = fetchSampleClinicalDataAttribute(study, currentSampleId, confirmedAttributeList[num])[0]
        currentSampleValue = currentSample['value']
        if currentSampleValue == compareValueList[num]:
            return 0
    return 1

# patient data 
def patientDataCompare(patientId: str, num: int, studyId: str):
    currentPatient = fetchPatientClinicalData(patientId, studyId, confirmedPatientAttributeList[num])[0]
    currentPatientValue = currentPatient['value']
    if currentPatientValue != comparePatientValueList[num]:
        return 1
    return 0

# MAIN
# Note on patient URL: there's no API function to get that URL, so I'm not sure there's a way to get it; will keep looking
def main(response : Annotated[str, typer.Option(prompt="Are you searching with a patient?(y/n)", 
                                                help="choose whether to use patient as a base")]):
    if response == "n":
        # SEARCH WITHOUT PID
        # console.print("Manual Search \n", style = "confirm")
        console.rule("Manual Search", style="blue")
        getStudyList()
        # loop until correct values entered
        while True:
            test = getCriteriaValues()
            if test == 0:
                break

        # proceed with the search
        search()

        return 0
    
    else:
        # SEARCH WITH PID. Validate the IDs
        # console.print("Patient-based Search \n", style = "confirm")
        console.rule("Patient-Based Search", style="blue")
        
        while True:
            console.print("Please enter a valid patientID: ", style = "prompt")
            original_patient_id = input()
            console.print("Please enter the corresponding studyID: ", style = "prompt")
            original_study_id = input()
            if errorCheckPatient(original_patient_id, original_study_id) + errorCheckStudy(original_study_id) == 0:
                break

        # Get criteria and studylist
        getStudyList()

        while True:
            console.rule("Sample Attributes", style ="blue")
            test = chooseAttributes(getAttributeIdList(), confirmedAttributeList)
            if test == 0:
                break
        while True:
            console.rule("Patient Attributes", style ="blue")
            test2 = chooseAttributes(getPatientAttributeIdList(), confirmedPatientAttributeList)
            if test2 == 0:
                break

        # fetch patient's attributes (attributeIDs stored in confirmedAttributeList (and patient versions))
        pOriginalSamples = fetchPatientSamples(original_patient_id, original_study_id)
        if len(pOriginalSamples) > 1:
            pOriginalSamples = pOriginalSamples[confirmCorrectSample(pOriginalSamples)]
        else:
            pOriginalSamples = pOriginalSamples[0]
        pSampleId = pOriginalSamples['sampleId']
        for attributeId in confirmedAttributeList:
            pCurrentAttribute = fetchSampleClinicalDataAttribute(original_study_id, pSampleId, attributeId)[0]
            pcurrentValue = pCurrentAttribute['value']
            compareValueList.append(pcurrentValue)
            print (f"{attributeId} : {pcurrentValue}")
        for pattributeId in confirmedPatientAttributeList:
            pCurrentAttribute = fetchPatientClinicalData(original_patient_id, original_study_id, pattributeId)[0]
            pcurrentValue = pCurrentAttribute['value']
            comparePatientValueList.append(pcurrentValue)
            print(f"{pattributeId} : {pcurrentValue}")
        
        # proceed with search
        search()
        return 0

# build URL
#URL structures: 
#ALWAYS start with: https://www.cbioportal.org/api/studies/{studyId}/
#endings that do not require more information oare patient list and clinical attributes of a study
#endings that do require more variables include sample data clinical attribute (SampleId, Attribute) and samples of a patient (PatientId)
#returns 0 when no url type is specified, leave fields with no bearing as None. Can change to a number system if overlaps occur later.
def buildURL(type: str, studyId: str, patientId: str, sampleId: str, attributeId :str) -> str|None:
    urlFirstPiece = f"https://www.cbioportal.org/api/studies/{studyId}/"
    urlEndPiece = "projection=SUMMARY&pageSize=200000&pageNumber=0&direction=ASC"
    if type == "samples":
         return f"{urlFirstPiece}patients/{patientId}/{type}?{urlEndPiece}"
    elif type == "studies":
         return f"{urlFirstPiece}"
    elif type == "clinical-data":
        return f"{urlFirstPiece}samples/{sampleId}/{type}?attributeId={attributeId}&{urlEndPiece}"
    elif type == "clinical-attributes":
        return f"{urlFirstPiece}{type}?{urlEndPiece}"
    elif type == "patients" and attributeId != None:
        # fetches clincial data attribute of a patient
        return f"{urlFirstPiece}{type}/{patientId}/clinical-data?attributeId={attributeId}&{urlEndPiece}"
    elif type == "patients" and patientId != None:
        # fetches one paarticular patient, not their clinical data (for confirmation purposes)
        return f"{urlFirstPiece}{type}/{patientId}"
    elif type == "patients":
        return f"{urlFirstPiece}{type}?{urlEndPiece}"
        
    return None

if __name__ == "__main__":
    typer.run(main)
