# Guide to Submitting Sources to the BigScience Data Sourcing Hackathon

## Table of Contents
* [Getting Started](#getting-started)
* [Loading the Form](#loading-the-form)
* [Adding a New Entry](#adding-a-new-entry)
  * [Adding a Primary Source](#adding-a-primary-source)
    * [Name, ID, Homepage, Description](#name-id-homepage-description)
    * [Languages and Locations](#languages-and-locations)
    * [Primary Source Availability](#primary-source-availability)
    * [Primary Source Type](#primary-source-type)
    * [Media Type, Format, Size, and Processing Needs](#media-type-format-size-and-processing-needs)
  * [Adding a Processed Dataset](#adding-a-processed-dataset)
    * [Name, ID, Homepage, Description](#name-id-homepage-description-1)
    * [Languages and Locations](#languages-and-locations-1)
    * [Processed Dataset Availability](#processed-dataset-availability)
    * [Primary Sources of Processed Dataset](#primary-sources-of-processed-dataset)
  * [Adding a Partner Organization](#adding-a-partner-organization)
    * [Name, ID, Homepage, Description](#name-id-homepage-description-2)
    * [Languages and Locations](#languages-and-locations-2)
    * [Partner Information](#partner-information)
  * [Submitting the Form](#submitting-the-form)
* [Explore the Current Catalogue](#explore-the-current-catalogue)
* [Validate an Existing Entry](#validate-an-existing-entry)
* [Contact Information](#contact-information)

## Getting Started

Thank you for participating in the BigScience Data Sourcing hackathon! Please use this guide as you submit information about potential data sources for the BigScience dataset using the form.

## Loading the Form

To load the form **###TODO###**

## Adding a New Entry

To get started, please add your name, add your email (optional), and select the type of resource you would like to add in the left-hand column. Then proceed to filling out the form. 

For the purposes of this work, we're organizing resources into three categories: primary source, processed dataset, and partner organization. Select the type of resource you are providing information for in the **General Information** subsection of the **Name, ID, Homepage, Description** section of the form.

### Adding a Primary Source

A primary source is a single source of language data (text or speech), such as a newspaper, radio, website, book collection, etc. 

You will be asked to fill in information about the availability of the source, its properties including availability and presence of personal information, its owners or producers, and the format of the language data.

#### Name, ID, Homepage, Description

First, provide a descriptive name for the resource. This should be a human-readable name such as *Le Monde newspaper*. 

In the next box provide a short `snake_case` unique identifier for the resource, for example `le_monde_primary`.

If available, provide a link to the home page for the resource e.g. https://www.lemonde.fr/.

Provide a short description of the resource, in a few words to a few sentences. The description will be used to index and navigate the catalogue. 

#### Languages and Locations

**Languages**

Please add all of the languages that are covered by the resource. For each additional language, click the `Add Language` checkbox and select the language from the dropdown menu. This is the higher-level classification of the languages that currently have working groups in the BigScience project, so selecting the Indic and Niger-Congo languages will open a new selection box for the specific language. 

**Locations**

For the location of the resource, select the country where the resource or organization itself located or hosted. For example, where is the *website hosted*, what is the physical *location of the library*, etc.?

Additionally, please select all of the countries where the data creators represented in the source are from. For example, where are the *people who write on the website* hosted, where are the *media managed by the library* from?

#### Primary Source Availability

**Obtaining the data: Online availability and data owner/custodian**

Please characterize the availability of the resource with one of four possible answers:
1. Yes - it has a direct download link or links
2. Yes - after signing a user agreement
3. No - but the current owners/custodians have contact information for data queries
4. No - we would need to spontaneously reach out to the current owners/custodians

Then provide the URL where the data can be downloaded if yes. If the data source is a website or collection of files, please provided the top-level URL or location of the file directory.

From the dropdown box, please select the type of entity that the data is owned or managed by and enter the entity's name. If available, please enter an email address that can be used to ask them about using/obtaining their data.

Please select whether you would be willing to contact the entity to ask them about using their data (with support from the BigScience Data Sourcing team). Is yes, please me make sure that your email information is entered in the left sidebar.

If there is a URL where we can find out more information about the data owner/custodian, please add it to the final textbox. For example, please provide the URL of the web page with their contact information, the homepage of the organization, or even their Wikipedia page if it exists.

**Data licenses and Terms of Service**

Please provide as much information as you can find about the data's licensing and terms of use. Please respond as to whether or not the language data in the resource come with explicit licenses of terms of use.

If yes, please copy the text for the license or terms of use into the form. Select each of the licenses (if more than one) that the data is shared under. Mark the `Add license n` checkbox if more than one license should be added.

If there are no licenses or terms of service, or if it is unclear as to what they are, **###TODO###**

**Personally Identifiable Information**

Please provide as much information as you can find about the data's contents related to personally identifiable information. This kind of information will impact the BigScience dataset and model in terms of privacy, security, and social impact. For more information please see **###LINK###**. 

We categorize personally identifiable information into three categories:

1. General
- Personally identifying general information includes names, physical and email addresses, website accounts with names or handles, dates (birth, death, etc.), full-face photographs and comparable images, URLS, and biometric identifiers (fingerprints, voice, etc.). 

2. Numbers
- Personally identifying numbers include information such as telephone numbers, fax numbers, vehicle and device identifiers and serial numbers, social security numbers and equivalent, IP addresses, medical record numbers, health plan beneficiary numbers, account numbers, certificate/license numbers, and any other uniquely identifying numbers.

3. Sensitive
- Sensitive information includes descriptions of racial or ethnic origin, political opinions, religious or philosophical beliefs, trade-union membership, genetic data, health-related data, and data concerning a person's sex life or sexual orientation.

Please select whether the resource contains any of these kinds of personally identifiable or sensitive information. 

If yes, please select what kinds from the dropdown boxes. The default answer should be to assume that there is some kind of personally identifiable information in the data.

If no or unclear, please select your reason for why there may not be personally indetifiable information in the data. Reasons may include that the data only contains general knowledge not written by or referring to private persons, or that the data consists of fictional text. If there is some other reason, please provide justification in the text box.

#### Primary Source Type

Please provide a description for the type of resource. We provide two possible types:

1. Collection
- Collections may contain books or book publishers, scientific articles and journals, newspapers, radio programs, clips, movies and documentaries, or podcasts. Other kinds of data collections may also be included. To add a new category, select `other` from the Collection dropdown menu, and add a description in the textbox. 

2. Website
- Websites may include social media, forums, news or magazine websites, wikis, blogs, official websites, or content repositories, archies, and collections. Other kinds of websites may also be included. To add a new category, select `other` from the Collection dropdown menu, and add a description in the textbox. 

If neither of these options appropriately describes the resource, please select `other` and add a description of the resource. 

#### Media Type, Format, Size, and Processing Needs

**Media Type**

Please provide information about the format of the language data. Select whether the language data in the resource is primarily text, audiovisual (from either video or audio recordings), or image data. Media data provided with transcription should select text, then select the transcribed option. PDFs that have pre-extracted text information should select text, while PDFs that need OCR should go into images. Select the latter if you're unsure.

If the data is primarily text, please select what format the text is in from the dropdown menu: plain text, HTML, PDF, XML, mediawiki, or other. If other, please enter a text description of the format. Select whether the text was transcribed from another media format and, if so, whether that media format was audiovisual or images.

If the data is primarily audiovisual, please select what format the text is in from the dropdown menu: mp4, wav, video, or other. If other, please enter a text description of the format.

If the data is primarily images, please select what format the text is in from the dropdown menu: JPEG, PNG, PDF, TIFF, or other. If other, please enter a text description of the format.

**Media Amounts**

Please estimate the amount of data in the dataset. Include an estimate of the number of instances in the resource as well as a description of what an instance consists of. This may include sentences, posts, or larger units such as paragraphs. Finally, include an estimate of the number of words per instance.

### Adding a Processed Dataset

A processed NLP dataset contains language data that can be used for language modeling. These resources are derived from one or several other primary sources. For example, the CNN/Dailymail summarization dataset is derived from the CNN and Dailymail websites. 

You will be asked to fill in information about the dataset object itself as well as the primary sources it was derived from.

#### Name, ID, Homepage, Description

First, provide a descriptive name for the resource. This should be a human-readable name such as *EXAMS QA dataset*. 

In the next box provide a short `snake_case` unique identifier for the resource, for example `exams_dataset`.

If available, provide a link to the home page for the resource, e.g. https://github.com/mhardalov/exams-qa.

Provide a short description of the resource, in a few words to a few sentences. The description will be used to index and navigate the catalogue. 

#### Languages and Locations

**Languages**

Please add all of the languages that are covered by the resource. For each additional language, click the `Add Language` checkbox and select the language from the dropdown menu. This is the higher-level classification of the languages that currently have working groups in the BigScience project, so selecting the Indic and Niger-Congo languages will open a new selection box for the specific language. 

**Locations**

For the location of the resource, select the country where the resource or organization itself located or hosted. For example, where is the *website hosted*, what is the physical *location of the library*, etc.?

Additionally, please select all of the countries where the data creators represented in the source are from. For example, where are the *people who write on the website* hosted, where are the *media managed by the library* from?

#### Processed Dataset Availability

**Obtaining the data: Online availability and data owner/custodian**

Please characterize the availability of the resource with one of four possible answers:
1. Yes - it has a direct download link or links
2. Yes - after signing a user agreement
3. No - but the current owners/custodians have contact information for data queries
4. No - we would need to spontaneously reach out to the current owners/custodians

Then provide the URL where the data can be downloaded if yes. If the data source is a website or collection of files, please provided the top-level URL or location of the file directory.

From the dropdown box, please select the type of entity that the data is owned or managed by and enter the entity's name. If available, please enter an email address that can be used to ask them about using/obtaining their data.

Please select whether you would be willing to contact the entity to ask them about using their data (with support from the BigScience Data Sourcing team). Is yes, please me make sure that your email information is entered in the left sidebar.

If there is a URL where we can find out more information about the data owner/custodian, please add it to the final textbox. For example, please provide the URL of the web page with their contact information, the homepage of the organization, or even their Wikipedia page if it exists.

**Data licenses and Terms of Service**

Please provide as much information as you can find about the data's licensing and terms of use. Please respond as to whether or not the language data in the resource come with explicit licenses of terms of use.

If yes, please copy the text for the license or terms of use into the form. Select each of the licenses (if more than one) that the data is shared under. Mark the `Add license n` checkbox if more than one license should be added.

If there are no licenses or terms of service, or if it is unclear as to what they are, **###TODO###**

**Personally Identifiable Information**

Please provide as much information as you can find about the data's contents related to personally identifiable information. This kind of information will impact the BigScience dataset and model in terms of privacy, security, and social impact. For more information please see **###LINK###**. 

We categorize personally identifiable information into three categories:

1. General
- Personally identifying general information includes names, physical and email addresses, website accounts with names or handles, dates (birth, death, etc.), full-face photographs and comparable images, URLS, and biometric identifiers (fingerprints, voice, etc.). 

2. Numbers
- Personally identifying numbers include information such as telephone numbers, fax numbers, vehicle and device identifiers and serial numbers, social security numbers and equivalent, IP addresses, medical record numbers, health plan beneficiary numbers, account numbers, certificate/license numbers, and any other uniquely identifying numbers.

3. Sensitive
- Sensitive information includes descriptions of racial or ethnic origin, political opinions, religious or philosophical beliefs, trade-union membership, genetic data, health-related data, and data concerning a person's sex life or sexual orientation.

Please select whether the resource contains any of these kinds of personally identifiable or sensitive information. 

If yes, please select what kinds from the dropdown boxes. The default answer should be to assume that there is some kind of personally identifiable information in the data.

If no or unclear, please select your reason for why there may not be personally indetifiable information in the data. Reasons may include that the data only contains general knowledge not written by or referring to private persons, or that the data consists of fictional text. If there is some other reason, please provide justification in the text box.

#### Primary Sources of Processed Dataset

If available, please provide a link to the documentation for the primary sources of the dataset.

If documentation is not available, please provide a description for each type of primary source in the resource. We provide two possible types:

1. Collection
- Collections may contain books or book publishers, scientific articles and journals, newspapers, radio programs, clips, movies and documentaries, or podcasts. Other kinds of data collections may also be included. To add a new category, select `other` from the Collection dropdown menu, and add a description in the textbox. 

2. Website
- Websites may include social media, forums, news or magazine websites, wikis, blogs, official websites, or content repositories, archies, and collections. Other kinds of websites may also be included. To add a new category, select `other` from the Collection dropdown menu, and add a description in the textbox. 

If neither of these options appropriately describes one of the primary sources, please select `other` and add a description of the primary source. 

### Adding a Partner Organization

A partner organization is an organization holding a set of resources and datasets of various types, formats, languages and/or with various degrees of availability. Examples include The Internet Archive, The British Library, l'institut national de l'audiovisuel, Wikimedia Foundation, or other libraries, archival institutions, cultural organizations. 

You will be asked to fill in information about the partner organization itself as well as information on how to get in contact with them.

#### Name, ID, Homepage, Description

First, provide a descriptive name for the resource. This should be a human-readable name such as *Creative Commons*. 

In the next box provide a short `snake_case` unique identifier for the resource, for example `creative_commons_org`.

If available, provide a link to the home page for the resource, e.g. https://creativecommons.org/.

Provide a short description of the resource, in a few words to a few sentences. The description will be used to index and navigate the catalogue. 

#### Languages and Locations

**Languages**

Please add all of the languages that are covered by the resource. For each additional language, click the `Add Language` checkbox and select the language from the dropdown menu. This is the higher-level classification of the languages that currently have working groups in the BigScience project, so selecting the Indic and Niger-Congo languages will open a new selection box for the specific language. 

**Locations** 

For the location of the resource, select the country where the resource or organization itself located or hosted. For example, where is the *website hosted*, what is the physical *location of the library*, etc.?

Additionally, please select all of the countries where the data creators represented in the source are from. For example, where are the *people who write on the website* hosted, where are the *media managed by the library* from?

#### Partner Information

From the dropdown box, please select the type of entity you are providing information about and enter the entity's name. If available, please enter an email address that can be used to ask them about using/obtaining their data.

Please select whether you would be willing to contact the entity to ask them about using their data (with support from the BigScience Data Sourcing team). Is yes, please me make sure that your email information is entered in the left sidebar.

If there is a URL where we can find out more information about the data owner/custodian, please add it to the final textbox. For example, please provide the URL of the web page with their contact information, the homepage of the organization, or even their Wikipedia page if it exists.

### Submitting the Form

Thank you for filling out the submission form! Please review your answers, which are visible in the right sidebar in json format, prior to submitting.

To submit the form, please **###TODO###**

## Explore the Current Catalogue

**###TODO###**

## Validate an Existing Entry

**###TODO###**

## Contact Information

If you have any questions or issues with the form, please contact **###TODO###**
