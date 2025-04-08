import xml.etree.ElementTree as ET
import csv
from tqdm import tqdm
import sys


def xml_to_csv(xml_file, csv_file):
    context = ET.iterparse(xml_file, events=("start", "end"))
    context = iter(context)
    event, root = next(context)  # Get the root element
    total_records = sum(1 for event, elem in ET.iterparse(xml_file) if elem.tag == "record")

    with open(csv_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)

        headers_written = False
        with tqdm(total=total_records, desc="Processing records") as pbar:
            for event, elem in context:
                if event == "end" and elem.tag == "record":
                    if not headers_written:
                        headers = [child.tag for child in elem]
                        csvwriter.writerow(headers)
                        headers_written = True

                    row = [child.text for child in elem]
                    csvwriter.writerow(row)

                    root.clear()
                    pbar.update(1)

filename = sys.argv[1]
output = sys.argv[2] if len(sys.argv) > 1 else filename.replace('.xml', '.csv')
xml_to_csv(xml_file=filename, csv_file=output)