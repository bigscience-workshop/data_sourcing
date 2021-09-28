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

with form_col.expander("General resource information"):
    st.write("TODO: name, short description")
    st.write("TODO: language, language variety, script, region")

if resource_type == "Processed dataset":
    with form_col.expander("Primary sources"):
        st.write("TODO: questions about primary sources")

if resource_type == "Primary source":
    with form_col.expander("Primary source type"):
        st.write("TODO: taxonomy - website/published work/collection")

    with form_col.expander("Availability of the language data"):
        st.write("TODO: how to obtain, license, personal information, will you do it")

    with form_col.expander("Format of the language data"):
        st.write("TODO: expected medium and processing needs")

display_col.markdown("## New catalogue entry: save output\n --- \n")
display_col.markdown(f"You are entering a new resource of type: *{resource_type}*")
