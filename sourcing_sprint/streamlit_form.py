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

### JSON-formatted resources and taxonomies
## Countries and languages
# from Wikipedia and https://unstats.un.org/unsd/methodology/m49/
regions, countries, region_tree = json.load(open("resources/country_regions.json", encoding="utf-8"))
country_centers = json.load(open("resources/country_center_coordinates.json", encoding="utf-8"))
country_mappings = json.load(open("resources/country_mappings.json", encoding="utf-8"))

bcp_47 = json.load(open("resources/bcp47.json", encoding="utf-8"))
bcp_47_langs = [x for x in bcp_47["subtags"] if x["type"] == "language"]

prog_langs = json.load(open("resources/programming_languages.json", encoding="utf-8"))
prog_langs = [x for x in prog_langs["itemListElement"]]

language_lists = json.load(open("resources/language_lists.json", encoding="utf-8"))
MAX_LANGS = 25
MAX_COUNTRIES = 25

# primary source categories
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

# file formats for different modalities
file_formats = json.load(open("resources/file_formats.json", encoding="utf-8"))

## Data accessibility
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
def get_region_center(region_name):
    latitudes = []
    longitudes = []
    for name in region_tree[region_name]:
        if name in region_tree:
            region_latitudes, region_longitudes = get_region_center(name)
            latitudes += region_latitudes
            longitudes += region_longitudes
        elif name in country_centers or name in country_mappings["to_center"]:
            country_center = country_centers[country_mappings["to_center"].get(name, name)]
            latitudes += [float(country_center["latitude"])]
            longitudes += [float(country_center["longitude"])]
    return latitudes, longitudes

@st.cache(allow_output_mutation=True)
def get_region_countries(region_name):
    countries = []
    for name in region_tree[region_name]:
        if name in region_tree:
            countries += get_region_countries(name)
        else:
            countries += [name]
    return countries

@st.cache(allow_output_mutation=True)
def make_choro_map(resource_counts, marker_thres=0):
    world_map = folium.Map(tiles="cartodbpositron", location=[0, 0], zoom_start=1.5)
    marker_cluster = MarkerCluster(icon_create_function=ICON_CREATE_FUNCTIOM)
    marker_cluster.add_to(world_map)
    for name, count in resource_counts.items():
        if name in country_centers or name in country_mappings["to_center"]:
            country_center = country_centers[country_mappings["to_center"].get(name, name)]
            MarkerWithProps(
                location=[country_center["latitude"], country_center["longitude"]],
                popup=f"{'Region' if name in region_tree else 'Country'} : {name}<br> \n Resources : {count} <br>",
                props={"name": name, "resources": count},
            ).add_to(marker_cluster)
        # put a pin at the center of the region
        elif name in region_tree:
            latitudes, longitudes = get_region_center(name)
            if len(latitudes) > 0:
                lat = sum(latitudes) / len(latitudes)
                lon = sum(longitudes) / len(longitudes)
                MarkerWithProps(
                    location=[lat, lon],
                    popup=f"{'Region' if name in region_tree else 'Country'} : {name}<br> \n Resources : {count} <br>",
                    props={"name": name, "resources": count},
                ).add_to(marker_cluster)
    # for choropleth, add counts to all countries in a region
    choropleth_counts = {}
    for loc_name in list(resource_counts.keys()):
        if loc_name in region_tree:
            for country_name in get_region_countries(loc_name):
                choropleth_counts[country_name] = choropleth_counts.get(country_name, 0) + resource_counts[loc_name]
        else:
            choropleth_counts[loc_name] = choropleth_counts.get(loc_name, 0) + resource_counts[loc_name]
    df_resource_counts = pd.DataFrame(
        [(country_mappings["to_outline"].get(n, n), c) for n, c in choropleth_counts.items()],
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
    catalogue_list = [json.load(open(fname, encoding="utf-8")) for fname in glob("entries/*.json") if not "-validated-" in fname]
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

# check whether the entry can be written to the catalogue
def can_save(entry_dct, submission_dct, adding_mode):
    if add_mode and (entry_dct['uid'] == "" or isfile(pjoin("entries", f"{entry_dct['uid']}.json"))):
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
st.sidebar.markdown(page_description, unsafe_allow_html=True)

mode_short_list = ["add", "viz", "val"]
app_mode = st.sidebar.radio(
    label="App mode:",
    options=[
        "Add a new entry",
        "Explore the current catalogue",
        "Validate an existing entry",
    ],
    index=mode_short_list.index(query_params.get("mode", ["add"])[0])
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
with st.sidebar.expander("User information", expanded=add_mode or val_mode):
    user_name = st.text_input(label="Name of submitter:")
    user_email = st.text_input(
        label="Email (optional, enter if you are available to follow up on this catalogue entry):"
    )
    if add_mode:
        submission_info_dict["submitted_by"] = user_name
        submission_info_dict["submitted_email"] = user_email
    else:
        submission_info_dict["validated_by"] = user_name
    st.markdown("[Privacy policy](https://github.com/bigscience-workshop/data_sourcing/wiki/Required-User-Information-and-Privacy-Policy)")

st.markdown("#### BigScience Catalogue of Language Data and Resources")
collapse_all = st.checkbox("Collapse all fields", value=True)
st.markdown("---\n")
# switch between expanded tabs
if add_mode:
    col_sizes = [100, 5, 1, 5, 1]
if viz_mode:
    col_sizes = [5, 100, 1, 5, 1]
if val_mode:
    col_sizes = [5, 5, 1, 100, 1]

form_col, viz_col, _, val_col, _ = st.columns(col_sizes)

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

form_col.markdown("### Entry Category, Name, ID, Homepage, Description" if add_mode else "")
with form_col.expander(
    "General information" if add_mode else "",
    expanded=add_mode and not collapse_all,
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
    expanded=add_mode and not collapse_all,
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
    if "Programming Language" in entry_dict["languages"]["language_names"]:
        entry_dict["languages"]["language_names"] += st.multiselect(
            label="The entry covers programming languages, select any that apply here:",
            options= [x["item"]["name"] for x in prog_langs],
            help="If the language you are looking for is not in the present list, you can add it through the **other languages** form below",
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
    expanded=add_mode and not collapse_all,
):
    st.markdown((entry_organization_text if entry_dict["type"] == "organization" else entry_custodian_text) if add_mode else "")
    if entry_dict["type"] == "organization":
        entry_dict["custodian"]["in_catalogue"] = ""
    else:
        organization_catalogue = dict([(entry['uid'], entry) for entry in load_catalogue().values() if entry["type"] == "organization"])
        organization_keys = [""] + list(organization_catalogue.keys())
        organization_catalogue[""] = {"uid": "", "description": {"name": ""}}
        entry_dict["custodian"]["in_catalogue"] = st.selectbox(
            label="Is the data owned or managed by an organization corresponding to a catalogue entry?",
            options=organization_keys,
            format_func=lambda uid: f"{organization_catalogue[uid]['uid']} | {organization_catalogue[uid]['description']['name']}",
            index=0,
            key="form_in_catalogue"
        )
    if entry_dict["custodian"]["in_catalogue"] == "":
        entry_dict["custodian"]["name"] = st.text_input(
            label="Please enter the name of the person or entity that owns or manages the data (data custodian)",
            value=entry_dict["description"]["name"] if entry_dict["type"] == "organization" else "",
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
        expanded=add_mode and not collapse_all,
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
            entry_dict["availability"]["procurement"]["download_email"] = st.text_input(
                label="Please provide the email of the person to contact to obtain the data",
                value=entry_dict["custodian"]["contact_email"],
                help="if it is different from the contact email entered for the data custodian in the **Data owner or custodian** section above",
            )

    with form_col.expander(
        "Data licenses and Terms of Service" if add_mode else "",
        expanded=add_mode and not collapse_all,
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
        expanded=add_mode and not collapse_all,
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
        expanded=add_mode and not collapse_all,
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
        expanded=add_mode and not collapse_all,
    ):
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
            if entry_dict["processed_from_primary"]["primary_availability"] != "No - the dataset curators kept the source data secret":
                primary_catalogue = dict([(entry['uid'], entry) for entry in load_catalogue().values() if entry["type"] == "primary"])
                primary_keys = list(primary_catalogue.keys())
                entry_dict["processed_from_primary"]["from_primary_entries"] = st.multiselect(
                    label="Please select all primary sources for this dataset that are available in this catalogue",
                    options=primary_keys,
                    format_func=lambda uid: f"{primary_catalogue[uid]['uid']} | {primary_catalogue[uid]['description']['name']}",
                    default=[],
                    key="form_from_primary_entries"
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
        "database_format": [],
        "text_is_transcribed": "",
        "instance_type": "",
        "instance_count": "",
        "instance_size": "",
        "validated": False,
    }
    with form_col.expander(
        "Media type" if add_mode else "",
        expanded=add_mode and not collapse_all,
    ):
        st.write("Please provide information about the language data formats covered in the entry")
        entry_dict["media"]["category"] = st.multiselect(
            label="The language data in the resource is made up of:",
            options=["text", "audiovisual", "image"],
            help="Media data provided with transcription should go into **text**, then select the *transcribed* option. PDFs that have pre-extracted text information should go into **text**, PDFs that need OCR should go into **images**, select the latter if you're unsure",
        )
        if "text" in entry_dict["media"]["category"]:
            text_format_dict = dict(
                [(fmt, desc) for fmt, desc in list(file_formats["Text"].items()) + list(file_formats["Web"].items()) + [("other", "other text file format")]]
            )
            text_format_list = text_format_dict.keys()
            entry_dict["media"]["text_format"] = st.multiselect(
                label="What text formats are present in the entry?",
                options=text_format_list,
                format_func=lambda x: f"{x} | {text_format_dict[x]}",
            )
            if "other" in entry_dict["media"]["text_format"]:
                entry_dict["media"]["text_format"] += [st.text_input(
                    label="You entered `other` for the text format, what format is it?",
                )]
            entry_dict["media"]["text_is_transcribed"] = st.radio(
                label="Was the text transcribed from another media format (e.g. audio or image)",
                options=["Yes - audiovisual", "Yes - image", "No"],
                index=2,
            )
        if "audiovisual" in entry_dict["media"]["category"] or "audiovisual" in entry_dict["media"]["text_is_transcribed"]:
            audiovisual_format_dict = dict(
                [(fmt, desc) for fmt, desc in list(file_formats["Audio"].items()) + list(file_formats["Video"].items()) + [("other", "other audiovisual file format")]]
            )
            audiovisual_format_list = audiovisual_format_dict.keys()
            entry_dict["media"]["audiovisual_format"] = st.multiselect(
                label="What format or formats do the audiovisual data come in?",
                options=audiovisual_format_list,
                format_func=lambda x: f"{x} | {audiovisual_format_dict[x]}",
            )
            if "other" in entry_dict["media"]["audiovisual_format"]:
                entry_dict["media"]["audiovisual_format"] += [st.text_input(
                    label="You entered `other` for the audiovisual format, what format is it?",
                )]
        if "image" in entry_dict["media"]["category"] or "image" in entry_dict["media"]["text_is_transcribed"]:
            image_format_dict = dict(
                [(fmt, desc) for fmt, desc in list(file_formats["Image"].items()) + [("other", "other image file format")]]
            )
            image_format_list = image_format_dict.keys()
            entry_dict["media"]["image_format"] = st.multiselect(
                label="What format or formats do the image data come in?",
                options=image_format_list,
                format_func=lambda x: f"{x} | {image_format_dict[x]}",
            )
            if "other" in entry_dict["media"]["image_format"]:
                entry_dict["media"]["image_format"] += [st.text_input(
                    label="You entered `other` for the image format, what format is it?",
                )]
        db_format_dict = dict(
            [(fmt, desc)
             for fmt, desc in list(file_formats["Data"].items()) + \
                list(file_formats["Database"].items()) + \
                list(file_formats["Compressed"].items()) + \
                [("other", "other database file format")]]
        )
        db_format_list = db_format_dict.keys()
        entry_dict["media"]["database_format"] = st.multiselect(
            label="If the data is presented as a database or compressed archive, please select all formats that apply here:",
            options=db_format_list,
            format_func=lambda x: f"{x} | {db_format_dict[x]}",
        )
        if "other" in entry_dict["media"]["database_format"]:
            entry_dict["media"]["database_format"] += [st.text_input(
                label="You entered `other` for the database format, what format is it?",
            )]


    with form_col.expander(
        "Media amounts" if add_mode else "",
        expanded=add_mode and not collapse_all,
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
form_col.markdown("### Review and Save Entry" if add_mode else "")
if add_mode:
    with form_col.expander("Show current entry" if add_mode else "", expanded=add_mode):
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
with viz_col.expander("Select resources to visualize" if viz_mode else "", expanded=viz_mode and not collapse_all):
    if viz_mode:
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
            options=entry_types,
            format_func=lambda x: entry_types[x],
        )
        filter_dict["languages"]["language_names"] = st.multiselect(
            label="I want to only see entries that have one of the following languages:",
            options=list(language_lists["language_groups"].keys()) + \
                language_lists["niger_congo_languages"] + \
                language_lists["indic_languages"],
        )
        filter_dict["custodian"]["type"] = st.multiselect(
            label="I want to only see entries that corresponds to organizations or to data that id owned/managed by organizations of the following types:",
            options=custodian_types,
        )
        full_catalogue = load_catalogue()
        filtered_catalogue = [entry for uid, entry in full_catalogue.items() if filter_entry(entry, filter_dict) and not (uid == "")]
        st.write(f"Your query matched {len(filtered_catalogue)} entries in the current catalogue.")
        entry_location_type = st.radio(
            label="I want to visualize",
            options=[
                "Where the language data creators are located",
                "Where the organizations or data custodians are located",
            ],
        )
        show_by_org = entry_location_type == "Where the organizations or data custodians are located"
    else:
        filtered_catalogue = []

with viz_col.expander("Map of entries" if viz_mode else "", expanded=viz_mode):
    if viz_mode:
        filtered_counts = {}
        for entry in filtered_catalogue:
            locations = [entry["custodian"]["location"]] if show_by_org else entry["languages"]["language_locations"]
            # be as specific as possible
            locations = [loc for loc in locations if not any([l in region_tree.get(loc, []) for l in locations])]
            for loc in locations:
                filtered_counts[loc] = filtered_counts.get(loc, 0) + 1
        world_map = make_choro_map(filtered_counts)
        folium_static(world_map, width=1150, height=600)

with viz_col.expander("View selected resources" if viz_mode else "", expanded=viz_mode and not collapse_all):
    if viz_mode:
        st.write("You can further select locations to select entries from here:")
        filter_region_choices = sorted(set(
            [loc for entry in filtered_catalogue for loc in ([entry["custodian"]["location"]] if show_by_org else entry["languages"]["language_locations"])]
        ))
        filter_locs = st.multiselect(
            "View entries from the following locations:",
            options=filter_region_choices
        )
        filter_loc_dict = {"custodian": {"location": filter_locs}} if show_by_org else {"languages": {"language_locations": filter_locs}}
        filtered_catalogue_by_loc = [
            entry for entry in filtered_catalogue if filter_entry(entry, filter_loc_dict)
        ]
        view_entry = st.selectbox(
            label="Select an entry to see more detail:",
            options=filtered_catalogue_by_loc,
            format_func=lambda entry: f"{entry['uid']} | {entry['description']['name']} -- {entry['description']['description']}"
        )
        st.markdown(f"##### *Type:* {view_entry['type']} *UID:* {view_entry['uid']} - *Name:* {view_entry['description']['name']}\n\n{view_entry['description']['description']}")

##################
## SECTION: Validate an existing entry
##################
val_col.markdown("### Entry selection" if val_mode else "")
with val_col.expander(
    "Select catalogue entry to validate" if val_mode else "",
    expanded=val_mode and not collapse_all,
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
        st.markdown("##### Note: this dataset has already been validated!")
        fname = st.selectbox(
            label="would you like to load a validated file for this entry?",
            options=[pjoin("entries", f"{entry_id}.json")] + already_validated_list,
        )
        entry_dict = json.load(open(fname, encoding="utf-8"))
    st.markdown(f"##### Validating: {entry_types.get(entry_dict['type'], '')} - {entry_dict['description']['name']}\n\n{entry_dict['description']['description']}")

if "languages" in entry_dict:
    val_col.markdown("### Entry Languages and Locations" if val_mode else "")
    with val_col.expander(
        "Validate language names and represented regions" if val_mode else "",
        expanded=val_mode and not collapse_all,
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
        st.markdown("If you are satisfied with the values for the fields above, press the button below to update and validate the **languages** section of the entry" if val_mode else "")
        if st.checkbox("Validate: languages"):
            entry_dict["languages"]["language_names"] = new_lang_list
            entry_dict["languages"]["language_comments"] = new_lang_comment
            entry_dict["languages"]["language_locations"] = new_region_list
            entry_dict["languages"]["validated"] = True

if "custodian" in entry_dict:
    val_col.markdown("### Entry Representative, Owner, or Custodian" if val_mode else "")
    with val_col.expander(
        ("Validate advocate or organization information" if entry_dict["type"] == "organization" else "Validate data owner or custodian")
        if val_mode
        else "",
        expanded=val_mode and not collapse_all,
    ):
        if entry_dict["type"] == "organization":
            new_in_catalogue = ""
        else:
            organization_catalogue = dict([(entry['uid'], entry) for entry in load_catalogue().values() if entry["type"] == "organization"])
            organization_keys = [""] + list(organization_catalogue.keys())
            organization_catalogue[""] = {"uid": "", "description": {"name": ""}}
            new_in_catalogue = st.selectbox(
                label="Is the data owned or managed by the following organization corresponding to a catalogue entry?",
                options=organization_keys,
                format_func=lambda uid: f"{organization_catalogue[uid]['uid']} | {organization_catalogue[uid]['description']['name']}",
                index=organization_keys.index(entry_dict["custodian"].get("in_catalogue", "")),
                key="validate_in_catalogue"
            )
        if new_in_catalogue == "":
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
        else:
            new_custodian_name = ""
            new_custodian_type = ""
            new_custodian_location = ""
            new_custodian_contact_name = ""
            new_custodian_contact_email = ""
            new_custodian_additional = ""
        st.markdown("If you are satisfied with the values for the fields above, press the button below to update and validate the **custodian** section of the entry" if val_mode else "")
        if st.checkbox("Validate: custodian"):
            entry_dict["custodian"]["name"] = new_custodian_name
            entry_dict["custodian"]["type"] = new_custodian_type
            entry_dict["custodian"]["location"] = new_custodian_location
            entry_dict["custodian"]["contact_name"] = new_custodian_contact_name
            entry_dict["custodian"]["contact_email"] = new_custodian_contact_email
            entry_dict["custodian"]["additional"] = new_custodian_additional
            entry_dict["custodian"]["validated"] = True

if "availability" in entry_dict:
    if entry_dict["type"] in ["primary", "processed"]:
        val_col.markdown("### Availability of the Resource: Procuring, Licenses, PII" if val_mode else "")
        with val_col.expander(
            "Validate Procuring, Licenses, and PII" if val_mode else "",
            expanded=val_mode and not collapse_all,
        ):
            download_options = [
                "Yes - it has a direct download link or links",
                "Yes - after signing a user agreement",
                "No - but the current owners/custodians have contact information for data queries",
                "No - we would need to spontaneously reach out to the current owners/custodians",
            ]
            new_for_download = st.radio(
                label="Can the data be obtained online?",
                options=download_options,
                index=download_options.index(entry_dict["availability"]["procurement"]["for_download"]),
                key="validate_for_download"
            )
            if "Yes -" in entry_dict["availability"]["procurement"]["for_download"]:
                new_download_email = ""
                new_download_url = st.text_input(
                    label="Please provide the URL where the data can be downloaded",
                    value=entry_dict["availability"]["procurement"]["download_url"],
                    key="validate_download_url"
                )
            else:
                new_download_url = ""
                new_download_email = st.text_input(
                    label="Please provide the email of the person to contact to obtain the data",
                    value=entry_dict["availability"]["procurement"]["download_email"],
                    key="validate_download_email",
                )
            has_licenses_options = ["Yes", "No", "Unclear"]
            new_has_licenses = st.radio(
                label="Does the language data in the resource come with explicit licenses of terms of use?",
                options=has_licenses_options,
                index=has_licenses_options.index(entry_dict["availability"]["licensing"]["has_licenses"]),
                key="validate_has_licenses",
            )
            if new_has_licenses == "Yes":
                new_license_properties = st.multiselect(
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
                    default=entry_dict["availability"]["licensing"]["license_properties"],
                    key="validate_license_properties",
                )
                new_license_list = st.multiselect(
                    label=f"Under which licenses is the data shared?",
                    options=licenses,
                    default=entry_dict["availability"]["licensing"]["license_list"],
                    key="validate_license_list"
                )
                new_license_text = st.text_area(
                    label=f"If the resource has explicit terms of use or license text, please copy it in the following area",
                    value=entry_dict["availability"]["licensing"]["license_text"],
                    key="validate_license_text_explicit",
                )
            else:
                new_license_properties = []
                new_license_list = []
                new_license_text = st.text_area(
                    label="Please provide your best assessment of whether the data can be used to train models while respecting the rights and wishes of the data creators and custodians. This field will serve as a starting point for further investigation.",
                    value=entry_dict["availability"]["licensing"]["license_text"],
                    key="validate_license_text_other",
                )
            new_has_pii = st.radio(
                label="Does the language data in the resource contain personally identifiable or sensitive information?",
                help="See the guide for descriptions and examples. The default answer should be 'Yes'. Answers of 'No' and 'Unclear' require justifications.",
                options=["Yes", "Yes - text author name only", "No", "Unclear"],
                index=["Yes", "Yes - text author name only", "No", "Unclear"].index(entry_dict["availability"]["pii"]["has_pii"]),
                key="validate_has_pii"
            )
            new_generic_pii_likely = ""
            new_numeric_pii_likely = ""
            new_sensitive_pii_likely = ""
            new_generic_pii_list = []
            new_numeric_pii_list = []
            new_sensitive_pii_list = []
            new_no_pii_justification_class = ""
            new_no_pii_justification_text = ""
            if new_has_pii == "Yes":
                new_generic_pii_likely = st.selectbox(
                    label="How likely is the data to contain instances of generic PII, such as names or addresses?",
                    options=["", "very likely", "somewhat likely", "unlikely", "none"],
                    index=["", "very likely", "somewhat likely", "unlikely", "none"].index(entry_dict["availability"]["pii"]["generic_pii_likely"]),
                    key="validate_generic_pii_likely"
                )
                if "likely" in new_generic_pii_likely:
                    new_generic_pii_list = st.multiselect(
                        label=f"What type of generic PII (e.g. names, emails, etc,) is the data most likely to contain?",
                        options=pii_categories["generic"],
                        default=entry_dict["availability"]["pii"]["generic_pii_list"],
                        key="validate_generic_pii_list"
                    )
                new_numeric_pii_likely = st.selectbox(
                    label="How likely is the data to contain instances of numeric PII, such as phone or social security numbers?",
                    options=["", "very likely", "somewhat likely", "unlikely", "none"],
                    index=["", "very likely", "somewhat likely", "unlikely", "none"].index(entry_dict["availability"]["pii"]["numeric_pii_likely"]),
                    key="validate_numeric_pii_likely"
                )
                if "likely" in new_numeric_pii_likely:
                    new_numeric_pii_list = st.multiselect(
                        label=f"What type of numeric PII (e.g. phone numbers, health ID numbers, etc,) is the data most likely to contain?",
                        options=pii_categories["numbers"],
                        default=entry_dict["availability"]["pii"]["numeric_pii_list"],
                        key="validate_numeric_pii_list"
                    )
                new_sensitive_pii_likely = st.selectbox(
                    label="How likely is the data to contain instances of numeric PII, such as phone or social security numbers?",
                    options=["", "very likely", "somewhat likely", "unlikely", "none"],
                    index=["", "very likely", "somewhat likely", "unlikely", "none"].index(entry_dict["availability"]["pii"]["sensitive_pii_likely"]),
                    key="validate_sensitive_pii_likely"
                )
                if "likely" in new_sensitive_pii_likely:
                    new_sensitive_pii_list = st.multiselect(
                        label=f"What type of sensitive PII (e.g. health status, poilitcal opinions, sexual orientation, etc.) is the data most likely to contain?",
                        options=pii_categories["sensitive"],
                        default=entry_dict["availability"]["pii"]["sensitive_pii_list"],
                        key="validate_sensitive_pii_list"
                    )
            else:
                no_pii_justification_class_options = [
                    "general knowledge not written by or referring to private persons",
                    "fictional text",
                    "other",
                ]
                new_no_pii_justification_class = st.radio(
                    label="What is the justification for assuming that this resource does not contain any personally identifiable information?",
                    options=no_pii_justification_class_options,
                    index=no_pii_justification_class_options.index(entry_dict["availability"]["pii"]["no_pii_justification_class"]),
                    key="validate_no_pii_justification_class"
                )
                if new_no_pii_justification_class == "other":
                    new_no_pii_justification_text = st.text_area(
                        label=f"If there is another reason for this resource not containing PII, please state why in the textbox below.",
                        value=entry_dict["availability"]["pii"]["no_pii_justification_text"],
                        key="validate_no_pii_justification_text",
                    )
            if st.checkbox("Validate: availability"):
                entry_dict["availability"] = {
                        "procurement": {
                            "for_download": new_for_download,
                            "download_url": new_download_url,
                            "download_email": new_download_email,
                        },
                        "licensing": {
                            "has_licenses": new_has_licenses,
                            "license_text": new_license_text,
                            "license_properties": new_license_properties,
                            "license_list": new_license_list,
                        },
                        "pii": {
                            "has_pii": new_has_pii,
                            "generic_pii_likely": new_generic_pii_likely,
                            "generic_pii_list": new_generic_pii_list,
                            "numeric_pii_likely": new_numeric_pii_likely,
                            "numeric_pii_list": new_numeric_pii_list,
                            "sensitive_pii_likely": new_sensitive_pii_likely,
                            "sensitive_pii_list": new_sensitive_pii_list,
                            "no_pii_justification_class": new_no_pii_justification_class,
                            "no_pii_justification_text": new_no_pii_justification_text,
                        },
                        "validated": True,
                    }

if "source_category" in entry_dict and entry_dict["type"] == "primary":
    val_col.markdown("### Primary Source Type" if val_mode else "")
    with val_col.expander(
        "Validate source category" if val_mode else "",
        expanded=val_mode and not collapse_all,
    ):
        source_type_list = [""] + ["collection", "website", "other"]
        if entry_dict["source_category"]["category_type"] not in source_type_list:
            source_type_list = source_type_list + [entry_dict["source_category"]["category_type"]]
        primary_tax_top = st.selectbox(
            label="Is the resource best described as a:",
            options=source_type_list,
            index=source_type_list.index(entry_dict["source_category"]["category_type"]),
            key="validate_category_type",
        )
        if primary_tax_top == "website":
            source_web_list = [""] + primary_taxonomy["website"]
            if entry_dict["source_category"]["category_web"] not in source_web_list:
                source_web_list = source_web_list + [entry_dict["source_category"]["category_web"]]
            primary_tax_web = st.selectbox(
                label="What kind of website?",
                options=source_web_list,
                index=source_web_list.index(entry_dict["source_category"]["category_web"]),
                key="validate_category_web",
            )
        else:
            primary_tax_web = ""
        if primary_tax_top == "collection" or "collection" in primary_tax_web:
            source_media_list = [""] + primary_taxonomy["collection"]
            if entry_dict["source_category"]["category_media"] not in source_media_list:
                source_media_list = source_media_list + [entry_dict["source_category"]["category_media"]]
            primary_tax_col = st.selectbox(
                label="What kind of collection?",
                options=source_media_list,
                index=source_media_list.index(entry_dict["source_category"]["category_media"]),
                key="validate_source_media",
            )
        else:
            primary_tax_col = ""
        if st.checkbox("Validate: source category"):
            entry_dict["source_category"]["category_type"] = primary_tax_top
            entry_dict["source_category"]["category_web"] = primary_tax_web
            entry_dict["source_category"]["category_media"] = primary_tax_col
            entry_dict["source_category"]["validated"] = True

if "processed_from_primary" in entry_dict and entry_dict["type"] == "processed":
    val_col.markdown("### Primary Sources of the Processed Dataset" if val_mode else "")
    with val_col.expander(
        "Validate list of primary sources" if val_mode else "",
        expanded=val_mode and not collapse_all,
    ):
        new_processed_from_primary = {}
        new_processed_from_primary["from_primary"] = st.radio(
            label="Was the language data in the dataset produced at the time of the dataset creation or was it taken from a primary source?",
            options=["Original data", "Taken from primary source"],
            index=["Original data", "Taken from primary source"].index(entry_dict["processed_from_primary"]["from_primary"]),
            key="validate_from_primary",
        )
        if new_processed_from_primary["from_primary"] == "Taken from primary source":
            primary_vailability_list = [
                "Yes - they are fully available",
                "Yes - their documentation/homepage/description is available",
                "No - the dataset curators describe the primary sources but they are fully private",
                "No - the dataset curators kept the source data secret",
            ]
            new_processed_from_primary["primary_availability"] = st.radio(
                label="Are the primary sources supporting the dataset available to investigate?",
                options=primary_vailability_list,
                index=primary_vailability_list.index(entry_dict["processed_from_primary"]["primary_availability"]),
                key="validate_primary_availability",
            )
            if new_processed_from_primary["primary_availability"] != "No - the dataset curators kept the source data secret":
                primary_catalogue = dict([(entry['uid'], entry) for entry in load_catalogue().values() if entry["type"] == "primary"])
                primary_keys = list(primary_catalogue.keys())
                new_processed_from_primary["from_primary_entries"] = st.multiselect(
                    label="Please select all primary sources for this dataset that are available in this catalogue",
                    options=primary_keys,
                    format_func=lambda uid: f"{primary_catalogue[uid]['uid']} | {primary_catalogue[uid]['description']['name']}",
                    default=entry_dict["processed_from_primary"].get("from_primary_entries", []),
                    key="validate_from_primary_entries"
                )
            if "Yes" in new_processed_from_primary["primary_availability"]:
                primary_types_list = [f"web | {w}" for w in primary_taxonomy["website"]] + primary_taxonomy["collection"]
                new_processed_from_primary["primary_types"] = st.multiselect(
                    label="What kind of primary sources did the data curators use to make this dataset?",
                    options=primary_types_list,
                    default=entry_dict["processed_from_primary"]["primary_types"],
                    key="validate_primary_types",
                )
                primary_license_list = [
                    "Yes - the source material has an open license that allows re-use",
                    "Yes - the dataset has the same license as the source material",
                    "Yes - the dataset curators have obtained consent from the source material owners",
                    "Unclear / I don't know",
                    "No - the license of the source material actually prohibits re-use in this manner",
                ]
                new_processed_from_primary["primary_license"] = st.radio(
                    label="Is the license or commercial status of the source material compatible with the license of the dataset?",
                    options=primary_license_list,
                    index=primary_license_list.index(entry_dict["processed_from_primary"]["primary_license"]),
                    key="validate_primary_license",
                )
        if st.checkbox("Validate: primary sources of dataset"):
            new_processed_from_primary["validated"] = True
            entry_dict["processed_from_primary"] = new_processed_from_primary

if "media" in entry_dict and entry_dict["type"] in ["primary", "processed"]:
    val_col.markdown("### Media type, format, size, and processing needs" if val_mode else "")
    new_media = {}
    with val_col.expander(
        "Validate media type" if val_mode else "",
        expanded=val_mode and not collapse_all,
    ):
        new_media["category"] = st.multiselect(
            label="The language data in the resource is made up of:",
            options=["text", "audiovisual", "image"],
            default=entry_dict["media"]["category"],
            key="validate_media_type"
        )
        if "text" in new_media["category"]:
            text_format_dict = dict(
                [(fmt, desc) for fmt, desc in list(file_formats["Text"].items()) + list(file_formats["Web"].items()) + [("other", "other text file format")]]
            )
            for frm in entry_dict["media"]["text_format"]:
                text_format_dict[frm] = text_format_dict.get(frm, frm)
            text_format_list = text_format_dict.keys()
            new_media["text_format"] = st.multiselect(
                label="What text formats are present in the entry?",
                options=text_format_list,
                default=entry_dict["media"]["text_format"],
                format_func=lambda x: f"{x} | {text_format_dict[x]}",
                key="validate_text_format",
            )
            new_media["text_is_transcribed"] = st.radio(
                label="Was the text transcribed from another media format (e.g. audio or image)",
                options=["Yes - audiovisual", "Yes - image", "No"],
                index=["Yes - audiovisual", "Yes - image", "No"].index(entry_dict["media"]["text_is_transcribed"]),
                key="validate_text_is_transcribed",
            )
        if "audiovisual" in new_media["category"] or "audiovisual" in new_media["text_is_transcribed"]:
            audiovisual_format_dict = dict(
                [(fmt, desc) for fmt, desc in list(file_formats["Audio"].items()) + list(file_formats["Video"].items()) + [("other", "other audiovisual file format")]]
            )
            for frm in entry_dict["media"]["audiovisual_format"]:
                audiovisual_format_dict[frm] = audiovisual_format_dict.get(frm, frm)
            audiovisual_format_list = audiovisual_format_dict.keys()
            new_media["audiovisual_format"] = st.multiselect(
                label="What format or formats do the audiovisual data come in?",
                options=audiovisual_format_list,
                default=entry_dict["media"]["audiovisual_format"],
                format_func=lambda x: f"{x} | {audiovisual_format_dict[x]}",
                key="validate_audiovisual_format",
            )
        if "image" in new_media["category"] or "image" in new_media["text_is_transcribed"]:
            image_format_dict = dict(
                [(fmt, desc) for fmt, desc in list(file_formats["Image"].items()) + [("other", "other image file format")]]
            )
            for frm in entry_dict["media"]["image_format"]:
                image_format_dict[frm] = image_format_dict.get(frm, frm)
            image_format_list = image_format_dict.keys()
            new_media["image_format"] = st.multiselect(
                label="What format or formats do the image data come in?",
                options=image_format_list,
                default=entry_dict["media"]["image_format"],
                format_func=lambda x: f"{x} | {image_format_dict[x]}",
                key="validate_image_format"
            )
        db_format_dict = dict(
            [(fmt, desc)
             for fmt, desc in list(file_formats["Data"].items()) + \
                list(file_formats["Database"].items()) + \
                list(file_formats["Compressed"].items()) + \
                [("other", "other database file format")]]
        )
        for frm in entry_dict["media"].get("database_format", []):
            db_format_dict[frm] = db_format_dict.get(frm, frm)
        db_format_list = db_format_dict.keys()
        new_media["database_format"] = st.multiselect(
            label="If the data is presented as a database or compressed archive, please select all formats that apply here:",
            options=db_format_list,
            default=entry_dict["media"].get("database_format", []),
            format_func=lambda x: f"{x} | {db_format_dict[x]}",
            key="validate_database_format"
        )
        # validate media amounts
        instance_type_list = ["", "article", "post", "dialogue", "episode", "book"]
        if entry_dict["media"]["instance_type"] not in instance_type_list:
            instance_type_list = instance_type_list + [entry_dict["media"]["instance_type"]]
        instance_type_list = instance_type_list + ["other"]
        new_media["instance_type"] = st.selectbox(
            label="What does a single instance of language data consist of in this dataset/primary source?",
            options=instance_type_list,
            index=instance_type_list.index(entry_dict["media"]["instance_type"]),
            key="validate_instance_list",
        )
        new_media["instance_count"] = st.selectbox(
            label="Please estimate the number of instances in the dataset",
            options=["", "n<100", "100<n<1K", "1K<n<10K", "10K<n<100K", "100K<n<1M", "1M<n<1B", "n>1B"],
            index=["", "n<100", "100<n<1K", "1K<n<10K", "10K<n<100K", "100K<n<1M", "1M<n<1B", "n>1B"].index(entry_dict["media"]["instance_count"]),
            key="validate_instance_count",
        )
        new_media["instance_size"] = st.selectbox(
            label="How long do you expect each instance to be on average interms of number of words?",
            options=["", "n<10", "10<n<100", "100<n<10,000", "n>10,000"],
            index=["", "n<10", "10<n<100", "100<n<10,000", "n>10,000"].index(entry_dict["media"]["instance_size"]),
            key="validate_instance_size"
        )
        if st.checkbox("Validate: media type and counts"):
            new_media["validated"] = True
            entry_dict["media"] = new_media

val_col.markdown("### Review and Save Entry" if val_mode else "")
if val_mode:
    with val_col.expander("Show current entry" if val_mode else "", expanded=val_mode):
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
        st.markdown(f"You are validating a resource of type: *{entry_dict['type']}*")
        st.write(entry_dict)
        st.markdown("You can also download the entry as a `json` file with the following button:")
        st.download_button(
            label="Download entry dictionary",
            data=json.dumps(entry_dict, indent=2),
            file_name="default_entry_name.json" if entry_dict["uid"] == "" else f"{entry_dict['uid']}.json",
        )
