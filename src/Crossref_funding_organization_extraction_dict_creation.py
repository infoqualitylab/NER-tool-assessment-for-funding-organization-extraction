import csv
import xml
import xml.etree.ElementTree as ET
from string import ascii_lowercase as alph

## create dictionary for sorted searching of orga, names
def funder_dictionary_creation(filename):
    # create empty dict with list for every character in alphabet, one "other" label for non-standard first characters (e.g. Chinese names)
    tree = ET.parse(filename)
    root = tree.getroot()
    orga_dict = {}
    for c in alph:
        orga_dict[c] = []
        if c=="z":
            orga_dict['other'] = []

    for orga in range(2,31552):
        names = []

        # iterate through entries in each organization and check whether the tag is interesting
        for entry in root[orga]:

            #print(entry)
            if entry.tag == '{http://www.w3.org/2008/05/skos-xl#}prefLabel' or entry.tag == '{http://www.w3.org/2008/05/skos-xl#}altLabel':

                orga_name = entry[0][0].text.lower()
                #print(orga_name)
                #print(orga_name[0])
                if orga_name[0] in alph:
                    orga_dict[orga_name[0]] == orga_dict[orga_name[0]].append(orga_name)
                else:
                    orga_dict['other'].append(orga_name)

    w = csv.writer(open("crossref_organizations_sorted_dict.csv", "w", encoding='utf-8', newline=''), delimiter='|')
    for letter,orgs in orga_dict.items():
        w.writerow([letter,list(orgs)])

    return orga_dict