
# coding: utf-8

# # CITY - NEW_DELHI(INDIA)
# 
# New Delhi is the capital of INDIA and It is the one of the most popular city in India and have a large amount of cultural diversity. My main reason for choosing this city is that i'm living here from past 4 years so I know this city and it would be easier for me to audit and clean data in here.

# Link for map :- https://www.openstreetmap.org/export#map=12/28.5639/77.1450&layers=DG

# ## Sample File

# My original osm file is so large that it takes so much time in executing thats why I made a mini_sample file from original file which takes some sample values from the original file and its purpose it to check the functionality of my codes.

# In[3]:

import xml.etree.cElementTree as ET  # Use cElementTree or lxml if too slow
import pprint

OSM_FILE = r"C:\Users\MAVERICK\delhi\new-delhi_india.osm"  #original osm file

SAMPLE_FILE = r"C:\Users\MAVERICK\delhi\mini_sample1.osm"        #sample osm file

k = 30 # Parameter: take every k-th top level element

def get_element(osm_file, tags=('node', 'way', 'relation')):
    
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


with open(SAMPLE_FILE, 'wb') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n')

    # Write every kth top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))
            
    output.write('</osm>')
print("code finished")


# ### Auditing Street Names

# There may be so many street names that are overabbreviated , mis-spelled or having different name than expected. So here we will find all those street names and then clean it later.

# In[4]:

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

osm_file = r"C:\Users\MAVERICK\delhi\mini_sample1.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE) # regular expression to match the last word of a string 
street_types=defaultdict(set) 

#creating a list of street types              
expected = ["Street", "Extension", "Enclave", "Town", "Block","Marg","Drive", "Place", "Square", "Lane", "Road","Path" ,
            "Basti", "Park","Phase","World","Lake","Nagar","Circle","Centre","Society","Kunj","Vihar",
            "Centre","Colony","Mall","Bazaar","Plaza","Stop","Stage","Station","Area","Annexe","City","Ridge","Apartment"]

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name) # searches the last word in street name 
    if m:
        street_type = m.group() # groups for specific street types 
        if street_type not in expected: #checking if the last word is present in the 'expected ' list of street types or n
            street_types[street_type].add(street_name)
    
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street") 


street_types = defaultdict(set)
for event, elem in ET.iterparse(osm_file, events=("start",)):
    if elem.tag == "node" or elem.tag == "way":
        for tag in elem.iter("tag"):
            if is_street_name(tag): 
                audit_street_type(street_types, tag.attrib['v'])


# In[5]:

#unique Last words of street names which are not in expected
for street in street_types:
    print(street)


# ## Cleaning Street Names

# here i'm cleaning some of the incorrect street names on my sample file to show that y code is working.

# In[31]:

#Updating the wrongly entred street names
from collections import defaultdict
import re
import pprint
import xml.etree.cElementTree as ET
#Creating a dictionary"mapping" to update the wrongly entred street types by mapping 
mapping = { "Ext.": "Extension",
            "Mkt.":"Market",
            "nagar":"Nagar",
            "St.": "Street",
            "Qrs":"Quarters",
            "chowk":"Chowk",
            "Rd":"Road",
            "block":"Block",
            "Rd.":"Road",
            "road":"Road",
            "vihar":"Vihar",
            "apartment":"Apartment",
            "No.":"Number " 
               
            }
keys=mapping.keys() #creating a list of keys present in mapping dictionary
print(keys)
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
PROBLEMCHARS = re.compile(r'[=\+/&-<>;\'"\?%#$@\,\. \t\r\n]') #regular expression to identify problematic charecters in a string
LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+') #regular expression to match or search "abc:def"

def update_street_name(name, mapping):#function to update wrongly entred street names
        m = street_type_re.search(name)
        if m:
            street_type=m.group()
    
            if street_type in keys:
                value=mapping[street_type]
                y=name.find(street_type) #finds the index of wrongly entred street type in street name
                z=value                  # updated street type
                return z

            else:
                x = name.replace("no."," Number ").replace(" Gurgaon 122002","None").replace("II","2").replace(" No.","  Number ").replace(" no.","").replace(",","")
                return x


# In[32]:

#Street names after cleaning
for event, elem in ET.iterparse(osm_file, events=("start",)):
    if elem.tag == "node" or elem.tag == "way": 
        for tag in elem.iter("tag"):
            if is_street_name(tag):               #checking if it is a street name
                print("Before:",tag.attrib['v'])
                print("After:",update_street_name(tag.attrib['v'], mapping))


# ## Auditing Postal Codes

# In this map region there are many areas which lies outside city boundries and have postal codes outside the range of delhi district and some postal codes may have white space in between due to insertion error. Hence in this section I'll find out all those codes and then clean it.

# In[26]:

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

SAMPLE_FILE = r"C:\Users\MAVERICK\delhi\mini_sample1.osm"

incorrect_pins = []        #creating a list for postal codes which are not in range
correct_pins = []          #creating a list of pincodes which belong to range 110001-110094
count = 0
white_space = re.compile(r'\S+\s+\S+')    #regular expression to match white space charecters in a sting with 2 words
for event, elem in ET.iterparse(SAMPLE_FILE):
    if elem.tag == "node" or elem.tag == "way": 
        for tag in elem.iter("tag"):
            if tag.attrib['k'] == "postal_code" or tag.attrib['k'] == "addr:postcode": 
                #some postalcodes are wrongly entred as a string
                if tag.attrib['v']=='Paschimanagari' or tag.attrib['v'] == 'spine Road':
                    count += 1
                    #print(tag.attrib['v'])
                    continue
                #finding number of postal code have white space in between ie.. "411 012"
                elif white_space.search(tag.attrib['v']):
                    #print(tag.attrib['v'])
                    count += 1
                    continue
                elif int(tag.attrib['v'].strip())<110001 or int(tag.attrib['v'].strip())>110094:                  
                    incorrect_pins.append(tag.attrib['v'])
                elif int(tag.attrib['v'].strip())>110001 or int(tag.attrib['v'].strip())<110094:                  
                    correct_pins.append(tag.attrib['v'])
print("Number of postal codes wrongly entered :",count)                    
print("Number of Postal codes which line outside the city : ",len(incorrect_pins))
print("Number of Postal codes which belong to range 110001-110094 :",len(correct_pins))


# ## Cleaning Postal Codes

# In[36]:

#Updating wrongly entered pincodes
white_space=re.compile(r'\S+\s+\S+')
COLON= re.compile(r'^([a-z]|_)+:')
def update_pincode(pincode):
    if white_space.search(pincode):
        x=pincode.replace(" ","") #replacing the white space in pincodes "110 001 " with "110001"
        return x 

    elif int(pincode) < 110001 or int(pincode) > 110094:
        return None
    else:
        return pincode


# In[37]:

#Postal codes before and after cleaning process
for event, elem in ET.iterparse(osm_file):
    if elem.tag == "node" or elem.tag == "way":
        for tag in elem.iter("tag"):
            if tag.attrib['k'] == "postal_code" or tag.attrib['k'] == "addr:postcode":
                print("Before :",tag.attrib['v'])
                print("After :",update_pincode(tag.attrib['v']))


# # XML to CSV File Conversion

# To use file in data base and process queries onto them we need to convert XML files in CSV formats and in the below code we will do the same. Before converting the file in CSV format we need to clean our XML file and we will first clean XML file then convert it in CSV format.

# In[38]:

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import codecs
import csv
import schema
import cerberus

SCHEMA=schema.schema

OSMFILE = r"C:\Users\MAVERICK\delhi\mini_sample1.osm"                    #using sample as a OSM file
NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

# Make sure the fields order in the csv's matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

#This function update the street names and postal codes by calling update_street_names and update_pincode functions
def shape_element(element, default_tag_type='regular'):
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements
    node_tags={}
    # checking if the tag is "Node"
    if element.tag == 'node':
        for k in element.attrib:
            #checking if 'K ' is in NODE_FIELDS
            if k in NODE_FIELDS:
                node_attribs[k]=element.attrib[k]
        for x in element:
            # Checking if the element has the child tag "tag"
            if x.tag=='tag':
                # searching for problematic charecters
                if PROBLEMCHARS.search(x.attrib["k"]):
                    continue
                # checking for colon " : " Match
                elif LOWER_COLON.match(x.attrib['k']) :
                    #equating the values to node_tags dictionary
                    node_tags['id']=element.attrib['id']
                    #spliting "key" and "type"  in 'K' attribute
                    node_tags['key']=x.attrib['k'].split(":",1)[1] #
                    node_tags['type']=x.attrib['k'].split(":",1)[0]
# if the value of k is " addr:street" and by calling "update_street_name" function will equate the cleaned street name  
                    if x.attrib['k']=='addr:street':
                        node_tags['value']=update_street_name(x.attrib['v'],mapping)
# if the value of k is " addr:postcode"  and by calling "update_pincode" function will equate the filtered postal codes  
                    elif x.attrib['k']=='addr:postcode':
                        if update_pincode(x.attrib['v']):
                            node_tags['value']=update_pincode(x.attrib['v'])
                        else:
                            continue
# if the value of k is " postal_code" and by calling "update_pincode" function will equate the filtered postal codes 
#here the 'type' will ne 'regular'
                elif x.attrib['k']=='post_code':
                    if update_postalcode(x.attrib['v']):
                        node_tags["value"]=update_postalcode(x.attrib["v"])
                        node_tags["type"]='regular'
                        node_tags["key"]=x.attrib["k"]
                        node_tags["id"]=element.attrib["id"]
                    else:
                        continue
#Below code is for the rest of the "k"  values
                else:
                    node_tags["type"]='regular'
                    node_tags["key"]=x.attrib["k"]
                    node_tags["id"]=element.attrib["id"]
                    node_tags["value"]=x.attrib["v"]
                tags.append(node_tags)
        return {'node': node_attribs, 'node_tags': tags}
# the following code is coded as same as above but for the tag "way"
    elif element.tag == 'way':
        for x in element.attrib:
            if x in WAY_FIELDS:
                way_attribs[x]=element.attrib[x]
        count=0
        for l in element.iter("nd"):
            way_nodes.append({'id':element.attrib['id'],'node_id':l.attrib['ref'],'position':count})
            count+=1
        for y in element:
            if y.tag=='tag':
                if PROBLEMCHARS.search(y.attrib["k"]):
                    continue
                elif LOWER_COLON.match(y.attrib['k']):
                    node_tags['id']=element.attrib['id']
                    node_tags['key']=y.attrib['k'].split(":",1)[1]
                    node_tags['type']=y.attrib['k'].split(":",1)[0]
                    if y.attrib['k']=='addr:street':
                        node_tags['value']=update_street_name(y.attrib['v'], mapping)
                    elif y.attrib['k']=='addr:postcode':
                        node_tags['value']=update_pincode(y.attrib['v'])
                elif y.attrib['k']=='post_code':
                    node_tags["value"]=update_postalcode(y.attrib["v"])
                    node_tags["type"]='regular'
                    node_tags["key"]=y.attrib["k"]
                    node_tags["id"]=element.attrib["id"]
                else:
                    node_tags["type"]='regular'
                    node_tags["key"]=y.attrib["k"]
                    node_tags["id"]=element.attrib["id"]
                    node_tags["value"]=y.attrib["v"]
                tags.append(node_tags) 
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}   
    
#THE FOLLOWING CODE IS TO CONVERT THE XML INTO CSV 
# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem           
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(OSMFILE, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'wb') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'wb') as nodes_tags_file,          codecs.open(WAYS_PATH, 'wb') as ways_file,          codecs.open(WAY_NODES_PATH, 'wb') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'wb') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(OSMFILE, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSMFILE, validate=False)


# In[ ]:



