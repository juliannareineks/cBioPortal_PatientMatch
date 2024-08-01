"""
Julianna Reineks
2024 
Internship Project, Matching patients
"""
# Application to match and search for patients with specified criteria and studies

import requests
import typer
from typing_extensions import Annotated

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

def getUserPreference(response: Annotated[chr, typer.Option(prompt="Would you like to search with a patient ID?(y/n):")]):
    return 0

# prompts the user to enter a list of studies one at a time
def getStudyList():
    print("Please enter studyIDs to search through. Enter after each entry.")
    while True:
        list_input = input()
        if list_input == "":
            break
        else:
            # TODO: Validate study Id

            # add to list
            studyList.append(list_input)
    return


# might get rid of the prompts, not all will use it
def main(pID : Annotated[str, typer.Option(help="patientID when searching using patient as a base")] = "",
        sID: Annotated[str, typer.Option(help="studyID of patient when searching using patientID")] = ""):
    # Check whether pID and sID were entered to decide how to proceed
    if pID == "":
        # search with only criteria
        print("Please answer the following prompts. Enter blank when leaving an attribute ambiguous or finishing a list. \n")
        getStudyList()
            
        return 0
    else:
        # search with pID. Validate the IDs

        # get list of studies 
        getStudyList()

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
