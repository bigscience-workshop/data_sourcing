import json
import re
from datetime import datetime
from glob import glob
from os.path import isfile
from os.path import join as pjoin

import streamlit as st

from streamlit_folium import folium_static

from catalogue import (
    app_categories,
    can_save,
    countries,
    filter_entry,
    form_availability,
    form_custodian,
    form_general_info_add,
    form_languages_add,
    form_languages_val,
    form_media,
    form_processed_from_primary,
    form_source_category,
    load_catalogue,
    make_choro_map,
    region_tree,
    select_entry_val,
)

##################
## streamlit
##################
st.set_page_config(
    page_title="BigScience Language Resource Catalogue Input Form",
    page_icon="https://avatars.githubusercontent.com/u/82455566",
    layout="wide",
    initial_sidebar_state="auto",
)

query_params = st.experimental_get_query_params()

page_description = """
# BigScience Data Catalogue

This application serves as the landing page for the **Catalogue of Language Data and Resources**
that is being built and maintained as part of the [BigScience workshop](https://bigscience.huggingface.co/).

The Catalogue app currently supports the following three functionalities:
- **Add a new entry**: This form can be used to add a new entry to the BigScience Data Sourcing Catalogue. To do so, enter add your name and email
then fill out the form according to the [**instructions.**](https://github.com/bigscience-workshop/data_sourcing/blob/master/sourcing_sprint/guide.md#guide-to-submitting-sources-to-the-bigscience-data-sourcing-hackathon)
- **Explore the current catalogue**: This page lets you explore the current catalogue and the geographical distribution of the entries.
- **Validate an existing entry**: Use this functionality to verify or add information to an existing entry.

Choose which functionality you want to make use of below.
"""

page_modes = {
    "add": "Add a new entry",
    "viz": "Explore the current catalogue",
    "val": "Validate an existing entry",
}

def main():
    if "save_state" not in st.session_state:
        st.session_state.save_state = {}

    st.sidebar.markdown(page_description, unsafe_allow_html=True)
    pages = {
        "add": add_page,
        "viz": viz_page,
        "val": val_page,
    }
    app_mode = st.sidebar.radio(
        label="App mode:",
        options=list(page_modes.keys()),
        format_func=lambda x: page_modes[x],
        index=list(page_modes).index(query_params.get("mode", ["add"])[0])
    )
    submission_info_dict = {
        "entry_uid": "",
        "submitted_by": "",
        "submitted_email": "",
        "submitted_date": "",
        "validated_by": "",
        "validated_date": "",
    }
    with st.sidebar.expander("User information", expanded=app_mode != "viz"):
        user_name = st.text_input(label="Name of submitter:")
        user_email = st.text_input(
            label="Email:"
        )
        if app_mode == "add":
            submission_info_dict["submitted_by"] = user_name
            submission_info_dict["submitted_email"] = user_email
        else:
            submission_info_dict["validated_by"] = user_name
        st.markdown("[Privacy policy](https://github.com/bigscience-workshop/data_sourcing/wiki/Required-User-Information-and-Privacy-Policy)")
    st.markdown("#### BigScience Catalogue of Language Data and Resources\n---\n")
    pages[app_mode](submission_info_dict)

##################
## SECTION: Add a new entry
##################
def add_page(submission_info_dict):
    entry_dict = {
        "uid": "",  # Unique Identifier string to link information and refer to the entry
        "type": "",  # in ["Primary source", "Language dataset", "Language organization"]
        "description": {
            "name": "",
            "description": "",
            "homepage": "",  # optional
            "validated": True,  # no need to have a second person validate this part
        },
        "languages": {
            "language_names": [],
            "language_comments": "",
            "language_locations": [],
            "validated": False,
        },
        "custodian": {  # for Primary source or Language daset - data owner or custodian
            "name": "",
            "in_catalogue": "",
            "type": "",
            "location": "",
            "contact_name": "",
            "contact_email": "",
            "contact_submitter": False,
            "additional": "",
            "validated": False,
        },
    }
    catalogue = load_catalogue()
    st.markdown("### Entry Category, Name, ID, Homepage, Description")
    form_general_info_add(entry_dict, app_categories)
    st.markdown("### Entry Languages and Locations")
    form_languages_add(entry_dict, app_categories, countries, region_tree)
    st.markdown("### Entry Representative, Owner, or Custodian")
    form_custodian(entry_dict, app_categories, countries, catalogue, "add")
    if entry_dict["type"] in ["primary", "processed"]:
        st.markdown("### Availability of the Resource: Procuring, Licenses, PII")
        form_availability(entry_dict, app_categories, "add")
    if entry_dict["type"] == "primary":
        st.markdown("### Primary Source Type")
        form_source_category(entry_dict, app_categories, "add")
    if entry_dict["type"] == "processed":
        st.markdown("### Primary Sources of the Processed Dataset")
        form_processed_from_primary(entry_dict, app_categories, catalogue, "add")
    if entry_dict["type"] in ["primary", "processed"]:
        st.markdown("### Media type, format, size, and processing needs")
        form_media(entry_dict, app_categories, "add")
    st.markdown("### Review and Save Entry")
    with st.expander("Show current entry", expanded=True):
        st.markdown("Do not forget to **save your entry** to the BigScience Data Catalogue!\n\nOnce you are done, please press the button below - this will either record the entry or tell you if there's anything you need to change first.")
        if st.button("Save entry to catalogue"):
            good_to_save, save_message = can_save(entry_dict, submission_info_dict, True)
            if good_to_save:
                submission_info_dict["entry_uid"] = entry_dict['uid']
                submission_info_dict["submitted_date"] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                json.dump(entry_dict, open(pjoin("entries", f"{entry_dict['uid']}.json"), "w", encoding="utf-8"), indent=2)
                json.dump(submission_info_dict, open(pjoin("entry_submitted_by", f"{entry_dict['uid']}.json"), "w", encoding="utf-8"), indent=2)
            else:
                st.markdown("##### Unable to save\n" + save_message)
        st.markdown(f"You are entering a new resource of type: *{entry_dict['type']}*")
        st.write(entry_dict)
        st.markdown("You can also download the entry as a `json` file with the following button:")
        st.download_button(
            label="Download entry dictionary",
            data=json.dumps(entry_dict, indent=2),
            file_name="default_entry_name.json" if entry_dict["uid"] == "" else f"{entry_dict['uid']}.json",
        )
    # save
    for k, v in st.session_state.items():
        if k != "save_state":
            st.session_state.save_state[k] = v

##################
## SECTION: Explore the current catalogue
##################
def viz_page(submission_info_dict):
    st.markdown("### Select entries to visualize")
    with st.expander("Select resources to visualize", expanded=False):
        st.markdown("##### Select entries by category, language, type of custodian or media")
        st.markdown(
            "You can select specific parts of the catalogue to visualize in this window." + \
            " Leave a field empty to select all values, or select specific options to only select entries that have one of the chosen values."
        )
        filter_dict = {
            "type": [],
            "languages": {
                "language_names": [],
            },
            "custodian": {  # for Primary source or Language daset - data owner or custodian
                "type": [],
            },
        }
        filter_dict["type"] = st.multiselect(
            label="I want to only see entries that are of the following category:",
            options=app_categories["entry_types"],
            format_func=lambda x: app_categories["entry_types"][x],
            key="viz_filter_type"
        )
        filter_dict["languages"]["language_names"] = st.multiselect(
            label="I want to only see entries that have one of the following languages:",
            options=list(app_categories["language_lists"]["language_groups"].keys()) + \
                app_categories["language_lists"]["niger_congo_languages"] + \
                app_categories["language_lists"]["indic_languages"],
                key="viz_filter_languages_language_names",
        )
        filter_dict["custodian"]["type"] = st.multiselect(
            label="I want to only see entries that corresponds to organizations or to data that id owned/managed by organizations of the following types:",
            options=app_categories["custodian_types"],
            key="viz_filter_custodian_type",
        )
        full_catalogue = load_catalogue()
        filtered_catalogue = [entry for uid, entry in full_catalogue.items() if filter_entry(entry, filter_dict) and not (uid == "")]
        st.write(f"Your query matched {len(filtered_catalogue)} entries in the current catalogue.")
        entry_location_type = st.radio(
            label="I want to visualize",
            options=[
                "Where the organizations or data custodians are located",
                "Where the language data creators are located",
            ],
            key="viz_show_location_type",
        )
        show_by_org = entry_location_type == "Where the organizations or data custodians are located"
    with st.expander("Map of entries", expanded=True):
        filtered_counts = {}
        for entry in filtered_catalogue:
            locations = [entry["custodian"]["location"]] if show_by_org else entry["languages"]["language_locations"]
            # be as specific as possible
            locations = [loc for loc in locations if not any([l in region_tree.get(loc, []) for l in locations])]
            for loc in locations:
                filtered_counts[loc] = filtered_counts.get(loc, 0) + 1
        world_map = make_choro_map(filtered_counts)
        folium_static(world_map, width=1150, height=600)
    with st.expander("View selected resources", expanded=False):
        st.write("You can further select locations to select entries from here:")
        filter_region_choices = sorted(set(
            [loc for entry in filtered_catalogue for loc in ([entry["custodian"]["location"]] if show_by_org else entry["languages"]["language_locations"])]
        ))
        filter_locs = st.multiselect(
            "View entries from the following locations:",
            options=filter_region_choices,
            key="viz_select_location",
        )
        filter_loc_dict = {"custodian": {"location": filter_locs}} if show_by_org else {"languages": {"language_locations": filter_locs}}
        filtered_catalogue_by_loc = [
            entry for entry in filtered_catalogue if filter_entry(entry, filter_loc_dict)
        ]
        view_entry = st.selectbox(
            label="Select an entry to see more detail:",
            options=filtered_catalogue_by_loc,
            format_func=lambda entry: f"{entry['uid']} | {entry['description']['name']} -- {entry['description']['description']}",
            key="viz_select_entry",
        )
        st.markdown(f"##### *Type:* {view_entry['type']} *UID:* {view_entry['uid']} - *Name:* {view_entry['description']['name']}\n\n{view_entry['description']['description']}")

##################
## SECTION: Validate an existing entry
##################
def val_page(submission_info_dict):
    st.markdown("### Entry selection")
    catalogue = load_catalogue()
    entry_dict = select_entry_val(catalogue, app_categories)
    st.markdown("### Entry Languages and Locations")
    if "languages" in entry_dict:
        form_languages_val(entry_dict, app_categories, countries, region_tree)
    if "custodian" in entry_dict:
        st.markdown("### Entry Representative, Owner, or Custodian")
        form_custodian(entry_dict, app_categories, countries, catalogue, "val")
    if "availability" in entry_dict:
        st.markdown("### Availability of the Resource: Procuring, Licenses, PII")
        form_availability(entry_dict, app_categories, "val")
    if "source_category" in entry_dict and entry_dict["type"] == "primary":
        st.markdown("### Primary Source Type")
        form_source_category(entry_dict, app_categories, "val")
    if "processed_from_primary" in entry_dict and entry_dict["type"] == "processed":
        st.markdown("### Primary Sources of the Processed Dataset")
        form_processed_from_primary(entry_dict, app_categories, catalogue, "val")
    if "media" in entry_dict and entry_dict["type"] in ["primary", "processed"]:
        st.markdown("### Media type, format, size, and processing needs")
        form_media(entry_dict, app_categories, "val")
    st.markdown("### Review and Save Entry")
    with st.expander("Show current entry", expanded=True):
        st.markdown("Do not forget to **save your work** to the BigScience Data Catalogue!\n\nOnce you are done, please press the button below - this will either record the entry or tell you if there's anything you need to change first.")
        if st.button("Save validated entry to catalogue"):
            good_to_save, save_message = can_save(entry_dict, submission_info_dict, False)
            if good_to_save:
                validation_info_dict = json.load(open(pjoin("entry_submitted_by", f"{entry_dict['uid']}.json"), encoding="utf-8"))
                validation_info_dict["validated_by"] = submission_info_dict['validated_by']
                validation_info_dict["validated_date"] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                friendly_date = re.sub(r"[^\w\s]", "_", validation_info_dict["validated_date"]).replace(" ", "_")
                json.dump(entry_dict, open(pjoin("entries", f"{entry_dict['uid']}-validated-{friendly_date}.json"), "w", encoding="utf-8"), indent=2)
                json.dump(validation_info_dict, open(pjoin("entry_submitted_by", f"{entry_dict['uid']}-validated-{friendly_date}.json"), "w", encoding="utf-8"), indent=2)
            else:
                st.markdown("##### Unable to save\n" + save_message)
        st.markdown(f"You are validating a resource of type: *{entry_dict['type']}*")
        st.write(entry_dict)
        st.markdown("You can also download the entry as a `json` file with the following button:")
        st.download_button(
            label="Download entry dictionary",
            data=json.dumps(entry_dict, indent=2),
            file_name="default_entry_name.json" if entry_dict["uid"] == "" else f"{entry_dict['uid']}.json",
        )

if __name__ == "__main__":
    main()
