import json
import re

import plotly.express as px
import streamlit as st

entry_type_help = """
- **Primary source**: a single source of language data (text or speech), such as a newspaper, radio, website, book collection, etc.
You will be asked to fill in information about the availability of the source, its properties including availability and presence of personal information,
its owners or producers, and the format of the language data.
- **Processed language dataset**: a processed NLP dataset containing language data that can be used for language modeling (most items should be at least a few sentences long).
You will be asked to fill in information about the dataset itself as well as the primary sources it was derived from
(e.g. Wikipedia, or news sites for most summarization datasets).
- **Language organization or advocate**: an organization or person holding or working on language resources of various types, formats, and languages.
Examples of such organization include e.g. the Internet Archive, Masakhane, the French Institut National de l'Audiovisuel, the Wikimedia Foundation, or other libraries, archival institutions, cultural organizations.
"""

entry_organization_text = """
#### Information about the language organization or advocate

In order to collaborate with the language organization or advocate to build up resources, we need contact and location information.
Please use this section to provide such information.
"""

entry_custodian_text = """
#### Information about the data owner or custodian

In order to make use of the language data indexed in this entry, we need information about the person or organization
that either owns or manages it (data custodian). Please use this section to provide such information.
"""

# Streamlit widgets with persistence
def make_multiselect(
    key, label, options, format_func=lambda x: x, help="", default=None
):
    if key in st.session_state:
        st.session_state.save_state[key] = st.session_state[key]
    elif default is not None:
        st.session_state.save_state[key] = default
    return st.multiselect(
        label=label,
        options=options,
        format_func=format_func,
        key=key,
        default=st.session_state.save_state.get(key, []),
        help=help,
    )


def make_selectbox(key, label, options, format_func=lambda x: x, help="", index=None, on_change=None):
    if key in st.session_state:
        st.session_state.save_state[key] = st.session_state[key]
    elif index is not None:
        st.session_state.save_state[key] = options[index]
    return st.selectbox(
        label=label,
        options=options,
        format_func=format_func,
        key=key,
        index=options.index(
            st.session_state.save_state.get(key, options[0])
        ),  # if st.session_state.save_state.get(key, options[0]) in options else 0,
        help=help,
        on_change=on_change,
    )


def make_radio(key, label, options, format_func=lambda x: x, help="", index=None):
    if key in st.session_state:
        st.session_state.save_state[key] = st.session_state[key]
    elif index is not None:
        st.session_state.save_state[key] = options[index]
    return st.radio(
        label=label,
        options=options,
        format_func=format_func,
        key=key,
        index=options.index(st.session_state.save_state.get(key, options[0])),
        help=help,
    )


def make_text_input(key, label, help="", value=None):
    if key in st.session_state:
        st.session_state.save_state[key] = st.session_state[key]
    elif value is not None:
        st.session_state.save_state[key] = value
    return st.text_input(
        label=label,
        key=key,
        value=st.session_state.save_state.get(key, ""),
        help=help,
    )


def make_text_area(key, label, help="", value=None):
    if key in st.session_state:
        st.session_state.save_state[key] = st.session_state[key]
    elif value is not None:
        st.session_state.save_state[key] = value
    return st.text_area(
        label=label,
        key=key,
        value=st.session_state.save_state.get(key, ""),
        help=help,
    )


def make_checkbox(key, label, help="", value=None):
    if key in st.session_state:
        st.session_state.save_state[key] = st.session_state[key]
    elif value is not None:
        st.session_state.save_state[key] = value
    return st.checkbox(
        label=label,
        key=key,
        value=st.session_state.save_state.get(key, False),
        help=help,
    )


# Page-specific forms
def form_general_info_add(entry_dict, options):
    with st.expander("General information", expanded=False):
        st.markdown(
            "##### Entry type, name, and summary"
        )  # TODO add collapsible instructions
        st.markdown(entry_type_help)
        entry_dict["type"] = st.radio(
            label="What resource type are you submitting?",
            options=options["entry_types"],
            format_func=lambda x: options["entry_types"][x],
            help=entry_type_help,
            key="add_description_type",
            index=list(options["entry_types"].keys()).index(
                st.session_state.save_state.get("add_description_type", "primary")
            ),
        )
        entry_dict["description"]["name"] = st.text_input(
            label=f"Provide a descriptive name for the resource",
            help="This should be a human-readable name such as e.g. **Le Monde newspaper** (primary source), **EXAMS QA dataset** (processed dataset), or **Creative Commons** (partner organization)",
            key="add_description_name",
            value=st.session_state.save_state.get("add_description_name", ""),
        )
        entry_dict["uid"] = st.text_input(
            label=f"Provide a short `snake_case` unique identifier for the resource",
            value=re.sub(
                r"[^\w\s]", "_", entry_dict["description"]["name"].lower()
            ).replace(" ", "_"),
            help="For example `le_monde_primary`, `exams_dataset`, or `creative_commons_org`",
            key="add_description_uid",
        )
        entry_dict["description"]["homepage"] = st.text_input(
            label=f"If available, provide a link to the home page for the resource",
            help="e.g. https://www.lemonde.fr/, https://github.com/mhardalov/exams-qa, or https://creativecommons.org/",
            key="add_description_homepage",
            value=st.session_state.save_state.get("add_description_homepage", ""),
        )
        entry_dict["description"]["description"] = st.text_area(
            label=f"Provide a short description of the resource",
            help="Describe the resource in a few words to a few sentences, the description will be used to index and navigate the catalogue",
            key="add_description_description",
            value=st.session_state.save_state.get("add_description_description", ""),
        )


def clear_validation_session_state():
    clear_keys = [k for k in st.session_state if k.startswith("val_") and k != "val_entry_select"]
    for val_key in clear_keys:
        del st.session_state[val_key]


def select_entry_val(catalogue, options):
    with st.expander("Select catalogue entry to validate", expanded=False):
        entry_ls = make_selectbox(
            key="val_entry_select",
            label="Select an entry to validate from the existing catalogue",
            options=catalogue,
            format_func=lambda e_ls: f"{e_ls[-1]['uid']} | {e_ls[-1]['description']['name']}",
            on_change=clear_validation_session_state,
        )
        if len(entry_ls) > 1:
            st.markdown("#### Note: this dataset has already been validated!")
            entry_dict = make_selectbox(
                key="val_entry_select_update",
                label="would you like to load a validated file for this entry?",
                options=entry_ls,
                format_func=lambda e_dct: e_dct.get("update_time", "original"),
            )
        else:
            entry_dict = entry_ls[0]
        st.markdown(
            f"##### Validating: {options['entry_types'].get(entry_dict['type'], '')} - {entry_dict['description']['name']}\n\n{entry_dict['description']['description']}"
        )
    return entry_dict


def form_languages_add(entry_dict, options, countries, region_tree):
    with st.expander("Language names and represented regions", expanded=False):
        language_help_text = """
        ##### Whose language is represented in the entry?
        For each entry, we need to catalogue which languages are represented or focused on,
        as characterized by both the **language names** and the **geographical distribution of the language data creators**.
        """
        st.markdown(language_help_text)
        entry_dict["languages"]["language_names"] = make_multiselect(
            key="add_languages_language_names_bigscience",
            label="If the entry covers language groups covered in the BigScience effort, select as many as apply here:",
            options=list(options["language_lists"]["language_groups"].keys()),
            format_func=lambda x: options["language_lists"]["language_groups"].get(
                x, ""
            ),
            help="This is the higher-level classification, Indic and African (Niger-Congo) languages open a new selection box for the specific language.",
        )
        if "Niger-Congo" in entry_dict["languages"]["language_names"]:
            entry_dict["languages"]["language_names"] += make_multiselect(
                key="add_languages_language_names_african",
                label="The entry covers African languages of the Niger-Congo family, select any that apply here:",
                options=options["language_lists"]["niger_congo_languages"],
                help="If the language you are looking for is not in the present list, you can add it through the **other languages** form below",
            )
        if "Indic" in entry_dict["languages"]["language_names"]:
            entry_dict["languages"]["language_names"] += make_multiselect(
                key="add_languages_language_names_indic",
                label="The entry covers Indic languages, select any that apply here:",
                options=options["language_lists"]["indic_languages"],
                help="If the language you are looking for is not in the present list, you can add it through the **other languages** form below",
            )
        if "Arabic" in entry_dict["languages"]["language_names"]:
            entry_dict["languages"]["language_names"] += make_multiselect(
                key="add_languages_language_names_arabic",
                label="The entry covers Arabic language data. Please provide any known information about the dialects here:",
                options=options["language_lists"]["arabic"],
                format_func=lambda x: f"{x} | {options['language_lists']['arabic'][x]}",
                help="If the dialect you are looking for is not in the present list, you can add it through the **other languages** form below",
            )
        if "Programming Language" in entry_dict["languages"]["language_names"]:
            entry_dict["languages"]["language_names"] += make_multiselect(
                key="add_languages_language_names_programming",
                label="The entry covers programming languages, select any that apply here:",
                options=[x["item"]["name"] for x in options["programming_languages"]],
            )
        entry_dict["languages"]["language_comments"] = make_text_input(
            key="add_languages_language_comments",
            label="Please add any additional comments about the language varieties here (e.g., significant presence of AAVE or code-switching)",
        )
        if make_checkbox(
            key="add_show_other_languages",
            label="Show other languages",
        ):
            entry_dict["languages"]["language_names"] += make_multiselect(
                key="add_languages_language_names_other",
                label="For entries that cover languages outside of the current BigScience list, select all that apply here:",
                options=[
                    ", ".join(x["description"]) for x in options["languages_bcp47"]
                ],
                help="This is a comprehensive list of languages obtained from the BCP-47 standard list.",
            )
        st.markdown(
            "---\n In addition to the names of the languages covered by the entry, we need to know where the language creators are **primarily** located.\n"
            + "You may select full *macroscopic areas* (e.g. continents) and/or *specific countries/regions*, choose all that apply."
        )
        entry_dict["languages"]["language_locations"] = make_multiselect(
            key="add_languages_language_locations_groups",
            label="Continents, world areas, and country groups. Select all that apply from the following",
            options=list(region_tree.keys()),
            format_func=lambda x: f"{x}: {', '.join(region_tree.get(x, [x]))}",
        )
        entry_dict["languages"]["language_locations"] += make_multiselect(
            key="add_languages_language_locations_regions",
            label="Countries, nations, regions, and territories. Select all that apply from the following",
            options=countries + ["other"],
        )


def form_languages_val(entry_dict, options, countries, region_tree):
    with st.expander("Validate language names and represented regions", expanded=False):
        language_choices = sorted(
            set(
                list(options["language_lists"]["language_groups"].keys())
                + options["language_lists"]["niger_congo_languages"]
                + options["language_lists"]["indic_languages"]
                + list(options["language_lists"]["arabic"].keys())
                + [", ".join(x["description"]) for x in options["languages_bcp47"]]
                + entry_dict["languages"]["language_names"]
            )
        ) + ["other"]
        new_lang_list = make_multiselect(
            key="val_languages_language_names",
            label="The entry currently has the following list of languages, you can add or remove any here:",
            options=language_choices,
            default=entry_dict["languages"]["language_names"],
        )
        new_lang_comment = make_text_input(
            key="val_languages_language_comments",
            label="The value currently has the following additional comment on the language(s) covered, you may edit it here",
            value=entry_dict["languages"]["language_comments"],
        )
        region_choices = sorted(
            set(
                list(region_tree.keys())
                + countries
                + entry_dict["languages"]["language_locations"]
            )
        ) + ["other"]
        new_region_list = make_multiselect(
            key="val_languages_language_locations",
            label="The entry currently has the following list of locations for the covered languages, you can add or remove any here:",
            options=region_choices,
            default=entry_dict["languages"]["language_locations"],
        )
    st.markdown(
        "If you are satisfied with the values for the fields above, press the button below to update and validate the **languages** section of the entry"
    )
    if make_checkbox(key="validated_languages", label="Validate: languages"):
        entry_dict["languages"]["language_names"] = new_lang_list
        entry_dict["languages"]["language_comments"] = new_lang_comment
        entry_dict["languages"]["language_locations"] = new_region_list
        entry_dict["languages"]["validated"] = True


def filter_entry(entry, filter_dct):
    res = True
    for k, v in entry.items():
        if k in filter_dct:
            if isinstance(v, dict):
                res = res and filter_entry(v, filter_dct[k])
            elif isinstance(v, list):
                res = res and (
                    len(filter_dct[k]) == 0 or any([e in filter_dct[k] for e in v])
                )
            else:
                res = res and (len(filter_dct[k]) == 0 or v in filter_dct[k])
    return res


def filter_catalogue_visualization(catalogue, options):
    st.markdown("### Select entries to visualize")
    with st.expander("Select resources to visualize", expanded=False):
        st.markdown(
            "##### Select entries by category, language, type of custodian or media"
        )
        st.markdown(
            "You can select specific parts of the catalogue to visualize in this window."
            + " Leave a field empty to select all values, or select specific options to only select entries that have one of the chosen values."
        )
        filter_by_options = [
            "resource type",
            "language names",
            "custodian type",
            "available for download",
            "license type",
            "personally identifying information - pii",
            "source type",
            "media type",
        ]
        filter_by = make_multiselect(
            key="viz_filter_by",
            label="You can filter the catalogue to only visualize entries that have certain properties, such as:",
            options=filter_by_options,
        )
        filter_dict = {}
        if "resource type" in filter_by:
            filter_dict["type"] = make_multiselect(
                key="viz_filter_type",
                label="I want to only see entries that are of the following category:",
                options=options["entry_types"],
                format_func=lambda x: options["entry_types"][x],
            )
        if "language names" in filter_by:
            filter_dict["languages"] = {}
            filter_dict["languages"]["language_names"] = make_multiselect(
                key="viz_filter_languages_language_names",
                label="I want to only see entries that have one of the following languages:",
                options=list(options["language_lists"]["language_groups"].keys())
                + options["language_lists"]["niger_congo_languages"]
                + options["language_lists"]["indic_languages"],
            )
            if make_checkbox(
                key="viz_show_other_languages",
                label="Show other languages",
            ):
                filter_dict["languages"]["language_names"] += make_multiselect(
                    key="viz_languages_language_names_other",
                    label="For entries that cover languages outside of the current BigScience list, select all that apply here:",
                    options=[
                        ", ".join(x["description"]) for x in options["languages_bcp47"]
                    ],
                    help="This is a comprehensive list of languages obtained from the BCP-47 standard list.",
                )
        if "custodian type" in filter_by:
            filter_dict["custodian"] = {}
            filter_dict["custodian"]["type"] = make_multiselect(
                key="viz_filter_custodian_type",
                label="I want to only see entries that corresponds to organizations or to data that id owned/managed by organizations of the following types:",
                options=options["custodian_types"],
            )
        if "available for download" in filter_by:
            filter_dict["availability"] = filter_dict.get("availability", {})
            filter_dict["availability"]["procurement"] = {}
            download_options = [
                "No - but the current owners/custodians have contact information for data queries",
                "No - we would need to spontaneously reach out to the current owners/custodians",
                "Yes - it has a direct download link or links",
                "Yes - after signing a user agreement",
            ]
            filter_dict["availability"]["procurement"][
                "for_download"
            ] = make_multiselect(
                key="viz_availability_procurement_for_download",
                label="Select based on whether the data can be obtained online:",
                options=download_options,
            )
        if "license type" in filter_by:
            filter_dict["availability"] = filter_dict.get("availability", {})
            filter_dict["availability"]["licensing"] = {}
            filter_dict["availability"]["licensing"][
                "license_properties"
            ] = make_multiselect(
                key="viz_availability_licensing_license_properties",
                label="Select primary entries that have the following license types",
                options=[
                    "public domain",
                    "multiple licenses",
                    "copyright - all rights reserved",
                    "open license",
                    "research use",
                    "non-commercial use",
                    "do not distribute",
                ],
            )
            primary_license_options = [
                "Unclear / I don't know",
                "Yes - the source material has an open license that allows re-use",
                "Yes - the dataset has the same license as the source material",
                "Yes - the dataset curators have obtained consent from the source material owners",
                "No - the license of the source material actually prohibits re-use in this manner",
            ]
            filter_dict["processed_from_primary"] = filter_dict.get(
                "processed_from_primary", {}
            )
            filter_dict["processed_from_primary"]["primary_license"] = make_multiselect(
                key="viz_processed_from_primary_primary_license",
                label="For datasets, selected based on: Is the license or commercial status of the source material compatible with the license of the dataset?",
                options=primary_license_options,
            )
        if "personally identifying information - pii" in filter_by:
            filter_dict["availability"] = filter_dict.get("availability", {})
            filter_dict["availability"]["pii"] = {}
            filter_dict["availability"]["pii"]["has_pii"] = make_multiselect(
                key="add_availability_pii_has_pii",
                label="Select based on: Does the language data in the resource contain personally identifiable or sensitive information?",
                help="See the guide for descriptions and examples. The default answer should be 'Yes'. Answers of 'No' and 'Unclear' require justifications.",
                options=["Yes", "Yes - text author name only", "No", "Unclear"],
            )
        if "source type" in filter_by:
            filter_dict["source_category"] = {}
            filter_dict["source_category"]["category_type"] = make_multiselect(
                key="viz_source_category_category_type",
                label="Select primary sources that correspond to:",
                options=["collection", "website"],
            )
            filter_dict["source_category"]["category_web"] = make_multiselect(
                key="viz_source_category_category_web",
                label="Select web-based primary sources that contain:",
                options=options["primary_taxonomy"]["website"],
            )
            filter_dict["source_category"]["category_media"] = make_multiselect(
                key="viz_source_category_category_media",
                label="Select primary sources that are collections of:",
                options=options["primary_taxonomy"]["collection"],
            )
            filter_dict["processed_from_primary"] = filter_dict.get(
                "processed_from_primary", {}
            )
            filter_dict["processed_from_primary"]["primary_types"] = make_multiselect(
                key="viz_processed_from_primary_primary_types",
                label="Select processed datasets whose primary sources contain:",
                options=[f"web | {w}" for w in options["primary_taxonomy"]["website"]]
                + options["primary_taxonomy"]["collection"],
            )
        if "media type" in filter_by:
            filter_dict["media"] = {}
            filter_dict["media"]["category"] = make_multiselect(
                key=f"viz_media_category",
                label="Select language data resources that contain:",
                options=["text", "audiovisual", "image"],
                help="Media data provided with transcription should go into **text**, then select the *transcribed* option. PDFs that have pre-extracted text information should go into **text**, PDFs that need OCR should go into **images**, select the latter if you're unsure",
            )
        filtered_catalogue = [
            entry
            for entry in catalogue
            if filter_entry(entry, filter_dict) and not (entry["uid"] == "")
        ]
        left_col, right_col = st.columns([4, 6])
        with left_col:
            _ = [st.write("\n") for _ in range(10)]
            st.markdown(
                f"##### Your query matched **{len(filtered_catalogue)}** entries in the current catalogue: \n"
            )
            st.download_button(
                label="Download filtered catalogue",
                data=json.dumps(filtered_catalogue, indent=2),
                file_name="filtered_catalogue.json",
            )
        with right_col:
            lang_counts = dict(
                [(ln, 0) for ln in options["language_lists"]["language_groups"]]
            )
            lang_counts["other"] = 0
            for entry in filtered_catalogue:
                other_lang = 1
                for ln in entry["languages"]["language_names"]:
                    if ln in lang_counts:
                        lang_counts[ln] += 1
                        other_lang = 0
                lang_counts["other"] += other_lang
            fig = px.pie(
                names=[ln for ln, ct in lang_counts.items()],
                values=[ct for ln, ct in lang_counts.items()],
                height=400,
            )
            st.plotly_chart(fig)
    return filtered_catalogue


# Re-usable forms
def form_custodian(entry_dict, options, countries, catalogue, mode):
    with st.expander(
        (
            "Advocate or organization information"
            if entry_dict["type"] == "organization"
            else "Data owner or custodian"
        ),
        expanded=False,
    ):
        st.markdown(
            (
                entry_organization_text
                if entry_dict["type"] == "organization"
                else entry_custodian_text
            )
        )
        if entry_dict["type"] == "organization":
            entry_dict["custodian"]["in_catalogue"] = ""
        else:
            organization_catalogue = dict(
                [
                    (entry["uid"], entry)
                    for entry in catalogue
                    if entry["type"] == "organization"
                ]
            )
            organization_keys = [""] + list(organization_catalogue.keys())
            organization_catalogue[""] = {"uid": "", "description": {"name": ""}}
            entry_dict["custodian"]["in_catalogue"] = make_selectbox(
                key=f"{mode}_custodian_in_catalogue",
                label="Is the data owned or managed by an organization corresponding to a catalogue entry?",
                options=organization_keys,
                format_func=lambda uid: f"{organization_catalogue[uid]['uid']} | {organization_catalogue[uid]['description']['name']}",
                index=organization_keys.index(
                    entry_dict["custodian"].get("in_catalogue", "")
                )
                if mode == "val"
                else None,
            )
        if entry_dict["custodian"]["in_catalogue"] == "":
            entry_dict["custodian"]["name"] = make_text_input(
                key=f"{mode}_custodian_name",
                label="Please enter the name of the person or entity that owns or manages the data (data custodian)",
                value=entry_dict["custodian"]["name"] if mode == "val" else None,
            )
            if mode == "add":
                custodian_type_options = [""] + options["custodian_types"] + ["other"]
            elif mode == "val":
                custodian_type_options = (
                    [""]
                    + sorted(
                        set(
                            options["custodian_types"]
                            + [entry_dict["custodian"]["type"]]
                        )
                    )
                    + ["other"]
                )
            entry_dict["custodian"]["type"] = make_selectbox(
                key=f"{mode}_custodian_type",
                label="Entity type: is the organization, advocate, or data custodian...",
                options=custodian_type_options,
                index=custodian_type_options.index(entry_dict["custodian"]["type"])
                if mode == "val"
                else None,
            )
            if entry_dict["custodian"]["type"] == "other":
                entry_dict["custodian"]["type"] = make_text_input(
                    key=f"{mode}_custodian_type_other",
                    label="You entered `other` for the entity type, how would you categorize them?",
                )
            entry_dict["custodian"]["location"] = make_selectbox(
                key=f"{mode}_custodian_location",
                label="Where is the entity located or hosted?",
                options=[""] + countries,
                help="E.g.: where does the **main author of the dataset** work, where is the **website hosted**, what is the physical **location of the library**, etc.?",
                index=([""] + countries).index(entry_dict["custodian"]["location"])
                if mode == "val"
                else None,
            )
            entry_dict["custodian"]["contact_name"] = make_text_input(
                key=f"{mode}_custodian_contact_name",
                label="Please enter the name of a contact person for the entity",
                value=entry_dict["custodian"]["contact_name"]
                if mode == "val"
                else entry_dict["description"]["name"],
            )
            entry_dict["custodian"]["contact_email"] = make_text_input(
                key=f"{mode}_custodian_contact_mail",
                label="If available, please enter an email address that can be used to ask them about using/obtaining the data:",
                value=entry_dict["custodian"]["contact_email"]
                if mode == "val"
                else None,
            )
            entry_dict["custodian"]["additional"] = make_text_input(
                key=f"{mode}_custodian_additional",
                label="Where can we find more information about the organization or data custodian? Please provide a URL",
                help="For example, please provide the URL of the web page with their contact information, the homepage of the organization, or even their Wikipedia page if it exists.",
                value=entry_dict["custodian"]["additional"] if mode == "val" else None,
            )
    if mode == "val":
        st.markdown(
            "If you are satisfied with the values for the fields above, press the button below to update and validate the **custodian** section of the entry"
        )
        if make_checkbox(key="validated_custodian", label="Validate: custodian"):
            entry_dict["custodian"]["validated"] = True


def form_availability(entry_dict, options, mode):
    if mode == "add":
        entry_dict["availability"] = {
            "procurement": {
                "for_download": "",
                "download_url": "",
                "download_email": "",
            },
            "licensing": {
                "has_licenses": "",
                "license_text": "",
                "license_properties": [],
                "license_list": [],
            },
            "pii": {
                "has_pii": "",
                "generic_pii_likely": "",
                "generic_pii_list": [],
                "numeric_pii_likely": "",
                "numeric_pii_list": [],
                "sensitive_pii_likely": "",
                "sensitive_pii_list": [],
                "no_pii_justification_class": "",
                "no_pii_justification_text": "",
            },
            "validated": False,
        }
    with st.expander(
        "Obtaining the data: online availability and data owner/custodian",
        expanded=False,
    ):
        st.markdown("##### Availability for download")
        download_options = [
            "No - but the current owners/custodians have contact information for data queries",
            "No - we would need to spontaneously reach out to the current owners/custodians",
            "Yes - it has a direct download link or links",
            "Yes - after signing a user agreement",
        ]
        entry_dict["availability"]["procurement"]["for_download"] = make_radio(
            key=f"add_availability_procurement_for_download",
            label="Can the data be obtained online?",
            options=download_options,
            index=download_options.index(
                entry_dict["availability"]["procurement"]["for_download"]
            )
            if mode == "val"
            else None,
        )
        if "Yes -" in entry_dict["availability"]["procurement"]["for_download"]:
            entry_dict["availability"]["procurement"]["download_url"] = make_text_input(
                key=f"{mode}_availability_procurement_download_url",
                label="Please provide the URL where the data can be downloaded",
                help="If the data source is a website or collection of files, please provided the top-level URL or location of the file directory",
                value=entry_dict["availability"]["procurement"]["download_url"]
                if mode == "val"
                else None,
            )
        else:
            entry_dict["availability"]["procurement"][
                "download_email"
            ] = make_text_input(
                key=f"{mode}_availability_procurement_download_email",
                label="Please provide the email of the person to contact to obtain the data",
                value=entry_dict["availability"]["procurement"]["download_email"]
                if mode == "val"
                else entry_dict["custodian"]["contact_email"],
                help="if it is different from the contact email entered for the data custodian in the **Data owner or custodian** section above",
            )
    with st.expander("Data licenses and Terms of Service", expanded=False):
        st.write(
            "Please provide as much information as you can find about the data's licensing and terms of use:"
        )
        entry_dict["availability"]["licensing"]["has_licenses"] = make_radio(
            key=f"{mode}_availability_licensing_has_licenses",
            label="Does the language data in the resource come with explicit licenses of terms of use?",
            options=["Yes", "No", "Unclear"],
            index=["Yes", "No", "Unclear"].index(
                entry_dict["availability"]["licensing"]["has_licenses"]
            )
            if mode == "val"
            else None,
        )
        if entry_dict["availability"]["licensing"]["has_licenses"] == "Yes":
            entry_dict["availability"]["licensing"][
                "license_properties"
            ] = make_multiselect(
                key=f"{mode}_availability_licensing_license_properties",
                label="Which of the following best characterize the licensing status of the data? Select all that apply:",
                options=[
                    "public domain",
                    "multiple licenses",
                    "copyright - all rights reserved",
                    "open license",
                    "research use",
                    "non-commercial use",
                    "do not distribute",
                ],
                default=entry_dict["availability"]["licensing"]["license_properties"]
                if mode == "val"
                else None,
            )
            st.markdown(
                "If the language data is shared under established licenses (such as e.g. **MIT license** or **CC-BY-3.0**), please select all that apply:"
            )
            entry_dict["availability"]["licensing"]["license_list"] = make_multiselect(
                key=f"{mode}_availability_licensing_license_list",
                label=f"Under which licenses is the data shared?",
                options=options["licenses"],
                default=entry_dict["availability"]["licensing"]["license_list"]
                if mode == "val"
                else None,
            )
            entry_dict["availability"]["licensing"]["license_text"] = make_text_area(
                key=f"{mode}_availability_licensing_license_text",
                label=f"If the resource has explicit terms of use or license text, please copy it in the following area",
                help="The text may be included in a link to the license webpage. You do not neet to copy the text if it corresponds to one of the established licenses that may be selected below.",
                value=entry_dict["availability"]["licensing"]["license_text"]
                if mode == "val"
                else None,
            )
        else:
            entry_dict["availability"]["licensing"]["license_text"] = make_text_area(
                key=f"{mode}_availability_licensing_license_text",
                label="Please provide your best assessment of whether the data can be used to train models while respecting the rights and wishes of the data creators and custodians. This field will serve as a starting point for further investigation.",
                value=entry_dict["availability"]["licensing"]["license_text"]
                if mode == "val"
                else None,
            )
    with st.expander("Personal Identifying Information", expanded=False):
        st.write(
            "Please provide as much information as you can find about the data's contents related to personally identifiable and sensitive information:"
        )
        entry_dict["availability"]["pii"]["has_pii"] = make_radio(
            key="add_availability_pii_has_pii",
            label="Does the language data in the resource contain personally identifiable or sensitive information?",
            help="See the guide for descriptions and examples. The default answer should be 'Yes'. Answers of 'No' and 'Unclear' require justifications.",
            options=["Yes", "Yes - text author name only", "No", "Unclear"],
        )
        if entry_dict["availability"]["pii"]["has_pii"] == "Yes":
            st.markdown(
                "If the resource does contain personally identifiable or sensitive information, please select what types are likely to be present:"
            )
            pii_likely_ranks = [
                "",
                "very likely",
                "somewhat likely",
                "unlikely",
                "none",
            ]
            entry_dict["availability"]["pii"]["generic_pii_likely"] = make_selectbox(
                key=f"{mode}_availability_pii_generic_pii_likely",
                label="How likely is the data to contain instances of generic PII, such as names or addresses?",
                options=pii_likely_ranks,
                index=pii_likely_ranks.index(
                    entry_dict["availability"]["pii"]["generic_pii_likely"]
                )
                if mode == "val"
                else None,
                help=f"Generic PII includes {', '.join(options['pii_categories']['generic'])}",
            )
            if "likely" in entry_dict["availability"]["pii"]["generic_pii_likely"]:
                entry_dict["availability"]["pii"][
                    "generic_pii_list"
                ] = make_multiselect(
                    key=f"{mode}_availability_pii_generic_pii_list",
                    label=f"What type of generic PII (e.g. names, emails, etc,) is the data most likely to contain?",
                    options=options["pii_categories"]["generic"],
                    default=entry_dict["availability"]["pii"]["generic_pii_list"]
                    if mode == "val"
                    else None,
                    help="E.g.: Does the resource contain names, birth dates, or personal life details?",
                )
            entry_dict["availability"]["pii"]["numeric_pii_likely"] = make_selectbox(
                key=f"{mode}_availability_pii_numeric_pii_likely",
                label="How likely is the data to contain instances of numeric PII, such as phone or social security numbers?",
                options=pii_likely_ranks,
                index=pii_likely_ranks.index(
                    entry_dict["availability"]["pii"]["numeric_pii_likely"]
                )
                if mode == "val"
                else None,
                help=f"Numeric PII includes {', '.join(options['pii_categories']['numbers'])}",
            )
            if "likely" in entry_dict["availability"]["pii"]["numeric_pii_likely"]:
                entry_dict["availability"]["pii"][
                    "numeric_pii_list"
                ] = make_multiselect(
                    key=f"{mode}_availability_pii_numeric_pii_list",
                    label=f"What type of numeric PII (e.g. phone numbers, social security numbers, etc.) is the data most likely to contain?",
                    options=options["pii_categories"]["numbers"],
                    default=entry_dict["availability"]["pii"]["numeric_pii_list"]
                    if mode == "val"
                    else None,
                    help="E.g.: Does the resource contain phone numbers, credit card numbers, or other numbers?",
                )
            entry_dict["availability"]["pii"]["sensitive_pii_likely"] = make_selectbox(
                key=f"{mode}_availability_pii_sensitive_pii_likely",
                label="How likely is the data to contain instances of Sensitive PII, such as health status or political beliefs?",
                options=pii_likely_ranks,
                index=pii_likely_ranks.index(
                    entry_dict["availability"]["pii"]["sensitive_pii_likely"]
                )
                if mode == "val"
                else None,
                help=f"Sensitive PII includes {', '.join(options['pii_categories']['sensitive'])}",
            )
            if "likely" in entry_dict["availability"]["pii"]["sensitive_pii_likely"]:
                entry_dict["availability"]["pii"][
                    "sensitive_pii_list"
                ] = make_multiselect(
                    key=f"{mode}_availability_pii_sensitive_pii_list",
                    label=f"What type of sensitive PII (e.g. health status, poilitcal opinions, sexual orientation, etc.) is the data most likely to contain?",
                    options=options["pii_categories"]["sensitive"],
                    default=entry_dict["availability"]["pii"]["sensitive_pii_list"]
                    if mode == "val"
                    else None,
                    help="E.g.: Does the resource contain sensitive data?",
                )
        else:
            no_pii_options = [
                "general knowledge not written by or referring to private persons",
                "fictional text",
                "other",
            ]
            entry_dict["availability"]["pii"][
                "no_pii_justification_class"
            ] = make_radio(
                key=f"{mode}_availability_pii_no_pii_justification_class",
                label="What is the justification for assuming that this resource does not contain any personally identifiable information?",
                options=no_pii_options,
                index=no_pii_options.index(
                    entry_dict["availability"]["pii"]["no_pii_justification_class"]
                )
                if mode == "val"
                else None,
            )
            if (
                entry_dict["availability"]["pii"]["no_pii_justification_class"]
                == "other"
            ):
                entry_dict["availability"]["pii"][
                    "no_pii_justification_text"
                ] = make_text_area(
                    key=f"{mode}_availability_pii_no_pii_justification_text",
                    label=f"If there is another reason for this resource not containing PII, please state why in the textbox below.",
                    value=entry_dict["availability"]["pii"]["no_pii_justification_text"]
                    if mode == "val"
                    else None,
                )
    if mode == "val":
        st.markdown(
            "If you are satisfied with the values for the fields above, press the button below to update and validate the **availability** section of the entry"
        )
        if make_checkbox(key="validated_availability", label="Validate: availability"):
            entry_dict["availability"]["validated"] = True


def form_source_category(entry_dict, options, mode):
    if mode == "add":
        entry_dict["source_category"] = {
            "category_type": "",
            "category_web": "",
            "category_media": "",
            "validated": False,
        }
    with st.expander("Source category", expanded=False):
        entry_dict["source_category"]["category_type"] = make_selectbox(
            key=f"{mode}_source_category_category_type",
            label="Is the resource best described as a:",
            options=["", "collection", "website", "other"],
            index=["", "collection", "website", "other"].index(
                entry_dict["source_category"]["category_type"]
            )
            if mode == "val"
            else None,
        )
        if entry_dict["source_category"]["category_type"] == "website":
            entry_dict["source_category"]["category_web"] = make_selectbox(
                key=f"{mode}_source_category_category_web",
                label="What kind of website?",
                options=[""] + options["primary_taxonomy"]["website"],
                index=([""] + options["primary_taxonomy"]["website"]).index(
                    entry_dict["source_category"]["category_web"]
                )
                if mode == "val"
                else None,
            )
        else:
            entry_dict["source_category"]["category_web"] = ""
        if (
            entry_dict["source_category"]["category_type"] == "collection"
            or "collection" in entry_dict["source_category"]["category_web"]
        ):
            entry_dict["source_category"]["category_media"] = make_selectbox(
                key=f"{mode}_source_category_category_media",
                label="What kind of collection?",
                options=[""] + options["primary_taxonomy"]["collection"],
                index=([""] + options["primary_taxonomy"]["collection"]).index(
                    entry_dict["source_category"]["category_media"]
                )
                if mode == "val"
                else None,
            )
        else:
            entry_dict["source_category"]["category_media"] = ""
        if entry_dict["source_category"]["category_type"] == "other":
            entry_dict["source_category"]["category_type"] = make_text_input(
                key=f"{mode}_source_category_category_type_other",
                label="You entered `other` for the resource type, how would you categorize it?",
            )
        if entry_dict["source_category"]["category_web"] == "other":
            entry_dict["source_category"]["category_web"] = make_text_input(
                key=f"{mode}_source_category_category_web_other",
                label="You entered `other` for the type of website, how would you categorize it?",
            )
        if entry_dict["source_category"]["category_media"] == "other":
            entry_dict["source_category"]["category_media"] = make_text_input(
                key=f"{mode}_source_category_category_media_other",
                label="You entered `other` for the type of collection, how would you categorize it?",
            )
    if mode == "val":
        st.markdown(
            "If you are satisfied with the values for the fields above, press the button below to update and validate the **source category** section of the entry"
        )
        if make_checkbox(
            key="validated_source_category", label="Validate: source category"
        ):
            entry_dict["source_category"]["validated"] = True


def form_processed_from_primary(entry_dict, options, catalogue, mode):
    if mode == "add":
        entry_dict["processed_from_primary"] = {
            "from_primary": "",
            "primary_availability": "",
            "primary_license": "",
            "primary_types": [],
            "validated": False,
        }
    with st.expander("List primary sources", expanded=False):
        st.write(
            "Please provide as much information as you can find about the data's primary sources:"
        )
        entry_dict["processed_from_primary"]["from_primary"] = make_radio(
            key=f"{mode}_processed_from_primary_from_primary",
            label="Was the language data in the dataset produced at the time of the dataset creation or was it taken from a primary source?",
            options=["Taken from primary source", "Original data"],
            index=["Taken from primary source", "Original data"].index(
                entry_dict["processed_from_primary"]["from_primary"]
            )
            if mode == "val"
            else None,
        )
        if (
            entry_dict["processed_from_primary"]["from_primary"]
            == "Taken from primary source"
        ):
            primary_available_options = [
                "Yes - their documentation/homepage/description is available",
                "Yes - they are fully available",
                "No - the dataset curators describe the primary sources but they are fully private",
                "No - the dataset curators kept the source data secret",
            ]
            entry_dict["processed_from_primary"]["primary_availability"] = make_radio(
                key=f"{mode}_processed_from_primary_primary_availability",
                label="Are the primary sources supporting the dataset available to investigate?",
                options=primary_available_options,
                index=primary_available_options.index(
                    entry_dict["processed_from_primary"]["primary_availability"]
                )
                if mode == "val"
                else None,
            )
            if (
                entry_dict["processed_from_primary"]["primary_availability"]
                != "No - the dataset curators kept the source data secret"
            ):
                primary_catalogue = dict(
                    [
                        (entry["uid"], entry)
                        for entry in catalogue
                        if entry["type"] == "primary"
                    ]
                )
                primary_keys = list(primary_catalogue.keys())
                entry_dict["processed_from_primary"][
                    "from_primary_entries"
                ] = make_multiselect(
                    key=f"{mode}_processed_from_primary_from_primary_entries",
                    label="Please select all primary sources for this dataset that are available in this catalogue",
                    options=primary_keys,
                    format_func=lambda uid: f"{primary_catalogue[uid]['uid']} | {primary_catalogue[uid]['description']['name']}",
                    default=entry_dict["processed_from_primary"]["from_primary_entries"]
                    if mode == "val"
                    else None,
                )
            if "Yes" in entry_dict["processed_from_primary"]["primary_availability"]:
                entry_dict["processed_from_primary"][
                    "primary_types"
                ] = make_multiselect(
                    key=f"{mode}_processed_from_primary_primary_types",
                    label="What kind of primary sources did the data curators use to make this dataset?",
                    options=[
                        f"web | {w}" for w in options["primary_taxonomy"]["website"]
                    ]
                    + options["primary_taxonomy"]["collection"],
                    default=entry_dict["processed_from_primary"]["primary_types"]
                    if mode == "val"
                    else None,
                )
                primary_license_options = [
                    "Unclear / I don't know",
                    "Yes - the source material has an open license that allows re-use",
                    "Yes - the dataset has the same license as the source material",
                    "Yes - the dataset curators have obtained consent from the source material owners",
                    "No - the license of the source material actually prohibits re-use in this manner",
                ]
                entry_dict["processed_from_primary"]["primary_license"] = make_radio(
                    key=f"{mode}_processed_from_primary_primary_license",
                    label="Is the license or commercial status of the source material compatible with the license of the dataset?",
                    options=primary_license_options,
                    index=primary_license_options.index(
                        entry_dict["processed_from_primary"]["primary_license"]
                    )
                    if mode == "val"
                    else None,
                )
    if mode == "val":
        st.markdown(
            "If you are satisfied with the values for the fields above, press the button below to update and validate the **processed primary source** section of the entry"
        )
        if make_checkbox(
            key="validated_processed_from_primary",
            label="Validate: processed primary source",
        ):
            entry_dict["processed_from_primary"]["validated"] = True


def form_media(entry_dict, options, mode):
    if mode == "add":
        entry_dict["media"] = {
            "category": [],
            "text_format": [],
            "audiovisual_format": [],
            "image_format": [],
            "database_format": [],
            "text_is_transcribed": "",
            "instance_type": "",
            "instance_count": "",
            "instance_size": "",
            "validated": False,
        }
    with st.expander("Media type", expanded=False):
        st.write(
            "Please provide information about the language data formats covered in the entry"
        )
        entry_dict["media"]["category"] = make_multiselect(
            key=f"{mode}_media_category",
            label="The language data in the resource is made up of:",
            options=["text", "audiovisual", "image"],
            default=entry_dict["media"]["category"] if mode == "val" else None,
            help="Media data provided with transcription should go into **text**, then select the *transcribed* option. PDFs that have pre-extracted text information should go into **text**, PDFs that need OCR should go into **images**, select the latter if you're unsure",
        )
        if "text" in entry_dict["media"]["category"]:
            text_format_dict = dict(
                [
                    (fmt, desc)
                    for fmt, desc in list(options["file_formats"]["Text"].items())
                    + list(options["file_formats"]["Web"].items())
                    + [("other", "other text file format")]
                ]
            )
            if mode == "val":
                for frm in entry_dict["media"]["text_format"]:
                    text_format_dict[frm] = text_format_dict.get(frm, frm)
            text_format_list = text_format_dict.keys()
            entry_dict["media"]["text_format"] = make_multiselect(
                key=f"{mode}_media_text_format",
                label="What text formats are present in the entry?",
                options=text_format_list,
                format_func=lambda x: f"{x} | {text_format_dict[x]}",
                default=entry_dict["media"]["text_format"] if mode == "val" else None,
            )
            # TODO - other selection in validation mode
            if mode == "add" and "other" in entry_dict["media"]["text_format"]:
                entry_dict["media"]["text_format"] += [
                    make_text_input(
                        key=f"{mode}_media_text_format_other",
                        label="You entered `other` for the text format, what format is it?",
                    )
                ]
            entry_dict["media"]["text_is_transcribed"] = make_radio(
                key=f"{mode}_media_text_is_transcribed",
                label="Was the text transcribed from another media format (e.g. audio or image)",
                options=["No", "Yes - audiovisual", "Yes - image"],
                index=["No", "Yes - audiovisual", "Yes - image"].index(
                    entry_dict["media"]["text_is_transcribed"]
                )
                if mode == "val"
                else None,
            )
        if (
            "audiovisual" in entry_dict["media"]["category"]
            or "audiovisual" in entry_dict["media"]["text_is_transcribed"]
        ):
            audiovisual_format_dict = dict(
                [
                    (fmt, desc)
                    for fmt, desc in list(options["file_formats"]["Audio"].items())
                    + list(options["file_formats"]["Video"].items())
                    + [("other", "other audiovisual file format")]
                ]
            )
            if mode == "val":
                for frm in entry_dict["media"]["audiovisual_format"]:
                    audiovisual_format_dict[frm] = audiovisual_format_dict.get(frm, frm)
            audiovisual_format_list = audiovisual_format_dict.keys()
            entry_dict["media"]["audiovisual_format"] = make_multiselect(
                key=f"{mode}_media_audiovisual_format",
                label="What format or formats do the audiovisual data come in?",
                options=audiovisual_format_list,
                format_func=lambda x: f"{x} | {audiovisual_format_dict[x]}",
                default=entry_dict["media"]["audiovisual_format"]
                if mode == "val"
                else None,
            )
            if mode == "add" and "other" in entry_dict["media"]["audiovisual_format"]:
                entry_dict["media"]["audiovisual_format"] += [
                    make_text_input(
                        key=f"{mode}_media_audiovisual_format_other",
                        label="You entered `other` for the audiovisual format, what format is it?",
                    )
                ]
        if (
            "image" in entry_dict["media"]["category"]
            or "image" in entry_dict["media"]["text_is_transcribed"]
        ):
            image_format_dict = dict(
                [
                    (fmt, desc)
                    for fmt, desc in list(options["file_formats"]["Image"].items())
                    + [("other", "other image file format")]
                ]
            )
            if mode == "val":
                for frm in entry_dict["media"]["image_format"]:
                    image_format_dict[frm] = image_format_dict.get(frm, frm)
            image_format_list = image_format_dict.keys()
            entry_dict["media"]["image_format"] = make_multiselect(
                key=f"{mode}_media_image_format",
                label="What format or formats do the image data come in?",
                options=image_format_list,
                format_func=lambda x: f"{x} | {image_format_dict[x]}",
                default=entry_dict["media"]["image_format"] if mode == "val" else None,
            )
            if mode == "add" and "other" in entry_dict["media"]["image_format"]:
                entry_dict["media"]["image_format"] += [
                    make_text_input(
                        key=f"{mode}_media_image_format_other",
                        label="You entered `other` for the image format, what format is it?",
                    )
                ]
        db_format_dict = dict(
            [
                (fmt, desc)
                for fmt, desc in list(options["file_formats"]["Data"].items())
                + list(options["file_formats"]["Database"].items())
                + list(options["file_formats"]["Compressed"].items())
                + [("other", "other database file format")]
            ]
        )
        if mode == "val":
            for frm in entry_dict["media"].get("database_format", []):
                db_format_dict[frm] = db_format_dict.get(frm, frm)
        db_format_list = db_format_dict.keys()
        entry_dict["media"]["database_format"] = make_multiselect(
            key=f"{mode}_media_database_format",
            label="If the data is presented as a database or compressed archive, please select all formats that apply here:",
            options=db_format_list,
            format_func=lambda x: f"{x} | {db_format_dict[x]}",
            default=entry_dict["media"].get("database_format", []) if mode == "val" else None,
        )
        if mode == "add" and "other" in entry_dict["media"]["database_format"]:
            entry_dict["media"]["database_format"] += [
                make_text_input(
                    key=f"{mode}_media_database_format_other",
                    label="You entered `other` for the database format, what format is it?",
                )
            ]
    with st.expander("Media amounts", expanded=False):
        st.write(
            "In order to estimate the amount of data in the dataset or primary source, we need a approximate count of the number of instances and the typical instance size therein."
        )
        instance_type_options = [
            "",
            "article",
            "post",
            "dialogue",
            "episode",
            "book",
            "webpage",
            "other",
        ]
        if (
            mode == "val"
            and entry_dict["media"]["instance_type"] not in instance_type_options
        ):
            instance_type_options += [entry_dict["media"]["instance_type"]]
        entry_dict["media"]["instance_type"] = make_selectbox(
            key=f"{mode}_media_instance_type",
            label="What does a single instance of language data consist of in this dataset/primary source?",
            options=instance_type_options,
            index=instance_type_options.index(entry_dict["media"]["instance_type"])
            if mode == "val"
            else None,
        )
        if entry_dict["media"]["instance_type"] == "other":
            entry_dict["media"]["instance_type"] = make_text_input(
                key=f"{mode}_media_instance_type_other",
                label="You entered `other` for the instance description. Please provide a description.",
            )
        instance_count_options = [
            "",
            "n<100",
            "100<n<1K",
            "1K<n<10K",
            "10K<n<100K",
            "100K<n<1M",
            "1M<n<1B",
            "n>1B",
        ]
        entry_dict["media"]["instance_count"] = make_selectbox(
            key=f"{mode}_media_instance_count",
            label="Please estimate the number of instances in the dataset",
            options=instance_count_options,
            index=instance_count_options.index(entry_dict["media"]["instance_count"])
            if mode == "val"
            else None,
        )
        instance_size_options = ["", "n<10", "10<n<100", "100<n<10,000", "n>10,000"]
        entry_dict["media"]["instance_size"] = make_selectbox(
            key=f"{mode}_media_instance_size",
            label="How long do you expect each instance to be on average interms of number of words?",
            options=instance_size_options,
            index=instance_size_options.index(entry_dict["media"]["instance_size"])
            if mode == "val"
            else None,
        )
    if mode == "val":
        st.markdown(
            "If you are satisfied with the values for the fields above, press the button below to update and validate the **media type and quantity** section of the entry"
        )
        if make_checkbox(
            key="validated_media", label="Validate: media type and quantity"
        ):
            entry_dict["media"]["validated"] = True
