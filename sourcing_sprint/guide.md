# Guide to Submitting Sources to the BigScience Data Sourcing Hackathon

## Table of Contents
* [Getting Started](#getting-started)
* [Loading the Form](#loading-the-form)
* [Adding a New Entry](#adding-a-new-entry)
  * [Adding a Primary Source](#adding-a-primary-source)
    * [Entry Category, Name, ID, Homepage, Description](#entry-category-name-id-homepage-description)
    * [Entry Languages and Locations](#entry-languages-and-locations)
    * [Representative, Owner, or Custodian](#representative-owner-or-custodian)
    * [Availability of the Resource: Procuring, Licenses, PII](#availability-of-the-resource-procuring-licenses-pii)
    * [Primary Source Type](#primary-source-type)
    * [Media Type, Format, Size, and Processing Needs](#media-type-format-size-and-processing-needs)
  * [Adding a Processed Dataset](#adding-a-processed-dataset)
    * [Entry Category, Name, ID, Homepage, Description](#entry-category-name-id-homepage-description-1)
    * [Entry Languages and Locations](#entry-languages-and-locations-1)
    * [Representative, Owner, or Custodian](#representative-owner-or-custodian-1)
    * [Availability of the Resource: Procuring, Licenses, PII](#availability-of-the-resource-procuring-licenses-pii-1)
    * [Primary Sources of Processed Dataset](#primary-sources-of-processed-dataset)
  * [Adding a Language Organization or Advocate](#adding-a-language-organization-or-advocate)
    * [Entry Category, Name, ID, Homepage, Description](#entry-category-name-id-homepage-description-2)
    * [Entry Languages and Locations](#entry-languages-and-locations-2)
    * [Representative, Owner, or Custodian](#representative-owner-or-custodian-2)
  * [Submitting the Form](#submitting-the-form)
* [Explore the Current Catalogue](#explore-the-current-catalogue)
* [Validate an Existing Entry](#validate-an-existing-entry)
* [Contact Information](#contact-information)

## Getting Started

Thank you for participating in the BigScience Data Sourcing hackathon! Please use this guide as you submit information about potential data sources for the BigScience dataset using the form.

## Loading the Form

You can load the form on your browser by going to: http://23.251.145.180:8501/

There are three app modes to select from in the left sidebar of the form: `Add a new entry`, `Explore the current catalogue`, and `Validate an existing entry`. Select the appropriate tab to either complete the form for a new data source submission, look at a map of what sources have been submitted to the hackathon so far, or verify or add information to those submitted sources.

## Adding a New Entry

To get started, please select the `Add a new entry` button and add your name and your email (optional) in the left sidebar. Then proceed to filling out the form. 

For the purposes of this work, we're organizing resources into three categories: primary source, processed dataset, and language organization or advocate. Select the type of resource you are providing information for in the **General Information** subsection of the **Entry Category, Name, ID, Homepage, Description** section of the form.

### Adding a Primary Source

A primary source is a single source of language data (text or speech), such as a newspaper, radio, website, book collection, etc. We're particularly interested in this kind of data as it helps us towards our goal of building a more representative data catalogue by expanding our search beyond online resources that are typically found in NLP datasets. 

You will be asked to fill in information about the availability of the source, its properties including availability and presence of personal information, its owners or producers, and the format of the language data.

#### Entry Category, Name, ID, Homepage, Description

First, provide a descriptive name for the resource. This should be a human-readable name such as *Le Monde newspaper*. 

In the next box provide a short `snake_case` unique identifier for the resource, for example `le_monde_primary`. The box will autopopulate based on your name for the resource, but may need modifications if the identifier has already been submitted for another resource.

If available, provide a link to the home page for the resource, e.g. https://www.lemonde.fr/.

Provide a short description of the resource, in a few words to a few sentences. The description will be used to index and navigate the catalogue. 

#### Entry Languages and Locations

For each entry, we need to catalogue which languages are represented or focused on, as characterized by both the language names and the geographical distribution of the language data creators who contribute to the primary source. We use language data creators to refer to those who wrote the text or spoke the speech that we refer to as data, as opposed to those who may have found, formatted, or created metadata and annotations for the data.

##### Languages

Please add all of the languages that are covered by the resource. You may select the language from the dropdown menu or type out the name of the language and submit by hitting enter. This is the higher-level classification of the languages that currently have working groups in the BigScience project. Selecting the Indic and Niger-Congo languages will open a new selection box for the specific language, and selecting Arabic will open a new selection box for the dialect. An additional textbox is available to provide further comments about the language variety. 

You may also click the `Show other languages` button to add languages that are currently not in the BigScience list. Again, you may select the language from the dropdown menu or type out the name of the language and submit by hitting enter.

Continuing with the above example of *Le Monde newspaper*, you would select `French` for the language and could additionally add a comment that the language variety is that spoken in France, as opposed to Canada or Senegal. 

##### Locations

In addition to the names of the languages covered by the entry, we need to know where the language creators are primarily located. You may select full *macroscopic areas* such as continents and/or *specific countries/regions*. Please choose all that apply by selecting from the dropdown menus. 

For *Le Monde newspaper*, the macroscopic area would be `Western Europe` and the specific country would be `France`.

#### Entry Representative, Owner, or Custodian

From the dropdown box, please select the type of entity you are providing information about. Possible answers include `a private individual`, `a commercial entity`, `a library, museum, or archival institute`, `a university or research institution`, `a nonprofit/NGO`, `a government organization`, and `other`. If you select `other`, please provide a description. 

Select the country, nation, region, or territory where the entity is located or hosted. Please enter the name of a contact person for the entity. The textbox will autopopulate with the name of the entity, but please replace this with the name of an individual if there is a specific person we can direct our query to. If available, please enter an email address that can be used to ask them about using/obtaining their data.

Please select whether you would be willing to contact the entity to ask them about using their data (with support from the BigScience Data Sourcing team). Is yes, please me make sure that your email information is entered in the left sidebar.

If there is a URL where we can find out more information about the data owner/custodian, please add it to the final textbox. For example, please provide the URL of the webpage with their contact information, the homepage of the organization, or even their Wikipedia page if it exists.

For *Le Monde newspaper*, the type is `a commercial entity`, the location of the entity is `France`, the contact name is `Sacha Morard`, the contact email is `droitsdauteur@lemonde.fr` and additional information on the entity is available at `https://fr.wikipedia.org/wiki/Groupe_Le_Monde`. 

#### Availability of the Resource: Procuring, Licenses, PII

##### Obtaining the data: Online availability and data owner/custodian

Please characterize the availability of the resource with one of four possible answers:
1. Yes - it has a direct download link or links
2. Yes - after signing a user agreement
3. No - but the current owners/custodians have contact information for data queries
4. No - we would need to spontaneously reach out to the current owners/custodians

If yes,then provide the URL where the data can be downloaded. If the data source is a website or collection of files, please provide the top-level URL or location of the file directory. If no, then please provide the email of the person to contact to obtain the data if it is different from the contact email entered for the data custodian in the **Entry Representative, Owner, or Custodian** section.

For *Le Monde newspaper*, the availability answer is `No - we would need to spontaneously reach out to the current ownders/custodians`. The contact was provided in the previous section. 

##### Data licenses and Terms of Service

Please provide as much information as you can find about the data's licensing and terms of use. This information will help us determine whether or not we can use the data in the BigScience dataset, for training the BigScience model, and whether or not we can share the data afterwards. Please respond as to whether or not the language data in the resource come with explicit licenses of terms of use.

If yes, select the option that best characterizes the licensing status of the data: `public domain`, `multiple licenses`, `copyright - all rights reserved`, `open license`, `research use`, `non-commercial use`, or `do not distribute`. Select each of the licenses (if more than one) that the data is shared under. If you select `other`, please copy the text for the license or terms of use into the form. The text may be included in a link to the license webpage. You do not neet to copy the text if it corresponds to one of the established licenses that may be selected.

If there are no licenses or terms of service, or if it is unclear as to what they are, please provide your best assessment of whether the data can be used to train models while respecting the rights and wishes of the data creators and custodians. This field will serve as a starting point for further investigation.

*Le Monde newspaper* does come with explicit licenses of terms of use, so select `copyright - all rights reserved`. The license is `other`, copy the text from https://moncompte.lemonde.fr/cgv#ancre_propriete into the textbox. 

##### Personally Identifiable Information

Please provide as much information as you can find about the data's contents related to personally identifiable information (PII). This kind of information will impact the BigScience dataset and model in terms of privacy, security, and social impact. For more information please see **###LINK###**. 

We categorize personally identifiable information into three categories:

1. General
- Personally identifying general information includes names, physical and email addresses, website accounts with names or handles, dates (birth, death, etc.), full-face photographs and comparable images, URLS, and biometric identifiers (fingerprints, voice, etc.). 

2. Numbers
- Personally identifying numbers include information such as telephone numbers, fax numbers, vehicle and device identifiers and serial numbers, social security numbers and equivalent, IP addresses, medical record numbers, health plan beneficiary numbers, account numbers, certificate/license numbers, and any other uniquely identifying numbers.

3. Sensitive
- Sensitive information includes descriptions of racial or ethnic origin, political opinions, religious or philosophical beliefs, trade-union membership, genetic data, health-related data, and data concerning a person's sex life or sexual orientation.

Please select whether the resource contains any of these kinds of PII or sensitive information: `yes`, `yes - text author name only`, `no`, or `unclear`. Please note that the default answer should be to assume that there is some kind of PII in the data.

If yes, please select how likely you believe it to be that the resource contains each kind of PII or sensitive information from the dropdown boxes: `very likely`, `somewhat likely`, `unlikely`, or `none`. Then select what kinds of data the resource is likely to contain from the lists of examples in (1), (2), and (3). 

If no or unclear, please select your reason for why there may not be PII in the data. Reasons may include that the data only contains general knowledge not written by or referring to private persons, or that the data consists of fictional text. If there is some other reason, please provide justification in the text box.

*Le Monde newspaper* does contain PII. It is `very likely` to contain generic PII such as names and dates. It is `somewhat likely` to contain numberic PII such as telephone numbers. It is `very likely` to contain sensitive PII such as political opinions, racial or ethic origin, health-related data, and religious or philosophical beliefs. 

#### Primary Source Type

Please provide a description for the type of resource. We provide two possible types:

1. Collection
- Collections may contain books or book publishers, scientific articles and journals, news articles, radio programs, clips, movies and documentaries, or podcasts. Other kinds of data collections may also be included. To add a new category, select `other` from the Collection dropdown menu, and add a description in the textbox. 

2. Website
- Websites may include social media, forums, news or magazine websites, wikis, blogs, official websites, or content repositories, archies, and collections. Other kinds of websites may also be included. To add a new category, select `other` from the Collection dropdown menu, and add a description in the textbox. 

If neither of these options appropriately describes the resource, please select `other` and add a description of the resource. 

For example, *Le Monde newspaper* is a `collection` of `news articles`.

#### Media Type, Format, Size, and Processing Needs

##### Media Type

Please provide information about the format of the language data. This information will help us determine what processing will be necessary to include the resource in the BigScience dataset.

Select whether the language data in the resource is primarily text, audiovisual (from either video or audio recordings), or image data. Media data provided with transcription should select text, then select the transcribed option. PDFs that have pre-extracted text information should select text, while PDFs that need OCR should go into images. Select the latter if you're unsure.

If the data is primarily text, please select what format the text is in from the dropdown menu: `plain text`, `HTML`, `PDF`, `XML`, `mediawiki`, or `other`. If `other`, please enter a text description of the format. Select whether the text was transcribed from another media format and, if so, whether that media format was audiovisual or images. Choose the format of the original data from the dropdown menu, if known.

If the data is primarily audiovisual, please select what format the text is in from the dropdown menu: `mp4`, `wav`, `video`, or `other`. If other, please enter a text description of the format.

If the data is primarily images, please select what format the text is in from the dropdown menu: `JPEG`, `PNG`, `PDF`, `TIFF`, or `other`. If other, please enter a text description of the format.

For example, *Le Monde newspaper* contains `text` data in the following formats: `plain text`, `HTML`, and `PDF`. It is not transcribed data.

##### Media Amounts

In order to estimate the amount of data in the dataset or primary source, we need a approximate count of the number of instances and the typical instance size therein. This will help us organize processing and storage requirements. 

Please select what an instance in the resource consists of: `article`, `post`, `dialogue`, `episode`, `book`, or `other`. If other, please enter a text description of an instance. Select an estimate the number of instances in the resource. Finally, select an estimate of the number of words per instance. Select the range that you think best fits the data, even if you are unsure.

For *Le Monde newspaper*, the instances are `articles`, is number of instances is estimated to be `10K<n<100K`, and the number of words per instances is estimated to be `100<n<10,000`. 

### Adding a Processed Dataset

A processed NLP dataset contains language data that can be used for language modeling. These resources are derived from one or several other primary sources. For example, the CNN/Dailymail summarization dataset is derived from the CNN and Dailymail websites. 

You will be asked to fill in information about the dataset object itself as well as the primary sources it was derived from.

#### Entry Category, Name, ID, Homepage, Description

First, provide a descriptive name for the resource. This should be a human-readable name such as *EXAMS QA dataset*. 

In the next box provide a short `snake_case` unique identifier for the resource, for example `exams_dataset`.

If available, provide a link to the home page for the resource, e.g. https://github.com/mhardalov/exams-qa.

Provide a short description of the resource, in a few words to a few sentences. The description will be used to index and navigate the catalogue. 

#### Entry Languages and Locations

For each entry, we need to catalogue which languages are represented or focused on, as characterized by both the language names and the geographical distribution of the language data creators whose data are contained in the dataset. We use language data creators to refer to those who wrote the text or spoke the speech that we refer to as data, as opposed to those who may have found, formatted, or created metadata and annotations for the data.

##### Languages

Please add all of the languages that are covered by the resource. You may select the language from the dropdown menu or type out the name of the language and submit by hitting enter. This is the higher-level classification of the languages that currently have working groups in the BigScience project. Selecting the Indic and Niger-Congo languages will open a new selection box for the specific language, and selecting Arabic will open a new selection box for the dialect. An additional textbox is available to provide further comments about the language variety. 

You may also click the `Show other languages` button to add languages that are currently not in the BigScience list. Again, you may select the language from the dropdown menu or type out the name of the language and submit by hitting enter.

The *EXAMS QA dataset* covers a large number of languages, so you would select `Arabic`, `French`, `Portuguese`, `Spanish`, and `Vietnamese` from the list of BigScience languages and `Albanian`, `Bulgarian`, `Croatian`, `German`, `Hungarian`, `Italian`, `Lithuanian`, `Macedonian`, `Polish`, `Serbian`, and `Turkish` from the list of all languages. You would further specific that the variety of Arabic is `ar-QA|(Arabic(Qatar))`. 

##### Locations

In addition to the names of the languages covered by the entry, we need to know where the language creators are primarily located. You may select full *macroscopic areas* such as continents and/or *specific countries/regions*. Please choose all that apply by selecting from the dropdown menus. 

For the *EXAMS QA dataset*, the macroscopic areas would be `Northern Africa`, `Western Asia`, `South-eastern Asia`, and `Europe`, and the specific countries would be `Albania`, `Bulgaria`, `Croatia`, `France`, `Germany`, `Hungary`, `Italy`, `Lithuania`, `North Macedonia`, `Poland`, `Portugal`, `Qatar`, `Spain`, `Serbia`, `Turkey`, and `Vietnam`. This information isn't always documented for processed datasets, so answer based on your best guess or just answer with the macroscopic areas.

#### Entry Representative, Owner, or Custodian

In order to make use of the language data indexed in this entry, we need information about the person or organization that either owns or manages it (data custodian).

Please enter the name of the data custodian in the textbox. From the dropdown box, please select the type of entity you are providing information about. Possible answers include `a private individual`, `a commercial entity`, `a library, museum, or archival institute`, `a university or research institution`, `a nonprofit/NGO`, `a government organization`, and `other`. If you select `other`, please provide a description. 

Select the country, nation, region, or territory where the entity is located or hosted. Please enter the name of a contact person for the entity. The textbox will autopopulate with the name of the entity, but please replace this with the name of an individual if there is a specific person we can direct our query to. If available, please enter an email address that can be used to ask them about using/obtaining their data.

Please select whether you would be willing to contact the entity to ask them about using their data (with support from the BigScience Data Sourcing team). Is yes, please me make sure that your email information is entered in the left sidebar.

If there is a URL where we can find out more information about the data owner/custodian, please add it to the final textbox. For example, please provide the URL of the webpage with their contact information, the homepage of the organization, or even their Wikipedia page if it exists.

For the *EXAMS QA dataset*, the data custodian is Sofia University “St. Kliment Ohridski”, which is `a university or research institution`. The location of the entity is `Bulgaria`. The contact person is `Momchil Hardalov`, whose email is `hardalov@@fmi.uni-sofia.bg`. Additional information on the entity is available in the [publication](https://aclanthology.org/2020.emnlp-main.438.pdf). 

#### Availability of the Resource: Procuring, Licenses, PII

##### Obtaining the data: Online availability and data owner/custodian

Please characterize the availability of the resource with one of four possible answers:
1. Yes - it has a direct download link or links
2. Yes - after signing a user agreement
3. No - but the current owners/custodians have contact information for data queries
4. No - we would need to spontaneously reach out to the current owners/custodians

If yes,then provide the URL where the data can be downloaded. If the data source is a website or collection of files, please provide the top-level URL or location of the file directory. If no, then please provide the email of the person to contact to obtain the data if it is different from the contact email entered for the data custodian in the **Entry Representative, Owner, or Custodian** section.

The answer for *EXAMS QA dataset* is `Yes - it has a direct download link or links`. The data is available to download on the [GitHub repo](https://github.com/mhardalov/exams-qa/tree/main/data/exams).

##### Data licenses and Terms of Service

Please provide as much information as you can find about the data's licensing and terms of use. This information will help us determine whether or not we can use the data in the BigScience dataset, for training the BigScience model, and whether or not we can share the data afterwards. Please respond as to whether or not the language data in the resource come with explicit licenses of terms of use.

If yes, select the option that best characterizes the licensing status of the data: `public domain`, `multiple licenses`, `copyright - all rights reserved`, `open license`, `research use`, `non-commercial use`, or `do not distribute`. Select each of the licenses (if more than one) that the data is shared under. If you select `other`, please copy the text for the license or terms of use into the form. The text may be included in a link to the license webpage. You do not neet to copy the text if it corresponds to one of the established licenses that may be selected.

If there are no licenses or terms of service, or if it is unclear as to what they are, please provide your best assessment of whether the data can be used to train models while respecting the rights and wishes of the data creators and custodians. This field will serve as a starting point for further investigation.

The *EXAMS QA dataset* is under an `open license`, specifically the `CC-BY-SA-4.0 License`. 

##### Personally Identifiable Information

Please provide as much information as you can find about the data's contents related to personally identifiable information. This kind of information will impact the BigScience dataset and model in terms of privacy, security, and social impact. For more information please see **###LINK###**. 

We categorize personally identifiable information into three categories:

1. General
- Personally identifying general information includes names, physical and email addresses, website accounts with names or handles, dates (birth, death, etc.), full-face photographs and comparable images, URLS, and biometric identifiers (fingerprints, voice, etc.). 

2. Numbers
- Personally identifying numbers include information such as telephone numbers, fax numbers, vehicle and device identifiers and serial numbers, social security numbers and equivalent, IP addresses, medical record numbers, health plan beneficiary numbers, account numbers, certificate/license numbers, and any other uniquely identifying numbers.

3. Sensitive
- Sensitive information includes descriptions of racial or ethnic origin, political opinions, religious or philosophical beliefs, trade-union membership, genetic data, health-related data, and data concerning a person's sex life or sexual orientation.

Please select whether the resource contains any of these kinds of personally identifiable or sensitive information: `yes`, `yes - text author name only`, `no`, or `unclear`. Please note that the default answer should be to assume that there is some kind of personally identifiable information in the data.

If yes, please select how likely you believe it to be that the resource contains each kind of personally identifiable or sensitive information from the dropdown boxes: `very likely`, `somewhat likely`, `unlikely`, or `none`. 

If no or unclear, please select your reason for why there may not be personally indetifiable information in the data. Reasons may include that the data only contains general knowledge not written by or referring to private persons, or that the data consists of fictional text. If there is some other reason, please provide justification in the text box.

The *EXAMS QA dataset* contains questions and answers from high school examinations for a number of subjects. It is therefore `very likely` to have names and dates in the history sections, `unlikely` to have any numerical PII, and `somewhat likely` to contain respondents' political opinions and religious or philosophical beliefs in social science sections.

#### Primary Sources of Processed Dataset

Please select whether the language data in the dataset was produced at the time of the dataset creation or whether it was taken from a primary source. 

Select one of the four options to describe the documentation of the dataset's primary sources:
1. Yes - they are fully available
2. Yes - their documentation/homepage/description is available
3. No - the dataset curators describe the primary sources but they are fully private
3. No - the dataset curators kept the source data secret

Describe the kind of data in the primary sources as one of the following sources: `web|wiki`, `web|content repository, archive, or collection`, `web|forum`, `web|news or magazine website`, `web|official website`, `web|social media`, `web|blog`, `web|other`, `books/book publisher`, `scientific articles/journal`, `news articles`, `radio`, `clips`, `movies and documentaries`, `podcasts`, or `other`. 

Select one of the following options to characterize the compatibility of the source material's license or commercial status and the dataset's:
1. Yes - the source material has an open license that allows re-use
2. Yes - the dataset has the same license as the source material
3. Yes - the dataset curators have obtained consent from the source material ownders
4. Unclear/I don't know
5. No - the license of the source material actually prohibits re-use in this manner

The data in the *EXAMS QA dataset* was taken from a primary source. The dataset curators describe the primary sources, but do not make them readily available. The primary sources are official state exams prepared by the ministries of education of various countries, so the category would be `other`. Because the sources are unknown, it's unclear what the licenses of the primary sources are.

#### Media Type, Format, Size, and Processing Needs

##### Media Type

Please provide information about the format of the language data. This information will help us determine what processing will be necessary to include the resource in the BigScience dataset.

Select whether the language data in the resource is primarily text, audiovisual (from either video or audio recordings), or image data. Media data provided with transcription should select text, then select the transcribed option. PDFs that have pre-extracted text information should select text, while PDFs that need OCR should go into images. Select the latter if you're unsure.

If the data is primarily text, please select what format the text is in from the dropdown menu: `plain text`, `HTML`, `PDF`, `XML`, `mediawiki`, or `other`. If `other`, please enter a text description of the format. Select whether the text was transcribed from another media format and, if so, whether that media format was audiovisual or images. Choose the format of the original data from the dropdown menu, if known.

If the data is primarily audiovisual, please select what format the text is in from the dropdown menu: `mp4`, `wav`, `video`, or `other`. If other, please enter a text description of the format.

If the data is primarily images, please select what format the text is in from the dropdown menu: `JPEG`, `PNG`, `PDF`, `TIFF`, or `other`. If other, please enter a text description of the format.

The *EXAMS QA dataset* contains `text` data in `plain text` format. It is not transcribed data.

##### Media Amounts

In order to estimate the amount of data in the dataset or primary source, we need a approximate count of the number of instances and the typical instance size therein. This will help us organize processing and storage requirements. 

Please select what an instance in the resource consists of: `article`, `post`, `dialogue`, `episode`, `book`, or `other`. If other, please enter a text description of an instance. Select an estimate the number of instances in the resource. Finally, select an estimate of the number of words per instance. Select the range that you think best fits the data, even if you are unsure.

The instances in the *EXAMS QA dataset* are `other` with the description being `question`. It has `10K<n<100K` instances, and the number of words per instances is estimated to be `10<n<100`. 

### Adding a Language Organization or Advocate

A language organization or advocate is an organization holding or working on a set of language resources of various types, formats, and languages. Examples include The Internet Archive, The British Library, l'institut national de l'audiovisuel, Wikimedia Foundation, or other libraries, archival institutions, cultural organizations. 

You will be asked to fill in information about the language organization or advocate itself as well as information on how to get in contact with them.

#### Entry Category, Name, ID, Homepage, Description

First, provide a descriptive name for the resource. This should be a human-readable name such as *Creative Commons*. 

In the next box provide a short `snake_case` unique identifier for the resource, for example `creative_commons_org`.

If available, provide a link to the home page for the resource, e.g. https://creativecommons.org/.

Provide a short description of the resource, in a few words to a few sentences. The description will be used to index and navigate the catalogue. 

#### Entry Languages and Locations

For each entry, we need to catalogue which languages are represented or focused on, as characterized by both the language names and the geographical distribution of the language data creators that are served by the language organization or advocate. We use language data creators to refer to those who wrote the text or spoke the speech that we refer to as data, as opposed to those who may have found, formatted, or created metadata and annotations for the data.

##### Languages

Please add all of the languages that are covered by the resource. You may select the language from the dropdown menu or type out the name of the language and submit by hitting enter. This is the higher-level classification of the languages that currently have working groups in the BigScience project. Selecting the Indic and Niger-Congo languages will open a new selection box for the specific language, and selecting Arabic will open a new selection box for the dialect. An additional textbox is available to provide further comments about the language variety. 

You may also click the `Show other languages` button to add languages that are currently not in the BigScience list. Again, you may select the language from the dropdown menu or type out the name of the language and submit by hitting enter.

*Creative Commons* aggregates data from many sources, so for languages you would select all of the top-level languages in the BigScience list: `African languages of the Niger-Congo family`, `Arabic`, `Basque`, `Catalan`, `Chinese`, `English`, `French`, `Indic languages`, `Indonesian`, `Portuguese`, `Spanish`, and `Vietnamese`. In similar cases where it's unclear what languages are covered, add all languages you suspect have at least some content. 

##### Locations

In addition to the names of the languages covered by the entry, we need to know where the language creators are primarily located. You may select full *macroscopic areas* such as continents and/or *specific countries/regions*. Please choose all that apply by selecting from the dropdown menus. 

For *Creative Commons*, the macroscopic area would be `World-Wide`.

#### Entry Representative, Owner, or Custodian

From the dropdown box, please select the type of entity you are providing information about. Possible answers include `a private individual`, `a commercial entity`, `a library, museum, or archival institute`, `a university or research institution`, `a nonprofit/NGO`, `a government organization`, and `other`. If you select `other`, please provide a description. 

Select the country, nation, region, or territory where the entity is located or hosted. Please enter the name of a contact person for the entity. The textbox will autopopulate with the name of the entity, but please replace this with the name of an individual if there is a specific person we can direct our query to. If available, please enter an email address that can be used to ask them about using/obtaining their data.

Please select whether you would be willing to contact the entity to ask them about using their data (with support from the BigScience Data Sourcing team). Is yes, please me make sure that your email information is entered in the left sidebar.

If there is a URL where we can find out more information about the data owner/custodian, please add it to the final textbox. For example, please provide the URL of the webpage with their contact information, the homepage of the organization, or even their Wikipedia page if it exists.

For *Creative Commons*, the type is `a nonprofit/NGO`, the location of the entity is `United States of America`, the contact name is the default `Creative Commons`, the contact email is `info@creativecommons.org` and additional information on the entity is available at `https://search.creativecommons.org/`. 

### Submitting the Form

Thank you for filling out the submission form! Please review your answers, which are visible in the **Review and Save Entry** section at the end of the form in json format, prior to submitting.

To submit the form, please enter a name (or pseudonym) in the left sidebar and click `Save entry to catalogue` in the **Review and Save Entry** section of the form. This will save the entry to the repository. You can also download the entry as a `json` file by clicking the `Download entry dictionary` button at the bottom of the form.

## Explore the Current Catalogue

To view a map of the current entries, select the `Explore the current catalogue` button in the left sidebar of the form. You can zoom in on the map to see the number of resources based on regions and countries. You can also restrict the shown resources based on resource category, language, the data custodian type, and whether the location is that of the data custodian or the data creators.

You can also look at individual entries by going to the **View selected resources** section below the map. You can select specific entries, and restrict that search by location, to view descriptions of the resources.

## Validate an Existing Entry

To get started, please select the `Validate an existing entry` button in the left sidebar of the form and add your name and your email (optional) in the left sidebar. Then proceed to filling out the form. 

You may select an entry to validate, or validate the entry proposed by the form.

**###TODO###**

## Contact Information

If you have any questions or issues with the form, please contact **###TODO###**
