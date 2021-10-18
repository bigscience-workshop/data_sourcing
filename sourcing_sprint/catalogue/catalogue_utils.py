import json

from glob import glob

import streamlit as st

app_categories = {
    "entry_types": {
        "primary": "Primary source",
        "processed": "Processed language dataset",
        "organization": "Language organization or advocate",
    },
    #
    "language_lists": json.load(open("resources/language_lists.json", encoding="utf-8")),
    "programming_languages": [x for x in json.load(open("resources/programming_languages.json", encoding="utf-8"))["itemListElement"]],
    "languages_bcp47": [x for x in json.load(open("resources/bcp47.json", encoding="utf-8"))["subtags"] if x["type"] == "language"],
    #
    "custodian_types": [
        "A private individual",
        "A commercial entity",
        "A library, museum, or archival institute",
        "A university or research institution",
        "A nonprofit/NGO (other)",
        "A government organization",
    ],
    "pii_categories": json.load(open("resources/pii_categories.json", encoding="utf-8")),
    "licenses": json.load(open("resources/licenses.json", encoding="utf-8")),
    "primary_taxonomy": json.load(open("resources/primary_source_taxonomy.json", encoding="utf-8")),
    "file_formats": json.load(open("resources/file_formats.json", encoding="utf-8")),
}

def load_catalogue():
    catalogue_list = [json.load(open(fname, encoding="utf-8")) for fname in glob("entries/*.json") if not "-validated-" in fname]
    catalogue = dict([('', {
        "uid": "",
        "type": "",
        "description": {
            "name": "",
            "description": "",
        },
    })] + [(dct["uid"], dct) for dct in catalogue_list])
    return catalogue

def filter_entry(entry, filter_dct):
    res = True
    for k, v in entry.items():
        if k in filter_dct:
            if isinstance(v, dict):
                res = res and filter_entry(v, filter_dct[k])
            elif isinstance(v, list):
                res = res and (len(filter_dct[k]) == 0 or any([e in filter_dct[k] for e in v]))
            else:
                res = res and (len(filter_dct[k]) == 0 or v in filter_dct[k])
    return res

def can_save(entry_dct, submission_dct, adding_mode):
    if adding_mode and (entry_dct['uid'] == "" or isfile(pjoin("entries", f"{entry_dct['uid']}.json"))):
        return False, f"There is already an entry with `uid` {entry_dct['uid']}, you need to give your entry a different one before saving. You can look at the entry with this `uid` by switching to the **Validate an existing entry** mode of this app in the left sidebar."
    if adding_mode and (submission_dct["submitted_by"] == "" or submission_dct["submitted_email"] == ""):
        return False, f"Please enter a name (or pseudonym) and email in the left sidebar before submitting this entry. [Privacy policy](https://github.com/bigscience-workshop/data_sourcing/wiki/Required-User-Information-and-Privacy-Policy)"
    if not adding_mode and submission_dct["validated_by"] == "":
        return False, f"Please enter a name (or pseudonym) in the left sidebar before validating this entry."
    if adding_mode and entry_dict["custodian"]["contact_submitter"] and submission_dct["submitted_email"] == "":
        return False, f"You said that you would be willing to reach out to the entity or organization. To do so, please enter an email we can use to follow up in the left sidebar."
    if not adding_mode and not all([v.get("validated", False) for k, v in entry_dict.items() if isinstance(v, dict)]):
        unvalidated = [k for k, v in entry_dict.items() if isinstance(v, dict) and not v.get("validated", False)]
        return False, f"Some of the fields haven't been validated: {unvalidated}"
    else:
        return True, ""
