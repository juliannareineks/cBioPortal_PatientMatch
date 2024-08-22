# cBioPortal Patient Match
Find similar cancer study patients from cBioPortal, a database of public cancer studies.

cBioPortal is a large, consistently-updated databse of cancer studies available to the public and used in hospital and research settings to advance treatments in oncology. The website cBioPortal is hosted on has a variety of features to help narrow down the type of data a user may be looking for, but lacks some features. cBioPortal Patient Match seeks to adda feature intended to aid oncologists with finding patients in other studies similar to their own or create cohorts of patients with similar attributes; additionaly, there is a search function similar to a regular search instead of relying on a patient's information.

You can find cBioPortal's website at https://www.cbioportal.org/ 

## Install

TODO

## Patient Search Use

In order to conduct a patient search, you must have a patient Id for the patient you're referencing, the study they originate from, and a list of study Ids you wish to search through. 

Example:
- patientId: MSK_LX239
- patient's study: lung_pdx_msk_2021
- list of studies: ntrk_msk_2019, lung_pdx_msk_2021

When asked if searching for a patient, respond with 'y' and follow the remaining prompts that ask which criteria you would like to use. Please note that when searching with a patient, if you decide to search through the same study they originate from, they will appear in the output. 

## Manual Search Use

To conduct a manual search, all you need is a list of study Ids. Respond with 'n' when asked if you are searching with a patient, enter the list of studies one by one, then answer the prompts to clarify which criteria to use.

Example: 
- list of studies: ntrk_msk_2019, lung_pdx_msk_2021
- criteria: Non-small cell lung cancer, Female

## Search Output

Regardless of which search you use, output will be the same. For each study you enter, you will recieve a message with the confirmed attributes of the study; thus, if a study is missing an attribute and goes unsearched, it will be east to identify the study and attribute. A panel at the bottom will print the patient Ids of those who fit the criteria along with their study and a url to their webpage on cBioPortal. When the search is complete, Tthe total number of matched patients will be given.

## Search Criteria note

To find study and patient Ids to use, you will have to go to cBioPortal's website (https://www.cbioportal.org/) and find them there.

Please keep in mind that not all studies measure the same criteria for patients and often have different names for the same attributes; for this reason, the only universal attributes are cancer type and sex. Patient Match will tell you when a study cannot be searched because it is missing a criteria, so please keep an eye out for that. 

## TODO Items

- Add more criteria options 
- Option to allow searches of studies with minimal missing criteria 
- Harmonizing attributes that use different names across studies, but have the same meaning
