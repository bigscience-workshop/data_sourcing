import json
import streamlit as st

##################
## resources
##################

### Countries and languages
# from Wikipedia and https://unstats.un.org/unsd/methodology/m49/
regions, countries, region_tree = json.load(open("unstats_regions_countries.json", encoding="utf-8"))

bcp_47 = json.load(open("bcp47.json", encoding="utf-8"))
bcp_47_langs = [x for x in bcp_47["subtags"] if x["type"] == "language"]


languages = {
    "Arabic": "Arabic",
    "Basque": "Basque",
    "Catalan": "Catalan",
    "Chinese": "Chinese",
    "English": "English",
    "French": "French",
    "Indic": "Indic languages, incl. Bengali, Hindi, Urdu...",
    "Indonesian": "Indonesian",
    "Niger-Congo": "African languages of the Niger-Congo family, incl. Bantu languages",
    "Portuguese": "Portuguese",
    "Spanish": "Spanish",
    "Vietnamese": "Vietnamese",
    "other": "Other",
}
# https://meta.wikimedia.org/wiki/African_languages
niger_congo_languages = [
    "Akan",
    "Bambara",
    "Chi Chewa",
    "ChiShona",
    "ChiTumbuka",
    "Fon",
    "Igbo",
    "isiZulu",
    "Kinyarwanda",
    "Kikongo",
    "Kikuyu",
    "Kirundi",
    "Lingala",
    "Luganda",
    "Northern Sotho",
    "Sesotho",
    "Setswana",
    "Swahili",
    "Twi",
    "Wolof",
    "Xhosa",
    "Xitsonga",
    "Yoruba",
]
# TODO: add more
indic_languages = [
    "Assamese",
    "Bengali",
    "Gujarati",
    "Hindi",
    "Kannada",
    "Malayalam",
    "Marathi",
    "Odia",
    "Punjabi",
    "Telugu",
    "Tamil",
    "Urdu",
]
MAX_LANGS = 25
MAX_COUNTRIES = 25

### Primary source categories
primary_taxonomy = {
    "website": [
        "social media",
        "forum",
        "news or magazine website",
        "wiki",
        "blog",
        "official website",
        "content repository, archive, or collection",
        "other",
    ],
    "collection": [
        "books/book publisher",
        "scientific articles/journal",
        "newspaper",
        "radio",
        "clips",
        "movies and documentaries",
        "podcasts",
        "other",
    ],
    "other": [],
}

# from Data Tooling docs
pii_categories = [
    "names",
    "addresses",
    "dates (birth, death, etc.)",
    "telephone numbers",
    "vehicle identifiers and serial numbers",
    "fax numbers",
    "device identifiers and serial numbers",
    "email addresses",
    "URLs",
    "social security numbers",
    "IP addresses",
    "medical record numbers",
    "biometric identifiers (fingerprints, voice, etc.)",
    "health plan beneficiary numbers",
    "full-face photographs and comparable images",
    "account numbers",
    "uniquely identifying numbers",
    "certificate/license numbers"
]

sensitive_categories = [
    "racial or ethnic origin",
    "political opinioins",
    "religious or philosophical beliefs",
    "trade-union membership",
    "genetic data",
    "health-related data",
    "data concerning a person's sex life or sexual orientation"
]
MAX_PII = 25

resource_dict = {
    "type": "",
    "name": "",
    "uid": "",
    "homepage": "",
    "description": "",
    "languages": [],
    "resource_location": "",
    "language_locations": [],
}

licenses = json.load(open("licenses.json", encoding="utf-8"))
MAX_LICENSES = 25
##################
## streamlit
##################
st.set_page_config(
    page_title="BigSCience Language Resource Catalogue Input Form",
    page_icon="https://avatars.githubusercontent.com/u/82455566",
    layout="wide",
    initial_sidebar_state="auto",
)

description = """
# Adding a new resource

This form can be used to add a new entry to the BigScience Data Sourcing Catalogue.

To do so, please add your name, email (optional), the type of resource you would like to add,
then fill out the form on the right.

For more information: [**guide to adding a new catalogue entry.**](https://github.com/bigscience-workshop/data_sourcing/blob/master/sourcing_sprint/guide.md#guide-to-submitting-sources-to-the-bigscience-data-sourcing-hackathon)

### Submitter information
"""
st.sidebar.markdown(description, unsafe_allow_html=True)

with st.sidebar.form("submitter_information"):
    submitter_name = st.text_input(label="Name of submitter:")
    submitter_email = st.text_input(
        label="Email (optional, enter if you are available to follow up on this catalogue entry):"
    )
    submitted_info = st.form_submit_button("Submit self information")

st.sidebar.markdown("### Resource type")
resource_type_help = """
You may choose one of the following three resource types:
- *Primary source*: a single source of language data (text or speech), such as a newspaper, radio, website, book collection, etc.
You will be asked to fill in information about the availability of the source, its properties including availability and presence of personal information,
its owners or producers, and the format of the language data.
- *Processed dataset*: a processed NLP dataset containing language data that can be used for language modeling (most items should be at least a few sentences long).
You will be asked to fill in information about the dataset object itself as well as the primary sources it was derived from
(e.g. Wikipedia, or news sites for most summarization datasets).
- *Partner organization*:
"""
resource_dict["type"] = st.sidebar.radio(
    label="What resource type are you submitting?",
    options=["Primary source", "Processed dataset", "Partner organization"],
    help=resource_type_help,
)

form_col, _, display_col = st.columns([10, 1, 7])

form_col.markdown("## New catalogue entry: input form\n --- \n")

form_col.markdown("### Name, ID, Homepage, Description")
with form_col.expander("General information"):
    resource_dict["name"] = st.text_input(
        label=f"Provide a descriptive name for the resource",
        help="This should be a human-readable name such as e.g. **Le Monde newspaper** (primary source), **EXAMS QA dataset** (processed dataset), or **Creative Commons** (partner organization)",
    )
    resource_dict["uid"] = st.text_input(
        label=f"Provide a short `snake_case` unique identifier for the resource",
        help="For example `le_monde_primary`, `exams_dataset`, or `creative_commons_org`",
    )
    resource_dict["homepage"] = st.text_input(
        label=f"If available, provide a link to the home page for the resource",
        help="e.g. https://www.lemonde.fr/, https://github.com/mhardalov/exams-qa, or https://creativecommons.org/",
    )
    resource_dict["description"] = st.text_area(
        label=f"Provide a short description of the resource",
        help="Describe the resource in a few words to a few sentences, the description will be used to index and navigate the catalogue",
    )

form_col.markdown("### Languages and locations")

with form_col.expander("Languages"):
    st.write("Add all of the languages that are covered by the resource (see 'Add language' checkbox)")
    resource_languages = []
    buttons_lang = [False for _ in range(MAX_LANGS + 1)]
    buttons_lang[0] = True
    for lni in range(MAX_LANGS):
        if buttons_lang[lni]:
            resource_lang_group = st.selectbox(
                label=f"Language (group) {lni+1}",
                options=[""] + list(languages.keys()),
                format_func=lambda x: languages.get(x, ""),
                help="This is the higher-level classification, Indic and Niger-Congo languages open a new selection box for the specific language. If you cannot find the language in either the top-level or lower-level menus, select `Other` to search in a more extensive list.",
            )
            if resource_lang_group == "other":
                resource_lang_group = st.selectbox(
                    label=f"Language (group) {lni+1}",
                    options= [''] + [', '.join(x['description']) for x in bcp_47_langs],
                    help="This is a comprehensive list of Languages, please select one using the search function",
                )
            if resource_lang_group == "Niger-Congo":
                resource_lang_subgroup = st.selectbox(
                    label=f"Niger-Congo language {lni+1}",
                    options=[""] + niger_congo_languages,
                )
            elif resource_lang_group == "Indic":
                resource_lang_subgroup = st.selectbox(
                    label=f"Indic language {lni+1}",
                    options=[""] + indic_languages,
                )
            else:
                resource_lang_subgroup = ""
            resource_languages += [(resource_lang_group, resource_lang_subgroup)]
            buttons_lang[lni + 1] = st.checkbox(f"Add language {lni+2}")
    resource_dict["languages"] = [(gr, ln) for gr, ln in resource_languages if gr != ""]

with form_col.expander("Locations"):
    st.write("Location of the aggregated resource:")
    resource_dict["resource_location"] = st.selectbox(
        label="Where is the resource or organization itself located or hosted?",
        options=[""] + countries,
        help="E.g.: where is the **website hosted**, what is the physical **location of the library**, etc.?",
    )
    st.write("Add all of the countries that have data creators represented in/by the resource/organization")
    buttons_countries = [False for _ in range(MAX_COUNTRIES + 1)]
    buttons_countries[0] = True
    for lni in range(MAX_COUNTRIES):
        if buttons_countries[lni]:
            lang_loc = st.selectbox(
                label=f"Where are the language creators located? Country {lni+1}",
                options=[""] + countries,
                index=countries.index(resource_dict["resource_location"]) + 1
                if lni == 0 and resource_dict["resource_location"] in countries
                else 0,
                help="E.g.: where are the **people who write on the website** hosted, where are the **media managed by the library** from, etc.?",
            )
            buttons_countries[lni + 1] = st.checkbox(f"Add country {lni+2}")
            if lang_loc != "":
                resource_dict["language_locations"] += [lang_loc]

if resource_dict["type"] == "Primary source":
    form_col.markdown("### Primary source availability")
    with form_col.expander("Obtaining the data: online availability and data owner/custodian"):
        st.markdown("---\n#### Availability for download")
        resource_dict["available_for_download"] = st.radio(
            label="Can the data be obtained online?",
            options=[
                "Yes - it has a direct download link or links",
                "Yes - after signing a user agreement",
                "No - but the current owners/custodians have contact information for data queries",
                "No - we would need to spontaneously reach out to the current owners/custodians"
            ],
        )
        if "Yes -" in resource_dict["available_for_download"]:
            resource_dict["download_url"] = st.text_input(
                label="Please provide the URL where the data can be downloaded",
                help="If the data source is a website or collection of files, please provided the top-level URL or location of the file directory",
            )
        st.markdown("---\n#### Information about the data owners/custodians")
        resource_dict["owner_type"] = st.selectbox(
            label="Is the data owned or managed by:",
            options=[
                "",
                "A commercial entity",
                "A library, museum, or archival institute",
                "A nonprofit/NGO (other)",
                "A government organization",
                "A private individual",
                "Unclear",
                "other",
            ],
        )
        if resource_dict["owner_type"] == "other":
            resource_dict["owner_type"] = st.text_input(
                label="You entered `other` for the data owner/custodian, how would you categorize them?",
            )
        resource_dict["owner_name"] = st.text_input(
            label="Please enter the name of the entity that manages the data:"
        )
        resource_dict["owner_email"] = st.text_input(
            label="If available, please enter an email adress that can be used to ask them about using/obtaining the data:"
        )
        resource_dict["owner_contact_submitter"] = st.radio(
            label="Would you be willing to reach out to the entity to ask them about using their data (with support from the BigScience data sourcing team)? If so, make sure to fill out your email information in the left sidebar.",
            options=["Yes", "No"],
            index=1,
        )
        resource_dict["owner_additional"] = st.text_input(
            label="Where can we find more information about the data owner/custodian? Please provide a URL",
            help="For example, please provide the URL of the web page with their contact information, the homepage of the organization, or even their Wikipedia page if it exists."
        )

    with form_col.expander("Data licenses and Terms of Service"):
        resource_dict["resource_licenses"] = []
        st.write("Please provide as much information as you can find about the data's licensing and terms of use:")
        resource_dict["has_licenses"] = st.radio(
            label="Does the language data in the resource come with explicit licenses of terms of use?",
            options=["Yes", "No", "Unclear"],
        )
        st.markdown("---\n")
        if resource_dict["has_licenses"] == "Yes":
            resource_dict["license_description"] = st.text_area(
                label=f"If the resource has explicit terms of use or license text, please copy it in the following area",
                help="The text may be included in a link to the license webpage. You do not neet to copy the text if it corresponds to one of the established licenses that may be selected below.",
            )
            st.markdown("If the language data is shared under established licenses (such as e.g. **MIT license** or **CC-BY-3.0**), please select all that apply below (use the `Add license n` checkbox below if more than one):")
            buttons_licenses = [False for _ in range(MAX_LICENSES + 1)]
            buttons_licenses[0] = True
            for lni in range(MAX_LICENSES):
                if buttons_licenses[lni]:
                    license = st.selectbox(
                        label=f"Under which license is the data shared? License {lni+1}",
                        options=[""] + licenses,
                        help="E.g.: Is the data shared under a CC or MIT license?",
                    )
                    buttons_licenses[lni + 1] = st.checkbox(f"Add license {lni+2}")
                    if license != "":
                        resource_dict["resource_licenses"] += [license]
        else:
            st.write("TODO: what do we do for nonexistent or unclear licenses?")

    with form_col.expander("Personal Identifying Information"):
        #st.write("TODO: Risk of PII - category and justificaction (cat + string)")
        resource_dict["resource_pii"] = []
        st.write("Please provide as much information as you can find about the data's contents related to personally identifiable and sensitive information:")
        resource_dict["has_pii"] = st.radio(
            label="Does the language data in the resource contain personally identifiable or sensitive information?",
            help="See the guide for descriptions and examples. The default answer should be 'Yes'. Answers of 'No' and 'Unclear' require justifications.",
            options=["Yes", "No", "Unclear"],
        )
        st.markdown("---\n")
        if resource_dict["has_pii"] == "Yes":
            st.markdown("If the resource does contain personally identifiable or sensitive information, please select what types:")
            buttons_pii = [False for _ in range(MAX_PII + 1)]
            buttons_pii[0] = True
            for lni in range(MAX_PII):
                if buttons_pii[lni]:
                    pii = st.selectbox(
                        label=f"What type(s) of PII does the resource contain? Type {lni+1}",
                        options=[""] + pii_categories + sensitive_categories,
                        help="E.g.: Does the resource contain names, birth dates, or personal life details?",
                    )
                    buttons_pii[lni + 1] = st.checkbox(f"Add PII Type {lni+2}")
                    if pii != "":
                        resource_dict["resource_pii"] += [pii]
        else:
            resource_dict["pii_justification"] = st.radio(
                label="What is the justification for this resource possibly not having personally identifiable or sensitive content?",
                options=["general knowledge not written by or referring to private persons", "fictional text", "other"],
            )
            if resource_dict["pii_justification"] == "other":
                resource_dict["pii_justification"] = st.text_area(
                    label=f"If the resource has explicit terms of use or license text, please copy it in the following area",
                    help="The text may be included in a link to the license webpage. You do not neet to copy the text if it corresponds to one of the established licenses that may be selected below.",
                )
                
    form_col.markdown("### Primary source type")
    with form_col.expander("Source category"):
        primary_tax_top = st.radio(
            label="Is the resource best described as a:",
            options=["collection", "website", "other"],
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
        resource_dict["primary_source_type"] = (primary_tax_top, primary_tax_web, primary_tax_col)

    form_col.markdown("### Media type, format, size, and processing needs")
    with form_col.expander("Media type"):
        st.write("Please provide information about the format of the language data")
        media_type = {}
        primary_media = st.radio(
            label="The language data in the resource is primarily:",
            options=["text", "audiovisual", "image"],
            help="Media data provided with transcription should go into **text**, then select the *transcribed* option. PDFs that have pre-extracted text information should go into **text**, PDFs that need OCR should go into **images**, select the latter if you're unsure",
        )
        media_type["category"] = primary_media
        if primary_media == "text":
            primary_media_text = st.selectbox(
                label="What is the format of the text?",
                options=["", "plain text", "HTML", "PDF", "XML", "mediawiki", "other"],
            )
            if primary_media_text == "other":
                primary_media_text = st.text_input(
                    label="You entered `other` for the text format, what format is it?",
                )
            media_type["text_format"] = primary_media_text
            primary_media_transcribed = st.radio(
                label="Was the text transcribed from another media format (e.g. audio or image)",
                options=["Yes - audiovisual", "Yes - image", "No"],
                index=2,
            )
            if primary_media_transcribed != "No":
                primary_media_transcribed_available = st.radio(
                    label="Are the source media available at the same location?", options=["Unavailable", "Available"]
                )
                primary_media_transcribed_mode = st.radio(
                    label="How was the transcription obtained?", options=["Unknown", "Manually", "Automatically"]
                )
            else:
                primary_media_transcribed_available = ""
                primary_media_transcribed_mode = ""
            media_type["is_transcribed"] = (
                primary_media_transcribed,
                primary_media_transcribed_available,
                primary_media_transcribed_mode,
            )
        if primary_media == "audiovisual" or (
            primary_media == "text"
            and primary_media_transcribed_available == "Available"
            and "audiovisual" in primary_media_transcribed
        ):
            primary_media_audiovisual = st.selectbox(
                label="What is the format of the audiovisual data?",
                options=["", "mp4", "wav", "video", "other"],
            )
            if primary_media_audiovisual == "other":
                primary_media_audiovisual = st.text_input(
                    label="You entered `other` for the audiovisual format, what format is it?",
                )
            media_type["audiovisual_format"] = primary_media_audiovisual
        if primary_media == "image" or (
            primary_media == "text"
            and primary_media_transcribed_available == "Available"
            and "image" in primary_media_transcribed
        ):
            primary_media_image = st.selectbox(
                label="What is the format of the image data?",
                options=["", "JPEG", "PNG", "PDF", "TIFF", "other"],
            )
            if primary_media_image == "other":
                primary_media_image = st.text_input(
                    label="You entered `other` for the image format, what format is it?",
                )
            media_type["image_format"] = primary_media_image
        resource_dict["media_type"] = media_type

    with form_col.expander("Media amounts"):
        st.write(
            "TODO: amount of data - list of number of items, what an item is, and expected number of words per item"
        )

if resource_dict["type"] == "Processed dataset":
    form_col.markdown("### Processed dataset availability")
    with form_col.expander("Obtaining the data: online availability and owner/provider"):
        st.write("TODO: how to obtain, license, personal information, will you do it")

    form_col.markdown("### Primary sources of processed dataset")
    with form_col.expander("List primary sources"):
        form_col.write("TODO: list and either link OR fill out relevant information")

display_col.markdown("## New catalogue entry: save output\n --- \n")
display_col.download_button(
    label="Download output as `json`",
    data=json.dumps(resource_dict, indent=2),
    file_name="resource_entry.json" if resource_dict["uid"] == "" else f"{resource_dict['uid']}_entry.json",
)
display_col.markdown(f"You are entering a new resource of type: *{resource_dict['type']}*")
display_col.write(resource_dict)
