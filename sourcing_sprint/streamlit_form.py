import json
import re
from datetime import datetime
from glob import glob
from os.path import isfile
from os.path import join as pjoin

import folium
import pandas as pd
import streamlit as st
from folium import Marker
from folium.plugins import MarkerCluster
from jinja2 import Template
from streamlit_folium import folium_static

##################
## resources
##################

### Types of catalogue entries
entry_types = {
    "primary": "Primary source",
    "processed": "Processed language dataset",
    "organization": "Language organization or advocate",
}

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

### Countries and languages
# from Wikipedia and https://unstats.un.org/unsd/methodology/m49/
regions, countries, region_tree = json.load(open("resources/country_regions.json", encoding="utf-8"))
country_centers = json.load(open("resources/country_center_coordinates.json", encoding="utf-8"))
country_mappings = json.load(open("resources/country_mappings.json", encoding="utf-8"))

bcp_47 = json.load(open("resources/bcp47.json", encoding="utf-8"))
bcp_47_langs = [x for x in bcp_47["subtags"] if x["type"] == "language"]

language_lists = json.load(open("resources/language_lists.json", encoding="utf-8"))
MAX_LANGS = 25
MAX_COUNTRIES = 25

### Primary source categories
primary_taxonomy = json.load(open("resources/primary_source_taxonomy.json", encoding="utf-8"))
MAX_SOURCES = 25

# entity categories
custodian_types = [
    "A private individual",
    "A commercial entity",
    "A library, museum, or archival institute",
    "A university or research institution",
    "A nonprofit/NGO (other)",
    "A government organization",
]

### Data accessibility
# from Data Tooling docs
pii_categories = json.load(open("resources/pii_categories.json", encoding="utf-8"))
MAX_PII = 25

licenses = json.load(open("resources/licenses.json", encoding="utf-8"))
MAX_LICENSES = 25

##################
## Mapping and visualization functions
##################
WORLD_GEO_URL = (
    "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json"
)

ICON_CREATE_FUNCTIOM = """
    function(cluster) {
        var markers = cluster.getAllChildMarkers();
        var sum = 0;
        for (var i = 0; i < markers.length; i++) {
            sum += markers[i].options.props.resources;
        }

        return L.divIcon({
             html: '<b>' + sum + '</b>',
             className: 'marker-cluster marker-cluster-small',
             iconSize: new L.Point(20, 20)
        });
    }
"""

class MarkerWithProps(Marker):
    _template = Template(
        """
        {% macro script(this, kwargs) %}
        var {{this.get_name()}} = L.marker(
            [{{this.location[0]}}, {{this.location[1]}}],
            {
                icon: new L.Icon.Default(),
                {%- if this.draggable %}
                draggable: true,
                autoPan: true,
                {%- endif %}
                {%- if this.props %}
                props : {{ this.props }}
                {%- endif %}
                }
            )
            .addTo({{this._parent.get_name()}});
        {% endmacro %}
        """
    )

    def __init__(self, location, popup=None, tooltip=None, icon=None, draggable=False, props=None):
        super(MarkerWithProps, self).__init__(
            location=location, popup=popup, tooltip=tooltip, icon=icon, draggable=draggable
        )
        self.props = json.loads(json.dumps(props))

@st.cache(allow_output_mutation=True)
def make_choro_map(resource_counts, marker_thres=0):
    world_map = folium.Map(tiles="cartodbpositron", location=[0, 0], zoom_start=1.5)
    marker_cluster = MarkerCluster(icon_create_function=ICON_CREATE_FUNCTIOM)
    marker_cluster.add_to(world_map)
    for name, count in resource_counts.items():
        if count > marker_thres and name in country_centers or name in country_mappings["to_center"]:
            country_center = country_centers[country_mappings["to_center"].get(name, name)]
            MarkerWithProps(
                location=[country_center["latitude"], country_center["longitude"]],
                popup=f"Country : {name}<br> \n Resources : {count} <br>",
                props={"name": name, "resources": count},
            ).add_to(marker_cluster)
    df_resource_counts = pd.DataFrame(
        [(country_mappings["to_outline"].get(n, n), c) for n, c in resource_counts.items()],
        columns=["Name", "Resources"],
    )
    folium.Choropleth(
        geo_data=WORLD_GEO_URL,
        name="resource map",
        data=df_resource_counts,
        columns=["Name", "Resources"],
        key_on="feature.properties.name",
        fill_color="PuRd",
        nan_fill_color="white",
    ).add_to(world_map)
    return world_map

##################
## App utility functions
##################
def load_catalogue():
    catalogue_list = [json.load(open(fname, encoding="utf-8")) for fname in glob("entries/*.json")]
    catalogue = dict([(dct["uid"], dct) for dct in catalogue_list])
    catalogue[''] = {
        "uid": "",
        "type": "",
        "description": {
            "name": "",
            "description": "",
        },
    }
    return catalogue

# check whether the entry can be written to the catalogue
def can_save(entry_dct, submission_dct, adding_mode):
    if add_mode and (entry_dct['uid'] == "" or isfile(pjoin("entries", f"{entry_dct['uid']}.json"))):
        return False, f"There is already an entry with `uid` {entry_dct['uid']}, you need to give your entry a different one before saving. You can look at the entry with this `uid` by switching to the **Validate an existing entry** mode of this app in the left sidebar."
    if adding_mode and submission_dct["submitted_by"] == "":
        return False, f"Please enter a name (or pseudonym) in the left sidebar before submitting this entry."
    if not adding_mode and submission_dct["validated_by"] == "":
        return False, f"Please enter a name (or pseudonym) in the left sidebar before validating this entry."
    if adding_mode and entry_dict["custodian"]["contact_submitter"] and submission_dct["submitted_email"] == "":
        return False, f"You said that you would be willing to reach out to the entity or organization. To do so, please enter an email we can use to follow up in the left sidebar."
    else:
        return True, ""

##################
## streamlit
##################
st.set_page_config(
    page_title="BigScience Language Resource Catalogue Input Form",
    page_icon="https://avatars.githubusercontent.com/u/82455566",
    layout="wide",
    initial_sidebar_state="auto",
)

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
st.sidebar.markdown(page_description, unsafe_allow_html=True)

app_mode = st.sidebar.radio(
    label="App mode:",
    options=[
        "Add a new entry",
        "Explore the current catalogue",
        "Validate an existing entry",
    ],
)
add_mode = app_mode == "Add a new entry"
viz_mode = app_mode == "Explore the current catalogue"
val_mode = app_mode == "Validate an existing entry"

submission_info_dict = {
    "entry_uid": "",
    "submitted_by": "",
    "submitted_email": "",
    "submitted_date": "",
    "validated_by": "",
    "validated_date": "",
}
if add_mode or val_mode:
    with st.sidebar.form("submitter_information"):
        user_name = st.text_input(label="Name of submitter:")
        user_email = st.text_input(
            label="Email (optional, enter if you are available to follow up on this catalogue entry):"
        )
        submitted_info = st.form_submit_button("Submit self information")
        if add_mode:
            submission_info_dict["submitted_by"] = user_name
            submission_info_dict["submitted_email"] = user_email
        else:
            submission_info_dict["validated_by"] = user_name

st.markdown("#### BigScience Catalogue of Language Data and Resources\n---\n")

# switch between expanded tabs
if add_mode:
    col_sizes = [60, 40, 5, 1, 5, 1, 1]
if viz_mode:
    col_sizes = [5, 1, 100, 1, 5, 1, 1]
if val_mode:
    col_sizes = [5, 1, 5, 1, 60, 40, 1]

form_col, display_col, viz_col, _, val_col, val_display_col, _ = st.columns(col_sizes)

##################
## SECTION: Add a new entry
##################
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
        "type": "",
        "location": "",
        "contact_name": "",
        "contact_email": "",
        "contact_submitter": False,
        "additional": "",
        "validated": False,
    },
}

form_col.markdown("### Entry Category, Name, ID, Homepage, Description" if add_mode else "")
with form_col.expander(
    "General information" if add_mode else "",
    expanded=add_mode,
):
    st.markdown("##### Entry type, name, and summary")  # TODO add collapsible instructions
    st.markdown(entry_type_help if add_mode else "")
    entry_dict["type"] = st.radio(
        label="What resource type are you submitting?",
        options=entry_types,
        format_func=lambda x: entry_types[x],
        help=entry_type_help,
    )
    entry_dict["description"]["name"] = st.text_input(
        label=f"Provide a descriptive name for the resource",
        help="This should be a human-readable name such as e.g. **Le Monde newspaper** (primary source), **EXAMS QA dataset** (processed dataset), or **Creative Commons** (partner organization)",
    )
    entry_dict["uid"] = st.text_input(
        label=f"Provide a short `snake_case` unique identifier for the resource",
        value=re.sub(r"[^\w\s]", "_", entry_dict["description"]["name"].lower()).replace(" ", "_"),
        help="For example `le_monde_primary`, `exams_dataset`, or `creative_commons_org`",
    )
    entry_dict["description"]["homepage"] = st.text_input(
        label=f"If available, provide a link to the home page for the resource",
        help="e.g. https://www.lemonde.fr/, https://github.com/mhardalov/exams-qa, or https://creativecommons.org/",
    )
    entry_dict["description"]["description"] = st.text_area(
        label=f"Provide a short description of the resource",
        help="Describe the resource in a few words to a few sentences, the description will be used to index and navigate the catalogue",
    )

form_col.markdown("### Entry Languages and Locations" if add_mode else "")
with form_col.expander(
    "Language names and represented regions" if add_mode else "",
    expanded=add_mode,
):
    language_help_text = """
    ##### Whose language is represented in the entry?
    For each entry, we need to catalogue which languages are represented or focused on,
    as characterized by both the **language names** and the **geographical distribution of the language data creators**.
    """
    st.markdown(language_help_text)
    entry_dict["languages"]["language_names"] = st.multiselect(
        label="If the entry covers language groups covered in the BigScience effort, select as many as apply here:",
        options=list(language_lists["language_groups"].keys()),
        format_func=lambda x: language_lists["language_groups"].get(x, ""),
        help="This is the higher-level classification, Indic and African (Niger-Congo) languages open a new selection box for the specific language.",
    )
    if "Niger-Congo" in entry_dict["languages"]["language_names"]:
        entry_dict["languages"]["language_names"] += st.multiselect(
            label="The entry covers African languages of the Niger-Congo family, select any that apply here:",
            options=language_lists["niger_congo_languages"],
            help="If the language you are looking for is not in the present list, you can add it through the **other languages** form below",
        )
    if "Indic" in entry_dict["languages"]["language_names"]:
        entry_dict["languages"]["language_names"] += st.multiselect(
            label="The entry covers Indic languages, select any that apply here:",
            options=language_lists["indic_languages"],
            help="If the language you are looking for is not in the present list, you can add it through the **other languages** form below",
        )
    if "Arabic" in entry_dict["languages"]["language_names"]:
        entry_dict["languages"]["language_names"] += st.multiselect(
            label="The entry covers Arabic language data. Please provide any known information about the dialects here:",
            options=language_lists["arabic"],
            format_func=lambda x: f"{x} | {language_lists['arabic'][x]}",
            help="If the dialect you are looking for is not in the present list, you can add it through the **other languages** form below",
        )
    entry_dict["languages"]["language_comments"] = st.text_input(
        label="Please add any additional comments about the language varieties here (e.g., significant presence of AAVE or code-switching)"
    )
    if st.checkbox("Show other languages"):
        entry_dict["languages"]["language_names"] = st.multiselect(
            label="For entries that cover languages outside of the current BigScience list, select all that apply here:",
            options=[", ".join(x["description"]) for x in bcp_47_langs],
            help="This is a comprehensive list of languages obtained from the BCP-47 standard list, please select one using the search function",
        )
    st.markdown(
        "---\n In addition to the names of the languages covered by the entry, we need to know where the language creators are **primarily** located.\n"
        + "You may select full *macroscopic areas* (e.g. continents) and/or *specific countries/regions*, choose all that apply."
    )
    entry_dict["languages"]["language_locations"] = st.multiselect(
        label="Continents, world areas, and country groups. Select all that apply from the following",
        options=["World-Wide"] + list(region_tree.keys()),
        format_func=lambda x: f"{x}: {', '.join(region_tree.get(x, [x]))}",
    )
    entry_dict["languages"]["language_locations"] += st.multiselect(
        label="Countries, nations, regions, and territories. Select all that apply from the following",
        options=countries + ["other"],
    )

form_col.markdown("### Entry Representative, Owner, or Custodian" if add_mode else "")
with form_col.expander(
    ("Advocate or organization information" if entry_dict["type"] == "organization" else "Data owner or custodian")
    if add_mode
    else "",
    expanded=add_mode,
):
    st.markdown((entry_organization_text if entry_dict["type"] == "organization" else entry_custodian_text) if add_mode else "")
    if entry_dict["type"] == "organization":
        entry_dict["custodian"]["name"] = entry_dict["description"]["name"]
    else:
        entry_dict["custodian"]["name"] = st.text_input(
            label="Please enter the name of the person or entity that owns or manages the data (data custodian)",
        )
    entry_dict["custodian"]["type"] = st.selectbox(
        label="Entity type: is the organization, advocate, or data custodian...",
        options=[""] + custodian_types + ["other"],
    )
    if entry_dict["custodian"]["type"] == "other":
        entry_dict["custodian"]["type"] = st.text_input(
            label="You entered `other` for the entity type, how would you categorize them?",
        )
    entry_dict["custodian"]["location"] = st.selectbox(
        label="Where is the entity located or hosted?",
        options=[""] + countries,
        help="E.g.: where does the **main author of the dataset** work, where is the **website hosted**, what is the physical **location of the library**, etc.?",
    )
    entry_dict["custodian"]["contact_name"] = st.text_input(
        label="Please enter the name of a contact person for the entity",
        value=entry_dict["description"]["name"],
    )
    entry_dict["custodian"]["contact_email"] = st.text_input(
        label="If available, please enter an email address that can be used to ask them about using/obtaining the data:"
    )
    entry_dict["custodian"]["contact_submitter"] = st.checkbox(
        label="Would you be willing to reach out to the entity to ask them about collaborating or using their data (with support from the BigScience data sourcing team)?"
        + " If so, make sure to fill out your email in the sidebar.",
    )
    entry_dict["custodian"]["additional"] = st.text_input(
        label="Where can we find more information about the organization or data custodian? Please provide a URL",
        help="For example, please provide the URL of the web page with their contact information, the homepage of the organization, or even their Wikipedia page if it exists.",
    )

if entry_dict["type"] in ["primary", "processed"]:
    form_col.markdown("### Availability of the Resource: Procuring, Licenses, PII" if add_mode else "")
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
    with form_col.expander(
        "Obtaining the data: online availability and data owner/custodian" if add_mode else "",
        expanded=add_mode,
    ):
        st.markdown("##### Availability for download")
        entry_dict["availability"]["procurement"]["for_download"] = st.radio(
            label="Can the data be obtained online?",
            options=[
                "Yes - it has a direct download link or links",
                "Yes - after signing a user agreement",
                "No - but the current owners/custodians have contact information for data queries",
                "No - we would need to spontaneously reach out to the current owners/custodians",
            ],
            index=3,
        )
        if "Yes -" in entry_dict["availability"]["procurement"]["for_download"]:
            entry_dict["availability"]["procurement"]["download_url"] = st.text_input(
                label="Please provide the URL where the data can be downloaded",
                help="If the data source is a website or collection of files, please provided the top-level URL or location of the file directory",
            )
        else:
            entry_dict["availability"]["procurement"]["download_url"] = st.text_input(
                label="Please provide the email of the person to contact to obtain the data",
                value=entry_dict["custodian"]["contact_email"],
                help="if it is different from the contact email entered for the data custodian in the **Data owner or custodian** section above",
            )

    with form_col.expander(
        "Data licenses and Terms of Service" if add_mode else "",
        expanded=add_mode,
    ):
        st.write("Please provide as much information as you can find about the data's licensing and terms of use:")
        entry_dict["availability"]["licensing"]["has_licenses"] = st.radio(
            label="Does the language data in the resource come with explicit licenses of terms of use?",
            options=["Yes", "No", "Unclear"],
        )
        if entry_dict["availability"]["licensing"]["has_licenses"] == "Yes":
            entry_dict["availability"]["licensing"]["license_properties"] = st.multiselect(
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
            )
            st.markdown(
                "If the language data is shared under established licenses (such as e.g. **MIT license** or **CC-BY-3.0**), please select all that apply:"
            )
            entry_dict["availability"]["licensing"]["license_list"] = st.multiselect(
                label=f"Under which licenses is the data shared?",
                options=licenses,
            )
            entry_dict["availability"]["licensing"]["license_text"] = st.text_area(
                label=f"If the resource has explicit terms of use or license text, please copy it in the following area",
                help="The text may be included in a link to the license webpage. You do not neet to copy the text if it corresponds to one of the established licenses that may be selected below.",
            )
        else:
            entry_dict["availability"]["licensing"]["license_text"] = st.text_area(
                label="Please provide your best assessment of whether the data can be used to train models while respecting the rights and wishes of the data creators and custodians. This field will serve as a starting point for further investigation.",
            )

    with form_col.expander(
        "Personal Identifying Information" if add_mode else "",
        expanded=add_mode,
    ):
        st.write(
            "Please provide as much information as you can find about the data's contents related to personally identifiable and sensitive information:"
        )
        entry_dict["availability"]["pii"]["has_pii"] = st.radio(
            label="Does the language data in the resource contain personally identifiable or sensitive information?",
            help="See the guide for descriptions and examples. The default answer should be 'Yes'. Answers of 'No' and 'Unclear' require justifications.",
            options=["Yes", "Yes - text author name only", "No", "Unclear"],
        )
        if entry_dict["availability"]["pii"]["has_pii"] == "Yes":
            st.markdown(
                "If the resource does contain personally identifiable or sensitive information, please select what types are likely to be present:"
            )
            entry_dict["availability"]["pii"]["generic_pii_likely"] = st.selectbox(
                label="How likely is the data to contain instances of generic PII, such as names or addresses?",
                options=["", "very likely", "somewhat likely", "unlikely", "none"],
                help=f"Generic PII includes {', '.join(pii_categories['generic'])}"
            )
            if "likely" in entry_dict["availability"]["pii"]["generic_pii_likely"]:
                entry_dict["availability"]["pii"]["generic_pii_list"] = st.multiselect(
                    label=f"What type of generic PII (e.g. names, emails, etc,) is the data most likely to contain?",
                    options=pii_categories["generic"],
                    help="E.g.: Does the resource contain names, birth dates, or personal life details?",
                )
            entry_dict["availability"]["pii"]["numeric_pii_likely"] = st.selectbox(
                label="How likely is the data to contain instances of numeric PII, such as phone or social security numbers?",
                options=["", "very likely", "somewhat likely", "unlikely", "none"],
                help=f"Numeric PII includes {', '.join(pii_categories['numbers'])}"
            )
            if "likely" in entry_dict["availability"]["pii"]["numeric_pii_likely"]:
                entry_dict["availability"]["pii"]["numeric_pii_list"] = st.multiselect(
                    label=f"What type of numeric PII (e.g. phone numbers, social security numbers, etc.) is the data most likely to contain?",
                    options=pii_categories["numbers"],
                    help="E.g.: Does the resource contain phone numbers, credit card numbers, or other numbers?",
                )
            entry_dict["availability"]["pii"]["sensitive_pii_likely"] = st.selectbox(
                label="How likely is the data to contain instances of Sensitive PII, such as health status or political beliefs?",
                options=["", "very likely", "somewhat likely", "unlikely", "none"],
                help=f"Sensitive PII includes {', '.join(pii_categories['sensitive'])}"
            )
            if "likely" in entry_dict["availability"]["pii"]["sensitive_pii_likely"]:
                entry_dict["availability"]["pii"]["sensitive_pii_list"] = st.multiselect(
                    label=f"What type of sensitive PII (e.g. health status, poilitcal opinions, sexual orientation, etc.) is the data most likely to contain?",
                    options=pii_categories["sensitive"],
                    help="E.g.: Does the resource contain sensitive data?",
                )
        else:
            entry_dict["availability"]["pii"]["no_pii_justification_class"] = st.radio(
                label="What is the justification for assuming that this resource does not contain any personally identifiable information?",
                options=[
                    "general knowledge not written by or referring to private persons",
                    "fictional text",
                    "other",
                ],
            )
            if entry_dict["availability"]["pii"]["no_pii_justification_class"] == "other":
                entry_dict["availability"]["pii"]["no_pii_justification_text"] = st.text_area(
                    label=f"If there is another reason for this resource not containing PII, please state why in the textbox below.",
                    key="processed_justification_other",
                )

if entry_dict["type"] == "primary":
    form_col.markdown("### Primary Source Type" if add_mode else "")
    entry_dict["source_category"] = {
        "category_type": "",
        "category_web": "",
        "category_media": "",
        "validated": False,
    }
    with form_col.expander(
        "Source category" if add_mode else "",
        expanded=add_mode,
    ):
        primary_tax_top = st.selectbox(
            label="Is the resource best described as a:",
            options=["", "collection", "website", "other"],
        )
        if primary_tax_top == "website":
            primary_tax_web = st.selectbox(
                label="What kind of website?",
                options=[""] + primary_taxonomy["website"],
            )
        else:
            primary_tax_web = ""
        if primary_tax_top == "collection" or "collection" in primary_tax_web:
            primary_tax_col = st.selectbox(
                label="What kind of collection?",
                options=[""] + primary_taxonomy["collection"],
            )
        else:
            primary_tax_col = ""
        if primary_tax_top == "other":
            primary_tax_top = st.text_input(
                label="You entered `other` for the resource type, how would you categorize it?",
            )
        if primary_tax_web == "other":
            primary_tax_web = st.text_input(
                label="You entered `other` for the type of website, how would you categorize it?",
            )
        if primary_tax_col == "other":
            primary_tax_col = st.text_input(
                label="You entered `other` for the type of collection, how would you categorize it?",
            )
        entry_dict["source_category"]["category_type"] = primary_tax_top
        entry_dict["source_category"]["category_web"] = primary_tax_web
        entry_dict["source_category"]["category_media"] = primary_tax_col

if entry_dict["type"] == "processed":
    form_col.markdown("### Primary Sources of the Processed Dataset" if add_mode else "")
    entry_dict["processed_from_primary"] = {
        "from_primary": "",
        "primary_availability": "",
        "primary_license": "",
        "primary_types": [],
        "validated": False,
    }
    with form_col.expander(
        "List primary sources" if add_mode else "",
        expanded=add_mode,
    ):
        processed_sources = {}
        st.write("Please provide as much information as you can find about the data's primary sources:")
        entry_dict["processed_from_primary"]["from_primary"] = st.radio(
            label="Was the language data in the dataset produced at the time of the dataset creation or was it taken from a primary source?",
            options=["Original data", "Taken from primary source"],
            index=1,
        )
        if entry_dict["processed_from_primary"]["from_primary"] == "Taken from primary source":
            entry_dict["processed_from_primary"]["primary_availability"] = st.radio(
                label="Are the primary sources supporting the dataset available to investigate?",
                options=[
                    "Yes - they are fully available",
                    "Yes - their documentation/homepage/description is available",
                    "No - the dataset curators describe the primary sources but they are fully private",
                    "No - the dataset curators kept the source data secret",
                ],
                index=1,
            )
            if "Yes" in entry_dict["processed_from_primary"]["primary_availability"]:
                entry_dict["processed_from_primary"]["primary_types"] = st.multiselect(
                    label="What kind of primary sources did the data curators use to make this dataset?",
                    options=[f"web | {w}" for w in primary_taxonomy["website"]] + primary_taxonomy["collection"],
                )
                entry_dict["processed_from_primary"]["primary_license"] = st.radio(
                    label="Is the license or commercial status of the source material compatible with the license of the dataset?",
                    options=[
                        "Yes - the source material has an open license that allows re-use",
                        "Yes - the dataset has the same license as the source material",
                        "Yes - the dataset curators have obtained consent from the source material owners",
                        "Unclear / I don't know",
                        "No - the license of the source material actually prohibits re-use in this manner",
                    ],
                    index=3,
                )

if entry_dict["type"] in ["primary", "processed"]:
    form_col.markdown("### Media type, format, size, and processing needs" if add_mode else "")
    entry_dict["media"] = {
        "category": [],
        "text_format": [],
        "audiovisual_format": [],
        "image_format": [],
        "text_is_transcribed": "",
        "instance_type": "",
        "instance_count": "",
        "instance_size": "",
        "validated": False,
    }
    with form_col.expander(
        "Media type" if add_mode else "",
        expanded=add_mode,
    ):
        st.write("Please provide information about the language data formats covered in the entry")
        entry_dict["media"]["category"] = st.multiselect(
            label="The language data in the resource is made up of:",
            options=["text", "audiovisual", "image"],
            help="Media data provided with transcription should go into **text**, then select the *transcribed* option. PDFs that have pre-extracted text information should go into **text**, PDFs that need OCR should go into **images**, select the latter if you're unsure",
        )
        if "text" in entry_dict["media"]["category"]:
            entry_dict["media"]["text_format"] = st.multiselect(
                label="What text formats are present in the entry?",
                options=["plain text", "HTML", "PDF", "XML", "mediawiki", "other"],
            )
            if "other" in entry_dict["media"]["text_format"]:
                entry_dict["media"]["text_format"] += st.text_input(
                    label="You entered `other` for the text format, what format is it?",
                )
            entry_dict["media"]["text_is_transcribed"] = st.radio(
                label="Was the text transcribed from another media format (e.g. audio or image)",
                options=["Yes - audiovisual", "Yes - image", "No"],
                index=2,
            )
        if "audiovisual" in entry_dict["media"]["category"] or "audiovisual" in entry_dict["media"]["text_is_transcribed"]:
            entry_dict["media"]["audiovisual_format"] = st.multiselect(
                label="What format or formats do the audiovisual data come in?",
                options=["mp4", "wav", "video", "other"],
            )
            if "other" in entry_dict["media"]["audiovisual_format"]:
                entry_dict["media"]["audiovisual_format"] += st.text_input(
                    label="You entered `other` for the audiovisual format, what format is it?",
                )
        if "image" in entry_dict["media"]["category"] or "image" in entry_dict["media"]["text_is_transcribed"]:
            entry_dict["media"]["image_format"] = st.multiselect(
                label="What format or formats do the image data come in?",
                options=["JPEG", "PNG", "PDF", "TIFF", "other"],
            )
            if "other" in entry_dict["media"]["image_format"]:
                entry_dict["media"]["image_format"] += st.text_input(
                    label="You entered `other` for the image format, what format is it?",
                )

    with form_col.expander(
        "Media amounts" if add_mode else "",
        expanded=add_mode,
    ):
        st.write("In order to estimate the amount of data in the dataset or primary source, we need a approximate count of the number of instances and the typical instance size therein.")
        entry_dict["media"]["instance_type"] = st.selectbox(
            label="What does a single instance of language data consist of in this dataset/primary source?",
            options=["", "article", "post", "dialogue", "episode", "book", "other"],
        )
        if entry_dict["media"]["instance_type"] == "other":
            entry_dict["media"]["instance_type"] = st.text_input(
                label="You entered `other` for the instance description. Please provide a description.",
            )
        entry_dict["media"]["instance_count"] = st.selectbox(
            label="Please estimate the number of instances in the dataset",
            options=["", "n<100", "100<n<1K", "1K<n<10K", "10K<n<100K", "100K<n<1M", "1M<n<1B", "n>1B"],
        )
        entry_dict["media"]["instance_size"] = st.selectbox(
            label="How long do you expect each instance to be on average interms of number of words?",
            options=["", "n<10", "10<n<100", "100<n<10,000", "n>10,000"],
        )

# visualize and download
display_col.markdown("### Review and Save Entry" if add_mode else "")
if add_mode:
    with display_col.expander("Show current entry" if add_mode else "", expanded=add_mode):
        st.markdown("Do not forget to **save your entry** to the BigScience Data Catalogue!\n\nOnce you are done, please press the button below - this will either record the entry or tell you if there's anything you need to change first.")
        if st.button("Save entry to catalogue"):
            good_to_save, save_message = can_save(entry_dict, submission_info_dict, add_mode)
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

##################
## SECTION: Explore the current catalogue
##################
viz_col.markdown("### Select entries to visualize" if viz_mode else "")
with viz_col.expander("Select resources to visualize" if viz_mode else "", expanded=viz_mode):
    st.write("TODO: add selection widgets")

with viz_col.expander("Map of entries" if viz_mode else "", expanded=viz_mode):
    if viz_mode:
        # make random count data
        random_counts = {
            "France": 45,
            "United States": 128,
            "Chile": 10,
            "Belgium": 4,
            "Puerto Rico": 3,
            "Canada": 25,
            "Greece": 5,
            "South Africa": 34,
            "Algeria": 5,
            "Lybia": 7,
            "Kenya": 23,
            "Rwanda": 4,
            "Vietnam": 10,
            "Hong Kong": 12,
            "China": 28,
            "New Zealand": 12,
            "Australia": 4,
            "Iceland": 30,
        }
        world_map = make_choro_map(random_counts)
        folium_static(world_map, width=1150, height=600)

viz_col.markdown("### Search entry names and descriptions" if viz_mode else "")
with viz_col.expander("ElasticSearch of resource names and descriptions" if viz_mode else "", expanded=viz_mode):
    st.write("TODO: implement ElasticSearch index and enable search here")

##################
## SECTION: Validate an existing entry
##################
val_col.markdown("### Entry selection" if val_mode else "")
with val_col.expander(
    "Select catalogue entry to validate" if val_mode else "",
    expanded=val_mode,
):
    catalogue = load_catalogue()
    entry_id = st.selectbox(
        label="Select an entry to validate from the existing catalogue",
        options=[k for k in catalogue if "-validated-" not in k],
        format_func=lambda x: f"{x} | {catalogue[x]['description']['name']}",
        index=len(catalogue)-1,
    )
    entry_dict = catalogue[entry_id]
    already_validated_list = glob(pjoin("entries", f"{entry_id}-validated*.json"))
    if len(already_validated_list) > 0:
        st.write("Note: this dataset has already been validated")
    st.markdown(f"##### Validating: {entry_types.get(entry_dict['type'], '')} - {entry_dict['description']['name']}\n\n{entry_dict['description']['description']}")

if val_mode and "languages" in entry_dict:
    val_col.markdown("### Entry Languages and Locations" if val_mode else "")
    with val_col.expander(
        "Language names and represented regions" if val_mode else "",
        expanded=val_mode,
    ):
        language_choices = sorted(set(
            list(language_lists["language_groups"].keys()) + \
            language_lists["niger_congo_languages"] + \
            language_lists["indic_languages"] + \
            list(language_lists["arabic"].keys()) + \
            [", ".join(x["description"]) for x in bcp_47_langs] + \
            entry_dict["languages"]["language_names"]
        )) + ["other"]
        new_lang_list = st.multiselect(
            label="The entry currently has the following list of languages, you can add or remove any here:",
            options=language_choices,
            default=entry_dict["languages"]["language_names"],
        )
        new_lang_comment = st.text_input(
            label="The value currently has the following additional comment on the language(s) covered, you may edit it here",
            value=entry_dict["languages"]["language_comments"],
        )
        region_choices = sorted(set(
            ["World-Wide"] + list(region_tree.keys()) + \
            countries + entry_dict["languages"]["language_locations"]
        )) + ["other"]
        new_region_list = st.multiselect(
            label="The entry currently has the following list of locations for the covered languages, you can add or remove any here:",
            options=region_choices,
            default=entry_dict["languages"]["language_locations"],
        )
        st.markdown("If you are satisfied with the values for the fields above, press the button below to update and validate the **languages** section of the entry")
        if st.checkbox("Validate: languages"):
            entry_dict["languages"]["language_names"] = new_lang_list
            entry_dict["languages"]["language_comments"] = new_lang_comment
            entry_dict["languages"]["language_locations"] = new_region_list
            entry_dict["languages"]["validated"] = True

if val_mode and "custodian" in entry_dict:
    val_col.markdown("### Entry Representative, Owner, or Custodian" if val_mode else "")
    with val_col.expander(
        ("Advocate or organization information" if entry_dict["type"] == "organization" else "Data owner or custodian")
        if val_mode
        else "",
        expanded=val_mode,
    ):
        if entry_dict["type"] == "organization":
            new_custodian_name = entry_dict["description"]["name"]
        else:
             new_custodian_name = st.text_input(
                label="The entry currently records the following name for the data custodian.",
                value=entry_dict["custodian"]["name"]
            )
        custodian_type_choices = [""] + sorted(set(custodian_types + [entry_dict["custodian"]["type"]])) + ["other"]
        new_custodian_type = st.selectbox(
            label="The current category of the data custodian, person, or organization is the following.",
            options=custodian_type_choices,
            index=custodian_type_choices.index(entry_dict["custodian"]["type"])
        )
        if new_custodian_type == "other":
            new_custodian_type = st.text_input(
                label="You entered `other` for the entity type, how would you categorize them?",
            )
        new_custodian_location = st.selectbox(
            label="The entity is recoreded as being located or hosted in:",
            options=countries,
            index=countries.index(entry_dict["custodian"]["location"])
        )
        new_custodian_contact_name = st.text_input(
            label="The following person is recorded as contact for the entity",
            value=entry_dict["custodian"]["contact_name"],
        )
        new_custodian_contact_email = st.text_input(
            label="Their contact email is recorded as:",
            value=entry_dict["custodian"]["contact_email"],
        )
        new_custodian_additional = st.text_input(
            label="The following URL is recorded as a place to find more information about the entity",
            value=entry_dict["custodian"]["additional"]
        )
        st.markdown("If you are satisfied with the values for the fields above, press the button below to update and validate the **custodian** section of the entry")
        if st.checkbox("Validate: custodian"):
            entry_dict["custodian"]["name"] = new_custodian_name
            entry_dict["custodian"]["type"] = new_custodian_type
            entry_dict["custodian"]["location"] = new_custodian_location
            entry_dict["custodian"]["contact_name"] = new_custodian_contact_name
            entry_dict["custodian"]["contact_email"] = new_custodian_contact_email
            entry_dict["custodian"]["additional"] = new_custodian_additional
            entry_dict["custodian"]["validated"] = True

# TODO: add all of the other validation sections

val_display_col.markdown("### Review and Save Entry" if val_mode else "")
if val_mode:
    with val_display_col.expander("Show current entry" if val_mode else "", expanded=val_mode):
        st.markdown("Do not forget to **save your work** to the BigScience Data Catalogue!\n\nOnce you are done, please press the button below - this will either record the entry or tell you if there's anything you need to change first.")
        if st.button("Save validated entry to catalogue"):
            good_to_save, save_message = can_save(entry_dict, submission_info_dict, add_mode)
            if good_to_save:
                validation_info_dict = json.load(open(pjoin("entry_submitted_by", f"{entry_dict['uid']}.json"), encoding="utf-8"))
                validation_info_dict["validated_by"] = submission_info_dict['validated_by']
                validation_info_dict["validated_date"] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                friendly_date = re.sub(r"[^\w\s]", "_", validation_info_dict["validated_date"]).replace(" ", "_")
                json.dump(entry_dict, open(pjoin("entries", f"{entry_dict['uid']}-validated-{friendly_date}.json"), "w", encoding="utf-8"), indent=2)
                json.dump(validation_info_dict, open(pjoin("entry_submitted_by", f"{entry_dict['uid']}-validated-{friendly_date}.json"), "w", encoding="utf-8"), indent=2)
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
