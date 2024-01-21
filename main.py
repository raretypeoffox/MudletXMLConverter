import os
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

tree = ET.parse('sample.xml')
root = tree.getroot()

def iterate_children(element, depth=0):
    # Create a dictionary to hold the element's information
    element_dict = {
        'tag': element.tag,
        'attributes': element.attrib,
        'text': element.text,
        'children': [],
        'depth': depth
    }

    # Recursively iterate over each child element, increasing the depth
    for child in element:
        child_dict = iterate_children(child, depth + 1)
        element_dict['children'].append(child_dict)

    return element_dict

# Start iterating from the root
root_dict = iterate_children(root)

# Write the dictionary to a file in JSON format
with open('log.json', 'w') as f:
    json.dump(root_dict, f, indent=4)
 
    
    
def reconstruct_element(element_dict):
    # Create a new element with the tag and attributes from the dictionary
    element = ET.Element(element_dict['tag'], element_dict['attributes'])

    # Set the element's text content
    if element_dict['text']:
        element.text = element_dict['text']

    # Recursively reconstruct each child element and add it to the current element
    for child_dict in element_dict['children']:
        child_element = reconstruct_element(child_dict)
        element.append(child_element)

    # Add a newline after every closed bracket
    if element_dict['children']:
        element.tail = '\n' + '    ' * element_dict['depth']

    return element

def reconstruct():
    # Load the dictionary from the JSON file
    with open('log.json', 'r') as f:
        root_dict = json.load(f)

    # Reconstruct the root element from the dictionary
    root = reconstruct_element(root_dict)

    # Create an ElementTree from the root element
    tree = ET.ElementTree(root)

    # Convert the ElementTree to a string
    xml_string = ET.tostring(root, encoding='unicode')

    # Parse the XML string with minidom and format it with toprettyxml
    pretty_xml = minidom.parseString(xml_string).toprettyxml(indent='    ')

    # Write the formatted XML to a file
    with open('reconstructed.xml', 'w') as f:
        f.write(pretty_xml)
    


def build_filestructure(element_dict, parent_dir='', package_dir=''):
    # Create a new element with the tag and attributes from the dictionary
    element = ET.Element(element_dict['tag'], element_dict['attributes'])

    # Set the element's text content
    if element_dict['text']:
        element.text = element_dict['text']

    # If the element is a TriggerGroup (or AliasGroup, ScriptGroup, KeyGroup),
    # and it has a name, create a new directory for it
    group_types = ['TriggerGroup', 'AliasGroup', 'ScriptGroup', 'KeyGroup']
    if element_dict['tag'] in group_types:
        for child in element_dict['children']:
            if child['tag'] == 'name':
                # Determine the correct package directory based on the group type
                package_dir = element_dict['tag'].replace('Group', 'Package')
                # Create the new directory
                new_dir = os.path.join('MudletPackage', package_dir, parent_dir, child['text'])
                os.makedirs(new_dir, exist_ok=True)
                # Update the parent directory for the next level of recursion
                parent_dir = os.path.join(parent_dir, child['text'])
                break

    # If the element is a Trigger, Alias, Script, or Key, create a .lua file for it
    element_types = ['Trigger', 'Alias', 'Script', 'Key']
    if element_dict['tag'] in element_types:
        for child in element_dict['children']:
            if child['tag'] == 'name':
                # Create the .lua file
                file_path = os.path.join('MudletPackage', package_dir, parent_dir, child['text'] + '.lua')
                with open(file_path, 'w') as file:
                    # Write the contents of the <script> element to the file
                    for script_child in element_dict['children']:
                        if script_child['tag'] == 'script' and script_child['text'] is not None:
                            file.write(script_child['text'])
                            break
                break

    # Recursively reconstruct each child element and add it to the current element
    for child_dict in element_dict['children']:
        child_element = build_filestructure(child_dict, parent_dir, package_dir)
        element.append(child_element)

    return element

build_filestructure(root_dict, '')