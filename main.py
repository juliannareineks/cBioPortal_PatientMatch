"""
Julianna Reineks
2024 
Internship Project, Matching patients
"""
# Application to match and search for patients with specified criteria and studies

import requests
import typer
from typing_extensions import Annotated
from typing import List, Optional

original_patient_id = None
original_study_id = None

# define lists of criteria 
genderList = ["Female", "Male", "Unidentified"]
# currently no efficent way to check, per patient, mutations (unavailable by searching w/ sample or patient Ids)
# mutationList = []
# maybe have cancer types as user-defined instead? 
cancerTypeList = ["Breast Cancer", "Non-Small Cell Lung Cancer", "Esophagogastric Cancer", "Colorectal Cancer", "Head and Neck Cancer", "Glioblastoma", "Prostate Cancer", "Leukemia", "Melanoma", "Bladder Cancer", "Renal Cell Carcinoma", "Pancreatic Cancer"]
overallSurvivalStatusList = ["Alive", "Deceased", "N/A"]
sampleTypeList = ["Metastasis", "Primary", "Recurrence"]
studyList = []
attributeIdList = ["CANCER_TYPE", "SAMPLE_TYPE", "SEX", "OS_STATUS"]
# os status and sex is under patient cd, other stuff is under sampleid
valueList = []
cancer_type_val= ""
survival_val = ""
gender_val = ""
sample_type_val = ""


# Methods
# fetchPatientSamples uses requests to get all of a pateint's samples
def fetchPatientSamples(patientId: str, studyId: str):
    return requests.get(buildURL("samples", studyId, patientId, None, None)).json()  

# fetchSampleClinicalDataAttribute takes a sample and pulls only the specified attribute
def fetchSampleClinicalDataAttribute(studyId: str, sampleId: str, attribute: str):
    return requests.get(buildURL("clinical-data", studyId, None, sampleId, attribute)).json()

# fetchClinicalAttributesStudy gets a list of all clinical attribute fields in a study
def fetchClinicalAttributesStudy(studyId: str):
    return requests.get(buildURL("clinical-attributes", studyId, None, None, None)).json()

# fetchPateintList gets a list of all patients in a study (does not include detailed info)
def fetchPatientList(studyId: str):
    return requests.get(buildURL("patients", studyId, None, None, None)).json()

# IMPORTANT: how to get mutations from sampleID? It's not a part of patient or sample clinical data
# I checked the API, you cannot get mutation data by patient. You have to obtain a MolecularProfileId, which when
# entered into a mutation search will give a list of every mutation instance in the study by sample by patient 
# It actually might be under Gene Panel Data, but there are a lot of hoops to jump through; even then, it would jsut provide a
# a list of samples that have the narrowed criteria when you use the corect sampleListId

# prompts the user to enter a list of studies one at a time
def getStudyList():
    print("Please enter studyIDs to search through. Enter after each entry. Enter blank when done.")
    while True:
        list_input = input()
        if list_input == "":
            break
        else:
            # TODO: Validate study Id. If invalid, move on

            # add to list
            studyList.append(list_input)
    print("List complete")
    return

# Possible to cut down further? 
# prompts the user for values, used when no patient specified.
def getCriteriaValues():
    # counter for ease
    print("Please specify the following criteria with the correct number. Enter blank when you don't want to specify.")
    
    # Cancer Type
    print("Cancer Type: ")
    attributePrinter(cancerTypeList, cancer_type_val)
    
    # Sample type
    print("Sample Type: ")
    attributePrinter(sampleTypeList, sample_type_val)

    # Gender
    print("Gender: ")
    attributePrinter(genderList, gender_val)

    # Survival Status
    print("Survival Status: ")
    attributePrinter(overallSurvivalStatusList, survival_val)

    # Print all values and confirm
    return confirmPrompt(valueList)

# prints out a list of available values for things with numbers and then save input (in assign)
def attributePrinter(aList, assign):
    counter = 0
    for type in aList:
        print(f"{counter} {type}")
        counter += 1
    user_input = input()
    if user_input != "":
        # input is valid; add value
        assign = aList[int(user_input)]
        valueList.append(assign)

    return

# chooseAttributes when patient is used as a base 
def chooseAttributes():
    counter = 0
    print("Please enter the corresponding numbers for which criteria to use. Enter blank to confirm all.")
    for item in attributeIdList:
        print(f"{counter} {item}")
        counter += 1
    while True:
        user_input = input()
        if user_input == "":
            break
        else:
            valueList.append(attributeIdList[int(user_input)])
    # confirm
    return confirmPrompt(valueList)

# when confirming settings
def confirmPrompt(aList):
    print("Are the following values correct(y/n)): ")
    for item in aList:
        print(item)
    user_input = input()
    if user_input == "n":
        print("Resetting Values")
        valueList.clear()
        return 1
    print("Confirmed")
    return 0


# main
def main(response : Annotated[str, typer.Option(prompt="Are you searching with a patient?(y/n)", 
                                                help="choose whether to use patient as a base")]):
    if response == "n":
        # search with only criteria
        print("Manual Search \n")
        getStudyList()
        # loop until correct values entered
        while True:
            test = getCriteriaValues()
            if test == 0:
                break

        # proceed with the search
        print("Searching...")

        return 0
    
    else:
        # search with pID. Validate the IDs
        print("Patient-based Search \n")
        print("Please enter a valid patientID: ")
        original_patient_id = input()
        print("Please enter the corresponding studyID: ")
        original_study_id = input()



        # Get criteria and studies
        getStudyList()
        while True:
            test = chooseAttributes()
            if test == 0:
                break

        # proceed with search
        print("Searching...")

        return 0


# Design choice: Put all params as commandline ops/args, or use progressive prompts (input)?

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
    elif type == "clinical-data":
        return f"{urlFirstPiece}samples/{sampleId}/{type}?attributeId={attributeId}&{urlEndPiece}"
    elif type == "clinical-attributes":
        return f"{urlFirstPiece}{type}?{urlEndPiece}"
    elif type == "patients":
        return f"{urlFirstPiece}{type}?{urlEndPiece}"
        
    return None

if __name__ == "__main__":
    typer.run(main)
