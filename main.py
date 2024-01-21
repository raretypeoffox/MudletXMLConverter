import os
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

FILE = 'sample.xml'
# FILE = 'artemis.xml'



tree = ET.parse(FILE)
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
    

def add_to_order(text, depth):
    for i in range(depth):
        text = ' ' + text
    Order.append(text)
    


def build_filestructure(element_dict, parent_dir='', package_dir='', depth=0):
    # If the element is a HostPackage, create a .json file for it
    if element_dict['tag'] == 'HostPackage':
        os.makedirs('MudletPackage', exist_ok=True)
        json_path = os.path.join('MudletPackage', 'HostPackage.json')
        with open(json_path, 'w') as file:
            # Write the tags and children to the JSON file
            json.dump({**element_dict['attributes'], 'children': element_dict['children']}, file)

    
    element = ET.Element(element_dict['tag'], element_dict['attributes'])

    # Set the element's text content
    if element_dict['text']:
        element.text = element_dict['text']
        
    # If the element is a TriggerGroup (or AliasGroup, ScriptGroup, KeyGroup),
    # and it has a name, create a new directory for it
    group_types = ['TriggerGroup', 'TimerGroup', 'AliasGroup', 'ScriptGroup', 'KeyGroup']
    if element_dict['tag'] in group_types:
        for child in element_dict['children']:
            if child['tag'] == 'name':
                # Determine the correct package directory based on the group type
                package_dir = element_dict['tag'].replace('Group', 'Package')
                # Replace forward slashes in the directory name
                dir_name = f"{child['text'].replace('/', '_S_').replace('*', '_A_').replace('?', '_Q_').replace('<', '_LT_').replace('>', '_GT_').replace('|', '_P_').replace('"', '_DQ_').rstrip('.')}"
                # Create the new directory
                new_dir = os.path.join('MudletPackage', package_dir, parent_dir, dir_name)
                os.makedirs(new_dir, exist_ok=True)
                add_to_order(child['text'], depth)
                # Update the parent directory for the next level of recursion
                parent_dir = os.path.join(parent_dir, dir_name)
                break

    # If the element is a Trigger, Alias, Script, or Key, create a .lua file for it
    element_types = ['Trigger', 'Timer', 'Alias', 'Script', 'Key']
    if element_dict['tag'] in element_types:
        for child in element_dict['children']:
            if child['tag'] == 'name':
                # Replace forward slashes in the filename
                filename = f"{child['text'].replace('/', '_S_').replace('*', '_A_').replace('?', '_Q_').replace('<', '_LT_').replace('>', '_GT_').replace('|', '_P_').replace('"', '_DQ_').rstrip('.')}"
                # Create the .lua file
                file_path = os.path.join('MudletPackage', package_dir, parent_dir, filename + '.lua')
                with open(file_path, 'w', encoding='utf-8') as file:
                    # Write the contents of the <script> element to the file
                    for script_child in element_dict['children']:
                        if script_child['tag'] == 'script' and script_child['text'] is not None:
                            file.write(script_child['text'])
                            break

                # Create the .json file
                json_path = os.path.join('MudletPackage', package_dir, parent_dir, filename + '.json')
                with open(json_path, 'w', encoding='utf-8') as file:
                    # Write the other tags to the JSON file
                    json.dump({k: v for k, v in element_dict.items() if k != 'children'}, file)
                add_to_order(child['text'], depth)

    # Recursively reconstruct each child element and add it to the current element
    for child_dict in element_dict['children']:
        child_element = build_filestructure(child_dict, parent_dir, package_dir, depth + 1)
        element.append(child_element)

    return element

Order = []

build_filestructure(root_dict, '')

with open('order.txt', 'w') as f:
    for item in Order:
        f.write("%s\n" % item)