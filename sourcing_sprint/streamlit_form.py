import folium
import json
import pandas as pd
import re
import streamlit as st

from folium import Marker
from folium.plugins import MarkerCluster
from jinja2 import Template
from streamlit_folium import folium_static

##################
## resources
##################

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

# from Data Tooling docs
pii_categories = json.load(open("resources/pii_categories.json", encoding="utf-8"))
MAX_PII = 25

licenses = json.load(open("resources/licenses.json", encoding="utf-8"))
MAX_LICENSES = 25

##################
## Mapping functions
##################
WORLD_GEO_URL = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json"

ICON_CREATE_FUNCTIOM = '''
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
'''

class MarkerWithProps(Marker):
    _template = Template(u"""
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
        """)
    def __init__(self, location, popup=None, tooltip=None, icon=None,
                 draggable=False, props = None):
        super(MarkerWithProps, self).__init__(location=location,popup=popup,tooltip=tooltip,icon=icon,draggable=draggable)
        self.props = json.loads(json.dumps(props))

@st.cache(allow_output_mutation=True)
def make_choro_map(resource_counts, marker_thres=0):
    world_map = folium.Map(tiles="cartodbpositron", location=[0,0], zoom_start=1.5)
    marker_cluster = MarkerCluster(icon_create_function=ICON_CREATE_FUNCTIOM)
    marker_cluster.add_to(world_map)
    for name, count in resource_counts.items():
        if count > marker_thres and name in country_centers or name in country_mappings["to_center"]:
            country_center = country_centers[country_mappings["to_center"].get(name, name)]
            MarkerWithProps(
                location = [
                    country_center["latitude"], country_center["longitude"]],
                popup = f"Country : {name}<br> \n Resources : {count} <br>",
                props = {'name': name, 'resources': count},
            ).add_to(marker_cluster)
    df_resource_counts = pd.DataFrame(
        [(country_mappings["to_outline"].get(n, n), c) for n, c in resource_counts.items()],
        columns=["Name", "Resources"],
    )
    folium.Choropleth(
        geo_data = WORLD_GEO_URL,
        name="resource map",
        data=df_resource_counts,
        columns=["Name", "Resources"],
        key_on="feature.properties.name",
        fill_color='PuRd',
        nan_fill_color='white',
    ).add_to(world_map)
    return world_map

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
# Adding a new resource

This form can be used to add a new entry to the BigScience Data Sourcing Catalogue.

To do so, please add your name, email (optional), the type of resource you would like to add,
then fill out the form on the right.

For more information: [**guide to adding a new catalogue entry.**](https://github.com/bigscience-workshop/data_sourcing/blob/master/sourcing_sprint/guide.md#guide-to-submitting-sources-to-the-bigscience-data-sourcing-hackathon)

### Submitter information
"""
st.sidebar.markdown(page_description, unsafe_allow_html=True)

with st.sidebar.form("submitter_information"):
    submitter_name = st.text_input(label="Name of submitter:")
    submitter_email = st.text_input(
        label="Email (optional, enter if you are available to follow up on this catalogue entry):"
    )
    submitted_info = st.form_submit_button("Submit self information")

st.markdown("#### What would you like to use this app for?")
add_col, viz_col, val_col = st.columns([1, 1, 1])
add_mode_button = add_col.button("Add a new entry")
viz_mode = viz_col.button("Explore the current catalogue")
val_mode = val_col.button("Validate an existing entry")
add_mode = add_mode_button or not (val_mode or viz_mode)
if add_mode:
    col_sizes = [60, 40, 5, 1, 5, 1]
if viz_mode:
    col_sizes = [5, 1, 100, 1, 5, 1]
if val_mode:
    col_sizes = [5, 1, 5, 1, 100, 1]

st.markdown("---\n")

form_col, display_col, viz_col, _, val_col, _ = st.columns(col_sizes)

if add_mode:
    form_col.markdown("### Entry Category, Name, ID, Homepage, Description")

resource_type_help = """
You may choose one of the following three resource types:
- *Primary source*: a single source of language data (text or speech), such as a newspaper, radio, website, book collection, etc.
You will be asked to fill in information about the availability of the source, its properties including availability and presence of personal information,
its owners or producers, and the format of the language data.
- *Processed dataset*: a processed NLP dataset containing language data that can be used for language modeling (most items should be at least a few sentences long).
You will be asked to fill in information about the dataset object itself as well as the primary sources it was derived from
(e.g. Wikipedia, or news sites for most summarization datasets).
- *Partner organization*: an organization holding a set of resources and datasets of various types, formats, languages and/or with various degrees of availability.
You will be asked to fill in information about the partner organization itself as well as information on how to get in contact with them.
(e.g. The Internet Archive, The British Library, l'institut national de l'audiovisuel, Wikimedia Foundation, or other libraries, archival institutions, cultural organizations).
"""

entry_dict = {
    "uid": "", # Unique Identifier string to link information and refer to the entry
    "type": "", # in ["Primary source", "Language dataset", "Language organization"]
    "description": {
        "name": "",
        "description": "",
        "homepage": "",  # optional
        "validated": True, # no need to have a second person validate this part
    },
    "languages": {
        "language_names": [],
        "language_locations_region": [],
        "language_locations_nation": [],
        "validated": False,
    },
    "custodian": { # for Primary source or Language daset - data owner or custodian
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

entry_types = {
    "primary": "Primary source",
    "processed": "Processed language dataset",
    "organization": "Language advocate or organization",
}
with form_col.expander(
    "General information" if add_mode else "",
    expanded = add_mode,
):
    st.markdown("##### Entry name and summary") # TODO add collapsible instructions
    entry_dict["type"] = st.radio(
        label="What resource type are you submitting?",
        options=entry_types,
        format_func=lambda x:entry_types[x],
        help=resource_type_help,
    )
    entry_dict["description"]["name"] = st.text_input(
        label=f"Provide a descriptive name for the resource",
        help="This should be a human-readable name such as e.g. **Le Monde newspaper** (primary source), **EXAMS QA dataset** (processed dataset), or **Creative Commons** (partner organization)",
    )
    entry_dict["uid"] = st.text_input(
        label=f"Provide a short `snake_case` unique identifier for the resource",
        value= re.sub(r'[^\w\s]', '_', entry_dict["description"]["name"].lower()).replace(" ", "_"),
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
    expanded = add_mode,
):
    language_help_text = """
    ##### Whose language is represented in the entry?
    For each entry, we need to catalogue which languages are represented or focused on,
    as charcterized by the language names and the location of the language data creators.
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
            options=language_lists["niger_congo_languages"],
            help="If the language you are looking for is not in the present list, you can add it through the **other languages** form below",
        )
    entry_dict["languages"]["language_names"] = st.multiselect(
        label="For entries that cover languages outside of the current BigScience list, select all that apply here:",
        options=[', '.join(x['description']) for x in bcp_47_langs],
        help="This is a comprehensive list of languages obtained from the BCP-47 standard list, please select one using the search function",
    )
    st.markdown(
        "In addition to the names of the languages covered by the entry, we need to know where the language creators are **primarily** located.\n" + \
        "This information can be entered both at the level of a *cacroscopic world region* or at the level of the *country or nation*, please select all that apply."
    )
    entry_dict["languages"]["language_locations_region"] = st.multiselect(
        label="Macroscopic regions. Please select all that apply from the following",
        options=["World-Wide"] + list(region_tree.keys()),
        format_func=lambda x: f"{x}: {', '.join(region_tree.get(x, []))}",
    )
    entry_dict["languages"]["language_locations_nation"] += st.multiselect(
        label="Countries and nations. Please all that apply from the following",
        options=countries + ["other"],
    )


form_col.markdown("### Entry Representative, Owner, or Custodian" if add_mode else "")
with form_col.expander(
    ("Advocate or organization information" if entry_dict["type"] == "organization" else "Data owner or custodian") if add_mode else "",
    expanded = add_mode,
):
        st.markdown("#### Information about the entry's custodian or representative")
        if entry_dict["type"] == "organization":
            entry_dict["custodian"]["name"] = entry_dict["description"]["name"]
        else:
            entry_dict["custodian"]["name"] = st.text_input(
                label="Please enter the name of the person or entity that owns or manages the data (data custodian)",
            )
        entry_dict["custodian"]["type"] = st.selectbox(
            label="Entity type: is the organization, advocate, or data custodian...",
            options=[
                "",
                "A private individual",
                "A commercial entity",
                "A library, museum, or archival institute",
                "A university or research institution",
                "A nonprofit/NGO (other)",
                "A government organization",
                "Unclear",
                "other",
            ],
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
            label="Would you be willing to reach out to the entity to ask them about using their data (with support from the BigScience data sourcing team)?" + \
            " If so, make sure to fill out your email in the sidebar.",
        )
        entry_dict["custodian"]["additional"] = st.text_input(
            label="Where can we find more information about the data owner/custodian? Please provide a URL",
            help="For example, please provide the URL of the web page with their contact information, the homepage of the organization, or even their Wikipedia page if it exists."
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
            "license_list": [],
        },
        "pii": {
            "has_pii": "",
            "general_pii_list": [],
            "numeric_pii_list": [],
            "sensitive_pii_list": [],
            "no_pii_justification_class": "",
            "no_pii_justification_text": "",
        },
        "validated": False,
    }
    with form_col.expander(
        "Obtaining the data: online availability and data owner/custodian" if add_mode else "",
        expanded = add_mode,
    ):
        st.markdown("##### Availability for download")
        entry_dict["availability"]["procurement"]["for_download"] = st.radio(
            label="Can the data be obtained online?",
            options=[
                "Yes - it has a direct download link or links",
                "Yes - after signing a user agreement",
                "No - but the current owners/custodians have contact information for data queries",
                "No - we would need to spontaneously reach out to the current owners/custodians"
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
        expanded = add_mode,
    ):
        st.write("Please provide as much information as you can find about the data's licensing and terms of use:")
        entry_dict["availability"]["licensing"]["has_licenses"] = st.radio(
            label="Does the language data in the resource come with explicit licenses of terms of use?",
            options=["Yes", "No", "Unclear"],
        )
        if entry_dict["availability"]["licensing"]["has_licenses"] == "Yes":
            entry_dict["availability"]["licensing"]["license_text"] = st.text_area(
                label=f"If the resource has explicit terms of use or license text, please copy it in the following area",
                help="The text may be included in a link to the license webpage. You do not neet to copy the text if it corresponds to one of the established licenses that may be selected below.",
            )
            st.markdown("If the language data is shared under established licenses (such as e.g. **MIT license** or **CC-BY-3.0**), please select all that apply below (use the `Add license n` checkbox below if more than one):")
            entry_dict["availability"]["licensing"]["license_list"] = st.multiselect(
                label=f"Under which licenses is the data shared?",
                options=licenses,
            )
        else:
            st.write("TODO: what do we do for nonexistent or unclear licenses?")

    with form_col.expander(
        "Personal Identifying Information" if add_mode else "",
        expanded = add_mode,
    ):
        st.write("Please provide as much information as you can find about the data's contents related to personally identifiable and sensitive information:")
        entry_dict["availability"]["pii"]["has_pii"] = st.radio(
            label="Does the language data in the resource contain personally identifiable or sensitive information?",
            help="See the guide for descriptions and examples. The default answer should be 'Yes'. Answers of 'No' and 'Unclear' require justifications.",
            options=["Yes", "Yes - text author name only", "No", "Unclear"],
        )
        if entry_dict["availability"]["pii"]["has_pii"] == "Yes":
            st.markdown("If the resource does contain personally identifiable or sensitive information, please select what types are likely to be present:")
            entry_dict["availability"]["pii"]["general_pii_list"] = st.multiselect(
                label=f"What type of generic PII (e.g. names, emails, etc,) does the resource contain?",
                options=pii_categories["general"],
                help="E.g.: Does the resource contain names, birth dates, or personal life details?",
            )
            entry_dict["availability"]["pii"]["numeric_pii_list"] = st.multiselect(
                label=f"What type of numeric PII (e.g. phone numbers, social security numbers, etc.) does the resource contain?",
                options=pii_categories["numbers"],
                help="E.g.: Does the resource contain phone numbers, credit card numbers, or other numbers?",
            )
            entry_dict["availability"]["pii"]["sensitive_pii_list"] = st.multiselect(
                label=f"What type of sensitive PII (e.g. health status, poilitcal opinions, sexual orientation, etc.) does the resource contain?",
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
                    key="processed_justification_other"
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
        expanded = add_mode,
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
        expanded = add_mode,
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
        "category": "",
        "text_format": "",
        "text_is_transcribed": "",
        "text_transcribed_available": "",
        "text_transcribed_mode": "",
        "instance_type": "",
        "instance_count": "",
        "instance_size": "",
        "validated": False,
    }
    with form_col.expander(
        "Media type" if add_mode else "",
        expanded=add_mode,
    ):
        st.write("Please provide information about the format of the language data")
        entry_dict["media"]["category"] = st.selectbox(
            label="The language data in the resource is primarily:",
            options=["", "text", "audiovisual", "image"],
            help="Media data provided with transcription should go into **text**, then select the *transcribed* option. PDFs that have pre-extracted text information should go into **text**, PDFs that need OCR should go into **images**, select the latter if you're unsure",
        )
        if entry_dict["media"]["category"] == "text":
            entry_dict["media"]["text_format"] = st.selectbox(
                label="What is the format of the text?",
                options=["", "plain text", "HTML", "PDF", "XML", "mediawiki", "other"],
            )
            if entry_dict["media"]["text_format"] == "other":
                entry_dict["media"]["text_format"] = st.text_input(
                    label="You entered `other` for the text format, what format is it?",
                )
            entry_dict["media"]["text_is_transcribed"] = st.radio(
                label="Was the text transcribed from another media format (e.g. audio or image)",
                options=["Yes - audiovisual", "Yes - image", "No"],
                index=2,
            )
            if entry_dict["media"]["text_is_transcribed"] != "No":
                entry_dict["media"]["text_transcribed_available"] = st.radio(
                    label="Are the source media available at the same location?", options=["Unavailable", "Available"]
                )
                entry_dict["media"]["text_transcribed_mode"] = st.radio(
                    label="How was the transcription obtained?", options=["Unknown", "Manually", "Automatically"]
                )
        if entry_dict["media"]["category"] == "audiovisual" or (
            entry_dict["media"]["category"] == "text"
            and "audiovisual" in entry_dict["media"]["text_is_transcribed"]
        ):
            entry_dict["media"]["audiovisual_format"] = st.selectbox(
                label="What is the format of the audiovisual data?",
                options=["", "mp4", "wav", "video", "other"],
            )
            if entry_dict["media"]["audiovisual_format"] == "other":
                entry_dict["media"]["audiovisual_format"] = st.text_input(
                    label="You entered `other` for the audiovisual format, what format is it?",
                )
        if entry_dict["media"]["category"] == "image" or (
            entry_dict["media"]["category"] == "text"
            and "image" in entry_dict["media"]["text_is_transcribed"]
        ):
            entry_dict["media"]["image_format"] = st.selectbox(
                label="What is the format of the image data?",
                options=["", "JPEG", "PNG", "PDF", "TIFF", "other"],
            )
            if entry_dict["media"]["image_format"] == "other":
                entry_dict["media"]["image_format"] = st.text_input(
                    label="You entered `other` for the image format, what format is it?",
                )

    with form_col.expander(
        "Media amounts" if add_mode else "",
        expanded=add_mode,
    ):
        st.write(
            "We need to at least provide an estimate of the amount of data in the dataset or primary source:"
        )
        entry_dict["media"]["instance_type"] = st.selectbox(
            label="What does a single instance of language data consist of in this dataset/primary source?",
            options=["", "article", "post", "dialogue", "episode", "book", "other"]
        )
        if entry_dict["media"]["instance_type"] == "other":
            entry_dict["media"]["instance_type"] = st.text_input(
                label="You entered `other` for the instance description. Please provide a description.",
            )
        entry_dict["media"]["instance_count"] = st.selectbox(
            label="Please estimate the number of instances in the dataset",
            options=["", "n<100", "100<n<1K", "1K<n<10K", "10K<n<100K", "100K<n<1M", "1M<n<1B", "n>1B"]
        )
        entry_dict["media"]["instance_size"] = st.selectbox(
            label="How long do you expect each instance to be on average interms of number of words?",
            options=["", "n<10", "10<n<100", "100<n<10,000", "n>10,000"]
        )

if entry_dict["type"] == "organization":
    if add_mode:
        form_col.markdown("### Partner Information")
    with form_col.expander(
        "Addiional organization information" if add_mode else "",
        expanded=add_mode,
    ):
        st.write("TODO: what else do we need to know about an organization")

# visualize and download
display_col.markdown("### Review and Save Entry" if add_mode else "")
if add_mode:
    with display_col.expander(
        "Show current entry" if add_mode else "",
        expanded=add_mode
    ):
        st.download_button(
            label="Download output as `json`",
            data=json.dumps(entry_dict, indent=2),
            file_name="resource_entry.json" if entry_dict["uid"] == "" else f"{entry_dict['uid']}_entry.json",
        )
        st.markdown(f"You are entering a new resource of type: *{entry_dict['type']}*")
        st.write(entry_dict)

with viz_col.expander(
    "Select resources to visualize" if viz_mode else "",
    expanded=viz_mode
):
    st.write("TODO: add selection widgets")

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
    with viz_col:
        folium_static(world_map, width=1200, height=600)

with viz_col.expander(
    "ElasticSearch of resource names and descriptions" if viz_mode else "",
    expanded=viz_mode
):
    st.write("TODO: implement ElasticSearch index and enable search here")


with val_col.expander(
    "Select catalogue entry to validate" if val_mode else "",
    expanded=val_mode,
):
    st.write("TODO: either propose an entry that still needs to be validate, or let the user navigate and find one themselves")

if val_mode:
    val_col.markdown("### Entry Category, Name, ID, Homepage, Description")

with val_col.expander(
    "Validate general information for the entry" if val_mode else "",
    expanded=val_mode,
):
    st.write("TODO: load general information for selected entry and let user modify/save/validate")

if val_mode:
    val_col.markdown("### Languages and locations")

with val_col.expander(
    "Validate language information for the entry" if val_mode else "",
    expanded=val_mode,
):
    st.write("TODO: load language information for selected entry and let user modify/save/validate")

with val_col.expander(
    "Validate location information for the entry" if val_mode else "",
    expanded=val_mode,
):
    st.write("TODO: load location information for selected entry and let user modify/save/validate")
