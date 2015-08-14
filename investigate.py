import xml.etree.ElementTree as ET
import re

# regular expressions used in checking data
# All lower case including  underscore
lower = re.compile(r'^([a-z]|_)*$')
# All lower case including underscore and one colon. 
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
# contains characters that might be problems
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
# upper or lowercase alphanumeric (including spaces)
alphanumeric = re.compile('^[a-zA-Z\s\d]+$')
# upper or lowercase alphabetical (including spaces)
alpha = re.compile('^[a-zA-Z\s]+$')
# upper of lowercase alphabetical (including spaces and apostrophes)
alphaappos = re.compile('^[a-zA-Z\s\']+$')
# numeric allowing hypens, commas and semicolons but not spaces (for house numbers)
hnumbers = re.compile('^[0-9\,;\-\s]+$')
# upper of lowercase alphabetical (including spaces or underscore)
alphunderscorenum =  re.compile('^[a-zA-Z\s\d\_]+$')
# Upper or lowercase alphabetical (including underscore but not spaces).
underscorenospace =  re.compile('^[a-zA-Z\s\d\_]+$')
# Match any string
regall =  re.compile('^[.]+$')

# Looks at the keys for each tag and checks for problem characters. 
def process_map(filename):

    def key_type(element, keys):
        if element.tag == "tag":
            attrib = element.get("k")
            if problemchars.search(attrib):
                keys["problemchars"]=keys["problemchars"]+1
            elif lower_colon.search(attrib):
                keys["lower_colon"]=keys["lower_colon"]+1
            elif lower.search(attrib):
                keys["lower"]=keys["lower"]+1
            else:    
                keys["other"]=keys["other"]+1
        return keys

    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys


# Sorts a dictionary of tags by the size of the count.
def sorttags(tags):
    return sorted(tags.items(), key = lambda x:x[1])


# Count and name all tags. Returns a dictionary. 
def count_tags(filename):
    tags = {}
    for event, elem in ET.iterparse (filename):
        if elem.tag=="tag":
            thisnode = elem.get("k")
            if thisnode in tags:
                tags[thisnode]=tags[thisnode]+1
            else: 
                tags[thisnode]=1
    return sorttags(tags)


# Check the values of a chosen tag against a regular expresion (default is alphanumeric characters and spaces).
# Prints any values which do not match the regular expression.
# If getkeys is true, returns a sorted dictionary of tag values with a count for each. 
def check_tag(filename,tag,getkeys=False,tag_regex=alphanumeric):
    def process_tag(element,keys):
        if element in keys:
            keys[element]=keys[element]+1
        else: 
            keys[element]=1
        return keys

    if getkeys:
        keys = {}
    for _, element in ET.iterparse(filename):
        if element.tag == "tag" and element.get("k")==tag:
            thistag = element.get("v")
            if tag_regex.match(thistag):
                pass
            else:
                print (thistag)
            if getkeys:
                keys = process_tag(thistag,keys)               
    if getkeys:
        return sorttags(keys)


# check street
def check_addr_street(filename):
    streetkeys = {}
    for _, element in ET.iterparse(filename):
        if element.tag == "tag" and element.get("k")=="addr:street":
            streetkeys = process_addr_street(element.get("v"),streetkeys)
    return streetkeys
            

def process_addr_street(element,keys):
    #check for non-alphanumeric characters in the string (as could indicate mistakes)
    if alphaappos.match(element):
        pass
    else:
        print (element)
    # Create agregate list of last word of street    
    element = element.split()
    element = element[-1]
    if element in keys:
        keys[element]=keys[element]+1
    else: 
        keys[element]=1
    return keys


# check postcode

def check_pc(filename):
    pckeys = {}
    for _, element in ET.iterparse(filename):
        if element.tag == "tag" and element.get("k")=="addr:postcode":
            pckeys = process_addr_pc(element.get("v"),pckeys)
    return pckeys

def process_addr_pc(element,keys):
    if re.match('^[a-zA-Z\s\d]+$',element):
        pass
    else:
        print (element)
    if element in keys:
        keys[element]=keys[element]+1
    else: 
        keys[element]=1
    return keys




filename = "colchester_england.osm"

######################################
#      Investigative process         #
######################################

# Uncomment the relevent code in each stage to reproduce.


#################### Stage 1 #########################

# Check all keys have acceptable values

#print (process_map(filename))

# Make an ordered list of keys to see which are the most used

#print (count_tags(filename))


################ Stage 2 Identifying problems ################
# Looking first at the address tags then at the other most used tags.


# Check streets
# Checks the last word of each street name and counts the number of each value. 

#print (check_addr_street(filename))

# Check postcodes for alphanumeric characters and print a summary of the different values. 

#print (check_tag(filename,"addr:postcode",True))

# check addr:housenumber
#check_tag(filename,"addr:housenumber",False,hnumbers)

# check building
# print (check_tag(filename,"building",True,alphunderscorenum))

# check source:building
#print (check_tag(filename,"source:building",True))

# check source
#print (check_tag(filename,"source",True,regall))

# check highway
#print (check_tag(filename,"highway",True,alphunderscorenum))

# check name
#check_tag(filename,"name",False)

# check addr:city
#print (check_tag(filename,"addr:city",True))

# check natural
#print (check_tag(filename,"natural",True))

# check addr:housename
#check_tag(filename,"addr:housename",False,alpha)

# check maxspeed
#print (check_tag(filename,"maxspeed",True))

# check landuse
#print (check_tag(filename,"landuse",True))

# check power
#print (check_tag(filename,"power",True))

# check amenity
#print (check_tag(filename,"amenity",True,alphunderscorenum))

# check barrier
#print (check_tag(filename,"barrier",True,alphunderscorenum))

# check service
#print (check_tag(filename,"service",True,alphunderscorenum))

# Naptan tags are not used for data but to track where the data has been imported from. No need to clean. 





