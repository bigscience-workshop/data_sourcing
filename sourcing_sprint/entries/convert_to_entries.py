import simplejson as json
import csv


with open('Sorted resource list - all languages_20211020.csv', newline='') as csvfile:
    source_reader = csv.DictReader(csvfile)
    for row in source_reader:

        source = {
            "uid": f' {row["#"]}_{row["Dataset title"].replace(" ", "_")}',
            "type": "primary",
            "description": {
                "name": row["Dataset title"],
                "description": None,
                "homepage": row["Domain Name / link (if highlighted in red, it's a duplicate! So don't add it...)"],
                "validated": False
            },
            "languages": {
                "language_names": row["Language(s) (or family)"].split(','),
                "language_comments": row["Dialect/accent (if known)"],
                "language_locations": None,
                "validated": False
            },
            "custodian": {
                "name": row["Owner"],
                "type": None,
                "location": None,
                "contact_name": None,
                "contact_email": None,
                "contact_submitter": None,
                "additional": None,
                "validated": False
            },
            "availability": {
                "procurement": {
                    "for_download": None,
                    "download_url": None,
                    "download_email": None
                },
                "licensing": {
                    "has_licenses": "Yes" if row["License (default is UNKNOWN)"].lower().strip() is not "unknown" else None,
                    "license_text": None,
                    "license_properties": None,
                    "license_list": row["License (default is UNKNOWN)"].lower().strip().split(',')
                },
                "pii": {
                    "has_pii": "No" if row["Contains Personal Information? (-1=unlikely, 0=neutral, 1=likely)"] == "-1" else "Yes",
                    "generic_pii_likely": "very likely",
                    "generic_pii_list": None,
                    "numeric_pii_likely": "somewhat likely",
                    "numeric_pii_list": None,
                    "sensitive_pii_likely": "very likely",
                    "sensitive_pii_list": None,
                    "no_pii_justification_class": "",
                    "no_pii_justification_text": ""
                },
                "validated": False
            },
            "source_category": {
                "category_type": None,
                "category_web": None,
                "category_media": None,
                "validated": False
            },
            "media": {
                "category": [
                    row["Format"]
                ],
                "text_format": [],
                "audiovisual_format": [],
                "image_format": [],
                "text_is_transcribed": "Yes" if row["Format"] == "spoken" else "No",
                "instance_type": None,
                "instance_count": None,
                "instance_size": None,
                "validated": False
            }
        }

        print(f' {source["uid"]} - {source["description"]["homepage"]} - {source["languages"]["language_names"]}')

        with open(f'./{row["#"]}.json', 'w') as f:
            json.dump(source, f, indent=4 * ' ')

