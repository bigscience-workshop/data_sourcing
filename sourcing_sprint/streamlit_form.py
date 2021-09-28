import streamlit as st

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

### Submitter information
"""
st.sidebar.markdown(description, unsafe_allow_html=True)

with st.sidebar.form("submitter_information"):
    submitter_name = st.text_input(
        label="Name of submitter:"
    )
    submitter_email = st.text_input(
        label="Email (optional, enter if you are available to follow up on this catalogue entry):"
    )
    submitted_info = st.form_submit_button("Submit")

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
resource_type = st.sidebar.radio(
    label="What resource type are you submitting?",
    options=["Primary source", "Processed dataset", "Partner organization"],
    help=resource_type_help,
)

form_col, _, display_col = st.columns([10, 1, 7])

form_col.markdown("## New catalogue entry: input form\n --- \n")

form_col.markdown("#### Name, ID, Homepage")
resource_name = form_col.text_input(
    label=f"Provide a descriptive name for the resource",
    help="This should be a human-readable name such as e.g. **Le Monde newspaper** (primary source), **EXAMS QA dataset** (processed dataset), or **Creative Commons** (partner organization)",
)
resource_uid = form_col.text_input(
    label=f"Provide a short `camel_case` unique identifier for the resource",
    help="For example `le_monde_primary`, `exams_dataset`, or `creative_commons_org`",
)
resource_homepage  = form_col.text_input(
    label=f"If available, provide a link to the home page for the resource",
    help="e.g. https://www.lemonde.fr/, https://github.com/mhardalov/exams-qa, or https://creativecommons.org/",
)
resource_homepage  = form_col.text_area(
    label=f"Provide a short description of the resource",
    help="Describe the resource in a few words to a few sentences, the description will be used to index and navigate the catalogue",
)

form_col.markdown("#### Language and location")
resource_is_multilingual = form_col.radio(
    label="Does the resource cover several languages?",
    options=["Yes", "No"],
    index=1,
)
if resource_is_multilingual == "Yes":
    lang_number = form_col.number_input(
        label="How many languages does the resource cover?",
        min_value=2,
        value=2,
    )
else:
    lang_number = 1

languages = {
    "Arabic": "Arabic",
    "Basque": "Basque",
    "Catalan": "Spanish: Catalan",
    "Chinese": "Chinese",
    "English": "English",
    "French": "French",
    "Indic": "Indic languages, incl. Bengali, Hindi, Urdu...",
    "Indonesian": "Indonesian",
    "Niger-Congo": "African languages of the Niger-Congo family, incl. Bantu languages",
    "Portuguese": "Portuguese",
    "Spanish": "Spanish: Castillan",
    "Vietnamese": "Vietnamese",
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
resource_languages = []
for lni in range(lang_number):
    resource_lang_group = form_col.selectbox(
        label=f"Language (group) {lni+1}",
        options=languages,
    )
    if resource_lang_group == "Niger-Congo":
        resource_lang_subgroup = form_col.selectbox(
            label=f"Niger-Congo language {lni+1}",
            options=niger_congo_languages,
        )
    elif resource_lang_group == "Indic":
        resource_lang_subgroup = form_col.selectbox(
            label=f"Indic language {lni+1}",
            options=indic_languages,
        )
    else:
        resource_lang_subgroup = ""
    resource_languages += [(resource_lang_group, resource_lang_subgroup)]


if resource_type == "Processed dataset":
    form_col.markdown("#### Processed dataset availability")
    form_col.write("TODO: how to obtain, license, personal information, will you do it")
    form_col.markdown("#### Primary sources of processed dataset")
    form_col.write("TODO: list and either link OR fill out relevant information")

if resource_type == "Primary source":
    form_col.markdown("#### Primary source type")
    form_col.write("TODO: taxonomy - website/published work/collection")
    form_col.markdown("#### Primary source availability")
    form_col.write("TODO: how to obtain, license, personal information, will you do it")

form_col.markdown("#### Media type and format")
form_col.write("TODO: list of formats and expected processing needs")

display_col.markdown("## New catalogue entry: save output\n --- \n")
display_col.markdown(f"You are entering a new resource of type: *{resource_type}*")