import json
import xml.etree.ElementTree as ET
import requests
import os
import uuid  # Added for GUID generation

# Fetch the language mapping data from GitHub
url = "https://raw.githubusercontent.com/IWLeng/Scripts/main/json_to_xml_analysis_converter/lang_mapping/lang_mapping_library.py"
response = requests.get(url)
mapping_data = response.text

# Extract the lang_mapping_library dictionary from the fetched data
temp_dict = {}
exec(mapping_data, temp_dict)

# Access the lang_mapping_library dictionary
lang_mapping_library = temp_dict.get("lang_mapping_library", {})

# Convert the lang_mapping_library keys to lowercase for case-insensitive matching
lang_mapping_library = {k.lower(): v for k, v in lang_mapping_library.items()}

# Prompt the user to input the path where JSON files are located
input_path = input("Enter the path to the directory containing JSON files: ")

# Ensure the input path exists
if not os.path.exists(input_path):
    print(f"The path '{input_path}' does not exist.")
    exit()

# Get all JSON files in the directory
json_files = [f for f in os.listdir(input_path) if f.endswith('.json')]

if not json_files:
    print(f"No JSON files found in '{input_path}'.")
    exit()

# Process each JSON file
for json_file in json_files:
    # Construct the full path to the JSON file
    json_file_path = os.path.join(input_path, json_file)

    # Load the JSON data from the file
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Create the root element for the XML
    root = ET.Element("task", name="analyse")

    # Create the taskInfo element and populate it
    task_info = ET.SubElement(root, "taskInfo", taskId="aa0a0a00-aa0a-0000-0000-0a0a000aa000", runAt=data['dateCreated'], runTime="Less than 1 second")
    project = ET.SubElement(task_info, "project", name=data['projectName'], number="aa0a0a00-aa0a-0000-0000-0a0a000aa000")

    # Extract data from analyseLanguageParts
    for part in data['analyseLanguageParts']:
        target_lang = part['targetLang']
        
        # Convert target_lang to lowercase for case-insensitive matching
        target_lang_lower = target_lang.lower()
        
        # Map the language name and LCID using the fetched mapping data
        lang_info = lang_mapping_library.get(target_lang_lower, {"name": target_lang, "lcid": ""})
        language_name = lang_info["name"]
        lcid = lang_info["lcid"]
        
        language = ET.SubElement(task_info, "language", lcid=str(lcid), name=language_name)
        settings = ET.SubElement(task_info, "settings", reportInternalFuzzyLeverage="no", reportLockedSegmentsSeparately="no", reportCrossFileRepetitions="no", presentIndividualFileDetails="no", minimumMatchScore="75", searchMode="n/a", missingFormattingPenalty="0", differentFormattingPenalty="0", multipleTranslationsPenalty="0", autoLocalizationPenalty="0", textReplacementPenalty="0", alignmentPenalty="0", characterWidthDifferencePenaltyEnabled="no", characterWidthDifferencePenalty="0", enableFuzzyMatchRepair="no", enableMtFuzzyMatchRepair="no", fullRecallMatchedWords="n/a", partialRecallMatchedWords="n/a", fullRecallSignificantWords="n/a", partialRecallSignificantWords="n/a", optimizedPerformance="no")

        # Extract data from each job and create <file> elements
        for job in part['jobs']:
            file_name = job['fileName']
            job_data = job['data']

            # Create the <file> element with a random GUID
            file_element = ET.SubElement(root, "file", name=file_name, guid=str(uuid.uuid4()))

            # Create the <analyse> element under <file>
            analyse = ET.SubElement(file_element, "analyse")

            # Populate the <analyse> element with data
            ET.SubElement(analyse, "perfect", segments=str(job_data['contextMatch']['segments']), words=str(job_data['contextMatch']['words']), characters=str(job_data['contextMatch']['characters']), placeables="0", tags="0", repairWords="0", fullRecallWords="0", partialRecallWords="0")
            ET.SubElement(analyse, "inContextExact", segments="0", words="0", characters="0", placeables="0", tags="0", repairWords="0", fullRecallWords="0", partialRecallWords="0")
            ET.SubElement(analyse, "exact", segments=str(job_data['match100']['segments']['sum']), words=str(job_data['match100']['words']['sum']), characters=str(job_data['match100']['characters']['sum']), placeables="0", tags="0", repairWords="0", fullRecallWords="0", partialRecallWords="0")
            ET.SubElement(analyse, "locked", segments="0", words="0", characters="0", placeables="0", tags="0", repairWords="0", fullRecallWords="0", partialRecallWords="0")
            ET.SubElement(analyse, "crossFileRepeated", segments="0", words="0", characters="0", placeables="0", tags="0", repairWords="0", fullRecallWords="0", partialRecallWords="0")
            ET.SubElement(analyse, "repeated", segments=str(job_data['repetitions']['segments']), words=str(job_data['repetitions']['words']), characters=str(job_data['repetitions']['characters']), placeables="0", tags="0", repairWords="0", fullRecallWords="0", partialRecallWords="0")
            ET.SubElement(analyse, "total", segments=str(job_data['total']['segments']), words=str(job_data['total']['words']), characters=str(job_data['total']['characters']), placeables="0", tags="0", repairWords="0", fullRecallWords="0", partialRecallWords="0")
            ET.SubElement(analyse, "new", segments=str(job_data['match0']['segments']['sum']), words=str(job_data['match0']['words']['sum']), characters=str(job_data['match0']['characters']['sum']), placeables="0", tags="0", repairWords="0", fullRecallWords="0", partialRecallWords="0")
            ET.SubElement(analyse, "fuzzy", min="50", max="74", segments=str(job_data['match50']['segments']['sum']), words=str(job_data['match50']['words']['sum']), characters=str(job_data['match50']['characters']['sum']), placeables="0", tags="0", repairWords="0", fullRecallWords="0", partialRecallWords="0")
            ET.SubElement(analyse, "fuzzy", min="75", max="84", segments=str(job_data['match75']['segments']['sum']), words=str(job_data['match75']['words']['sum']), characters=str(job_data['match75']['characters']['sum']), placeables="0", tags="0", repairWords="0", fullRecallWords="0", partialRecallWords="0")
            ET.SubElement(analyse, "fuzzy", min="85", max="94", segments=str(job_data['match85']['segments']['sum']), words=str(job_data['match85']['words']['sum']), characters=str(job_data['match85']['characters']['sum']), placeables="0", tags="0", repairWords="0", fullRecallWords="0", partialRecallWords="0")
            ET.SubElement(analyse, "fuzzy", min="95", max="99", segments=str(job_data['match95']['segments']['sum']), words=str(job_data['match95']['words']['sum']), characters=str(job_data['match95']['characters']['sum']), placeables="0", tags="0", repairWords="0", fullRecallWords="0", partialRecallWords="0")

        # Create the <batchTotal> element
        batch_total = ET.SubElement(root, "batchTotal")
        analyse_batch = ET.SubElement(batch_total, "analyse")

        # Populate the <batchTotal> element with data from analyseLanguageParts
        part_data = part['data']
        ET.SubElement(analyse_batch, "perfect", segments=str(part_data['contextMatch']['segments']), words=str(part_data['contextMatch']['words']), characters=str(part_data['contextMatch']['characters']), placeables="0", tags="0", repairWords="0", fullRecallWords="0", partialRecallWords="0")
        ET.SubElement(analyse_batch, "inContextExact", segments="0", words="0", characters="0", placeables="0", tags="0", repairWords="0", fullRecallWords="0", partialRecallWords="0")
        ET.SubElement(analyse_batch, "exact", segments=str(part_data['match100']['segments']['sum']), words=str(part_data['match100']['words']['sum']), characters=str(part_data['match100']['characters']['sum']), placeables="0", tags="0", repairWords="0", fullRecallWords="0", partialRecallWords="0")
        ET.SubElement(analyse_batch, "locked", segments="0", words="0", characters="0", placeables="0", tags="0", repairWords="0", fullRecallWords="0", partialRecallWords="0")
        ET.SubElement(analyse_batch, "crossFileRepeated", segments="0", words="0", characters="0", placeables="0", tags="0", repairWords="0", fullRecallWords="0", partialRecallWords="0")
        ET.SubElement(analyse_batch, "repeated", segments=str(part_data['repetitions']['segments']), words=str(part_data['repetitions']['words']), characters=str(part_data['repetitions']['characters']), placeables="0", tags="0", repairWords="0", fullRecallWords="0", partialRecallWords="0")
        ET.SubElement(analyse_batch, "total", segments=str(part_data['total']['segments']), words=str(part_data['total']['words']), characters=str(part_data['total']['characters']), placeables="0", tags="0", repairWords="0", fullRecallWords="0", partialRecallWords="0")
        ET.SubElement(analyse_batch, "new", segments=str(part_data['match0']['segments']['sum']), words=str(part_data['match0']['words']['sum']), characters=str(part_data['match0']['characters']['sum']), placeables="0", tags="0", repairWords="0", fullRecallWords="0", partialRecallWords="0")
        ET.SubElement(analyse_batch, "fuzzy", min="50", max="74", segments=str(part_data['match50']['segments']['sum']), words=str(part_data['match50']['words']['sum']), characters=str(part_data['match50']['characters']['sum']), placeables="0", tags="0", repairWords="0", fullRecallWords="0", partialRecallWords="0")
        ET.SubElement(analyse_batch, "fuzzy", min="75", max="84", segments=str(part_data['match75']['segments']['sum']), words=str(part_data['match75']['words']['sum']), characters=str(part_data['match75']['characters']['sum']), placeables="0", tags="0", repairWords="0", fullRecallWords="0", partialRecallWords="0")
        ET.SubElement(analyse_batch, "fuzzy", min="85", max="94", segments=str(part_data['match85']['segments']['sum']), words=str(part_data['match85']['words']['sum']), characters=str(part_data['match85']['characters']['sum']), placeables="0", tags="0", repairWords="0", fullRecallWords="0", partialRecallWords="0")
        ET.SubElement(analyse_batch, "fuzzy", min="95", max="99", segments=str(part_data['match95']['segments']['sum']), words=str(part_data['match95']['words']['sum']), characters=str(part_data['match95']['characters']['sum']), placeables="0", tags="0", repairWords="0", fullRecallWords="0", partialRecallWords="0")

    # Create an ElementTree object and write to file
    tree = ET.ElementTree(root)
    output_file_name = os.path.splitext(json_file)[0] + ".xml"
    output_file_path = os.path.join(input_path, output_file_name)
    tree.write(output_file_path, encoding="utf-8", xml_declaration=False)

    print(f"Processed '{json_file}' -> '{output_file_name}'")

print("Batch processing complete.")
