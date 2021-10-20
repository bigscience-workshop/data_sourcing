import simplejson as json
import csv


with open('Sorted resource list - all languages_20211020.csv', newline='') as csvfile:
    source_reader = csv.DictReader(csvfile)
    for row in source_reader:

        source = {
            "uid": f' {row["#"]}_{row["Dataset title"].replace(" ", "_")}',
            "type": "primary",
            "imported": True,
            "description": {
                "name": row["Dataset title"],
                "description": "",
                "homepage": row["Domain Name / link (if highlighted in red, it's a duplicate! So don't add it...)"],
                "validated": False
            },
            "languages": {
                "language_names": row["Language(s) (or family)"].split(','),
                "language_comments": row["Dialect/accent (if known)"],
                "language_locations": [],
                "validated": False
            },
            "custodian": {
                "name": row["Owner"],
                "type": "",
                "location": "",
                "contact_name": "",
                "contact_email": "",
                "contact_submitter": "",
                "additional": "",
                "validated": False
            },
            "availability": {
                "procurement": {
                    "for_download": "Not sure",
                    "download_url": "",
                    "download_email": ""
                },
                "licensing": {
                    "has_licenses": "Yes" if row["License (default is UNKNOWN)"].lower().strip() is not "unknown" else None,
                    "license_text": row["License (default is UNKNOWN)"],
                    "license_properties": [],
                    "license_list": []
                },
                "pii": {
                    "has_pii": "No" if row["Contains Personal Information? (-1=unlikely, 0=neutral, 1=likely)"] == "-1" else "Yes",
                    "generic_pii_likely": "very likely",
                    "generic_pii_list": [],
                    "numeric_pii_likely": "somewhat likely",
                    "numeric_pii_list": [],
                    "sensitive_pii_likely": "very likely",
                    "sensitive_pii_list": [],
                    "no_pii_justification_class": "",
                    "no_pii_justification_text": ""
                },
                "validated": False
            },
            "source_category": {
                "category_type": "",
                "category_web": "",
                "category_media": "",
                "validated": False
            },
            "media": {
                "category": [],
                "text_format": [],
                "audiovisual_format": [],
                "image_format": [],
                "database_format": [],
                "text_is_transcribed": "Yes" if row["Format"] == "spoken" else "No",
                "instance_type": "",
                "instance_count": "",
                "instance_size": "",
                "validated": False
            }
        }

        print(f' {source["uid"]} - {source["description"]["homepage"]} - {source["languages"]["language_names"]}')

        with open(f'./{row["#"]}.json', 'w') as f:
            json.dump(source, f, indent=4 * ' ')

