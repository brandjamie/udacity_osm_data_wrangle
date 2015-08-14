import xml.etree.ElementTree as ET
import re
import string
import json


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
# numbers only
numbers = re.compile('^[0-9]+$')
# numeric allowing hypens, commas and semicolons but not spaces (for house numbers)
hnumbers = re.compile('^[0-9\,;\-\s]+$')
# upper of lowercase alphabetical (including spaces or underscore)
alphunderscorenum =  re.compile('^[a-zA-Z\s\d\_]+$')
# Upper or lowercase alphabetical (including underscore but not spaces).
underscorenospace =  re.compile('^[a-zA-Z\s\d\_]+$')
# Match any string
regall = re.compile('^[.]+$')
# Match correct postcodes
pcd = re.compile('^[A-Z]{1,2}[[0-9]{1,2} [0-9][A-Z][A-Z]$')
# Match correct maxspeed
mxspd = re.compile('^[0-9]{1,3} mph$')




# Specific tags to deal with. No longer needed but left here to explain some of the code later. 
problem_tags = {
    # Amended in the clean_name_number_street function
    "addr:street":["The Centre, The Crescent, Colchester Business Part","<difference>","25 Culver St W","Stephenson Road"],
    # removed tags as data is not meaningful
    # Amended in the 'clean_building' function
    "building":["bing","no"],
    # removed tags as data is not meaningful
    # in the 'cleanelement' function
    "highway":["no"],
    #Changed from 'natural' tag to housename
    # Amended in the 'elementtojson' function
    "natural":["Bentley Childrens Play Area", "Hollands Farm"],
  # Acceptable value as it is for a railway
    "maxspeed":["161"],
    # Amended in the clean_name_number_street function
    # Names "LB1" - "LB4" allowed as not sure if data is meaningful or not
    "addr:housename":["LB1","LB2","LB3","LB4","A12 Southbound"]
    }


# Clean the 'addr_street' tag
def clean_addr_street(element):
    # abbreivations to change (will ignore case) 
    types = {
        "Road":["road","rd","rd."],
        "Lane":["lane","ln","ln."],
        "Street":["street","st",'st.'],
        "West":["west","w","w."],
        "East":["east","e","e."],
        "South":["south","s","s."],
        "North":["north","n","n."],
        "Drive":["drive","drv","dv",'dv.'],
        "Cut":["cut"]
    }
    # Fix capitalization
    element = string.capwords(element)
    
    element = element.split()
    # Check and fix last word for abbreviations
    lastword = element[-1]
    lastword = checktagvalue(lastword,types)
    element[-1]=lastword
    # check and fix second to last word for abbreviations
    # if last word is a compass direction
    if lastword in ["North","South","East","West"]:
        secondlastword = element[-2]
        secondlastword = checktagvalue(secondlastword,types)
        element[-2]=secondlastword
    element = " ".join(element)
    return element


# Clean the postcode tag
def clean_postcode(pc):
    # Change '!' to '1' as identified in testing.
    pc = pc.replace("!","1")
    pc = pc.upper()
    pc = re.sub(' +',' ',pc)
    # identified in testing - OQL exists while 0lo doesn't
    if pc == "CO7 0QLO":
        pc = "CO7 0QL"
    # identified in testing
    if pc == "CO61DU":
        pc = "CO6 1DU"
    return pc


# Clean the building tag
def clean_building(building):
    building = building.lower()
    building = building.replace(" ","_")
    if building == "pig_ark" or building == "pigl_ark":
        building = "sty"
    if building == "bing" or building == "no":
        building == False
    return building

# Clean the source:building tag
def clean_source_building(building):
    if building == "bing":
        building == "Bing"
    return building
        
# Clean the source tag
def clean_source(source):
    if source == "bing":
        source == "Bing"
    source = source.replace(" ","_")
    return source

# Clean the maxspeed tag
def clean_maxspeed(spd):
    if not mxspd.match(spd):
        if numbers.match(spd):
            spd = spd+" mph"
        else:
            spd = spd[:-3]+" mph"
        if not mxspd.match(spd):
            print("Warning max speed wrong after cleaning")
            print(mxspd)
    return spd

# Check an element against a dictionary and apply a substitution if neccesary. 
def checktagvalue(element,types):
    for key in types:
        if element.lower() in types[key]:
            return key
    return element






# Take a key and an element and return a cleaned element. 
def cleanelement(elkey,elvalue):
    # these keys all require replaceing spaces with underscores and making lowercase
    lower_and_underscore = ["landuse","aminity","barrier","service"]
    if elkey =="addr:street":
        elvalue = clean_addr_street(elvalue)
    elif elkey =="addr:postcode":
        elvalue = clean_postcode(elvalue)
    elif elkey =="building":
        elvalue = clean_building(elvalue)
    elif elkey =="source:building":
        elvalue = clean_source_building(elvalue)
    elif elkey =="source":
        elvalue = clean_source(elvalue)
    elif elkey =="maxspeed":
        elvalue = clean_maxspeed(elvalue)
    # Specific tag from investigation
    elif elkey =="highway" and elvalue =="no":
        elvalue = False
    elif elkey in lower_and_underscore:
        elvalue = elvalue.lower()
        elvalue = elvalue.replace(" ","_")
    return elvalue        

# change words to numbers. Works with numbers from 1-99
def wordtoint(word):
    types = {
        "one":1,
        "two":2,
        "three":3,
        "four":4,
        "five":5,
        "six":6,
        "seven":7,
        "eight":8,
        "nine":9,
        "ten":10,
        "eleven":11,
        "twelve":12,
        "thirteen":13,
        "fourteen":14,
        "fifteen":15,
        "sixteen":16,
        "seventeen":17,
        "eighteen":18,
        "nineteen":19,
        "twenty":20,
        "thirty":30,
        "forty":40,
        "fifty":50,
        "sixty":60,
        "seventy":70,
        "eighty":80,
        "ninety":90
        }
    if word.lower() in types:
        word = types[word.lower()]
    return word


# change a string with number words in it to use figures instead (e.g. 'Unit Twenty One' becomes 'Unit 21'). Works with numbers one to ninety nine.
def wordstonum(words):
    words = words.split()
    lastword = 0
    newwords = ""
    for word in words:
        word = wordtoint(word)
        if type(word)==int:
            lastword = lastword+word
        else:
            if lastword > 0:
                newwords = newwords+str(lastword)+" "
            newwords = newwords+word+" "
    if lastword > 0:
        newwords = newwords+str(lastword)+" "
    newwords = newwords[:-1]
    return newwords

# Compare the house name, street and house number and try to put values in the correct tags. 
def clean_name_number_street(hname,hnum,sname):
    #create arrays to check
    hnuma = [False,False,False]
    hnamea = [False,False,False]
    is_clash = False
    newsname = sname
   
    # housenumber can return housenumber, housename or street from dirty data
    if bool(hnum):
        hnuma = clean_housenumber(hnum)
    if bool(sname):
        snamea = clean_addr_street(sname)
    # housename can return housenumber, housename or street from dirty data
    if bool (hname):
        hnamea = clean_housename(hname)

        # Give a warning if two house number values are available
    if bool(hnuma[0]) and bool(hnamea[0]):
        newhnum = hnuma[0]
        print("Warning - two values for housenumber: "+hnuma[0]+ " and "+hnamea[0])
        print("Reverting to original values")
        is_clash = True
    elif bool(hnamea [0]):
        newhnum = hnamea [0]
    else:
        newhnum = hnuma[0]
   
    
    # Give a warning if two house name values are available
    if bool(hnamea[1]) and bool(hnuma[1]):
        newhname = hnamea[1]
        print("Warning - two values for housenumber: "+hnamea[1]+ " and "+hnuma[1])
        print("Reverting to original values")
        is_clash = True
    elif bool(hnamea [1]):
        newhname = hnamea [1]
    else:
        newhname = hnuma[1]
    
    
    # Give a warning if three street name values are available
    if bool(hnamea[2]) and bool(hnuma[2]) and bool(sname):
      is_clash = True
        
    elif bool(sname) and bool(hnamea[2]):
       is_clash = True
  
    elif bool(sname) and bool(hnuma[2]):
      is_clash = True
  
    elif bool(hnamea[2]) and bool(hnuma[2]):
        is_clash = True
        newsname = hname[2]
    elif bool(sname):
        pass
    elif bool (hnamea[2]):
        newsname = hnamea[2]
    elif bool (hnuma[2]):
        newsname = hnuma[2]
    
   # Address specific problems found in the set
    if sname == "25 Culver St W":
        newsname = "Culver Sreet West"
        newhnum = "25"
    # Checked address on Google.     
    if sname == "The Centre, The Crescent, Colchester Business Part":
        newsname = "Colchester Business Park"
        newhname = "The Centre, The Crescent"
    if sname == "<different>":
        newsname = False
    if hname == "A12 Southbound":
        newhname = sname
        newsname = hname
            
    #revert changes if there has been a clash of values
    if is_clash:
        newhname = hname
        newhnum = hnum
        newsname = sname
   
     
    return [newhname,newhnum,newsname]
        
        
    

# returns an array of housenumber, housename and streetname - each defaulting to false if the relevent value is not found
# to catch: 'The Bungalow, Meadowview Park' 'Unit 7a Rice Bridge Industrial Estate' '3' 'Bo-Peep'
def clean_housename(hname):
    hnum = False
    sname = False
    if hname == "?":
        hname = False
    elif re.match('^[a-zA-Z\s\'\-\&\(\)\-\.\’\é]+$',hname):
        pass
    elif numbers.match(hname):
        hnum = hname
        hname = False
    elif re.match('^Unit [A-Z0-9\-]+$',hname):
        hnum = hname
        hname = False
    elif re.match('^Block [A-Z0-9\-]+$',hname):
        hnum = hname
        hname = False
    elif re.match('^Unit [A-Za-z0-9\-\/]+ [A-Za-z\s]+$',hname):
        splitname = hname.split()
        hnum = " ".join(splitname[0:2])
        hname = " ".join(splitname[2:])
    elif re.match('^[0-9a-z\-]+ [A-Za-z\s]+$',hname):
        splitname = hname.split()
        hnum = " ".join(splitname[0:1])
        sname = " ".join(splitname[1:])

        #Specific problem addresses
        #matching a specific address with a mistake in it. 
    elif hname == ",Scarletts":
        hname == "Scarletts"
        # matching 'No 1 Tha Maltings The Quayside Maltings
    elif re.match('^No',hname):
        hname = "The Maltings"
        sname = "The Quayside Maltings"
        hnum = "1"
        # matching 'Upper Tower, Lower Tower' let pass as it is unclear what the correct name should be
    elif hname == "Upper Tower,Lower Tower":
        pass
    # matching "The Sixth Form College, Colchester"
    elif hname == "The Sixth Form College, Colchester":
        pass
    # Assuming that if there is a comma, it is separating house name and street name. 
    elif re.match('^[A-Za-z\s]+,[A-Za-z\s]+$',hname):
        splitname = hname.split(",")
        hname = splitname[0]
        sname = splitname[1]        
    return [hnum,hname,sname]







# returns an array of housenumber, housename and streetname - each defaulting to false if the relevent value is not found
def clean_housenumber(hnum):
    hname = False
    sname = False
    # change written numbers to figures
    hnum = wordstonum(hnum)
    #Change "?" value to False (to be removed as a tag) 
    if hnum=="?":
        hnum=False
    # Allow values with only numbers and punctuation
    elif hnumbers.match(hnum):
        pass
    # If it takes the form 'A13' (as found in investigation)
    elif re.match('^A[0-9]+$',hnum):
        pass
    # Allow numbers plus one alphabetical character e.g. 112a
    elif re.match('^[0-9]+[a-z]$',hnum):
        pass
    # Allow numbers plus one alphabetical character e.g. 112A changed to lower case
    elif re.match('^[0-9]+[A-Z]$',hnum):
        hnum=hnum.lower()
    # If word has only alphabetical characters (with appostrophe,hypen and forward slash)    
    elif re.match('^[a-zA-Z\s\'\-\/]+$',hnum):
        # Some houses have a singles letter instead of a house number. Convert all instances to uppercase. 
        if re.match('^[a-zA-Z]$',hnum):
            hnum = hnum.upper()
        # Allow 'Unit A' etc
        elif re.match('^Unit [A-Z]$',hnum):
            pass
        else:
            hname="'"+hnum+"'"
            hnum=False
    elif re.match('^[0-9\,\;\-]+ [a-zA-Z\s]+$',hnum):
        splitnum = hnum.split()
        hnum = splitnum[0]
        sname= splitnum[1:]
        sname = " ".join(sname)
    return ([hnum,hname,sname])




# take the xml filename, convert and save the data to json
def makejson(filename):
    out = filename+".json"
    notfirstline = False
    with open(out,'w') as outfile:
        #While writing as a stream, need to have opening square bracket
        outfile.write('[')
        for _, element in ET.iterparse(filename):
            node = elementtojson(element)
            if bool(node):
                if notfirstline:
                      #While writing as a stream, need to have dividing comma
                      outfile.write(',')
                else:
                    notfirstline = True
                json.dump(node, outfile,indent = 4)
        #While writing as a stream, need to have closing square bracket
        outfile.write(']')
        outfile.close


                
# Convert each element to json format
def elementtojson(element):
    CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
    node = {}
    created = {}
    address = {}
    lat = 0
    lon = 0
    noderefs = []
    housenumber = False
    housename = False
    streetname = False
    if element.tag == "node" or element.tag == "way" :
        #set node type
        if element.tag == "node":
            node['type']="node"
        else:
            node['type']="way"
        #set attribute elements    
        for item in element.attrib:
            if item in CREATED:
                created[item]=element.attrib[item]
            elif item == "lat":
                lat = float(element.attrib[item])
            elif item == "lon":
                lon = float(element.attrib[item])
            else:
                node[item]=element.attrib[item]
        node['created']=created
        node['pos'] = [lat,lon]
        # iterate through tags        
        for item in element:
            # collect noderefs
            if element.tag =="way" and item.tag == "df":
                noderefs.append(item.attrib['ref'])
            elif "k" in item.attrib and not problemchars.search(item.get('k')):
                elkey = item.get('k')
                elvalue = item.get('v')
                # collect housenumber streetname and housename for comparison
                if elkey == "addr:housenumber":
                    housenumber = elvalue
                elif elkey == "addr:housename":
                    housename = elvalue
                elif elkey == "addr:street":
                    streetname = elvalue
                else:
                    addarr = elkey.split(":")
                    # check if item is an address
                    if len(addarr) == 2 and addarr[0] == "addr":
                        #clean and add item to address
                        address[addarr[1]]= cleanelement(elkey,elvalue)
                    else:
                        #clean and add item
                        #specific change from observations. 
                        if elkey == "natural":
                            if elvalue == "Hollands Farm":
                                elkey ="addr:housename"
                            elif elvalue == "Bentley Childrens Play Area":
                                elkey ="addr:housename"
                        
                        elvalue = cleanelement(elkey,elvalue)
                        # check cleanelement doesn't return 'False'
                        if bool(elvalue):
                            #add element to json
                            node[item.attrib['k']] = cleanelement(elkey,elvalue)
        # Housenumber, housename and streetname to be compared                  
        if bool(housenumber) or bool(housename) or bool(streetname):
            housenamenum = clean_name_number_street(housename,housenumber,streetname)
            # Add housenumber, housename and/or street name if they exist
            if bool(housenamenum[0]):
                address['housename']=housenamenum[0]
            if bool(housenamenum[1]):
                address['housenumber']=housenamenum[1]
            if bool(housenamenum[2]):
                address['street']=housenamenum[2]
                
        if bool(address):
            node['address']=address
        if bool(noderefs):
            node['node_refs']=noderefs
        return node
    else:
        return None 

    
filename = "colchester_england.osm"

makejson(filename)


