import xml.etree.ElementTree as ET
import sys

# Sample XML data
xml_data = '''
<DataBase>
<Count>20</Count>
<DatabaseRedactions>
<DatabaseRedaction ID="1">0,0,0,,,,0,0,0,0,0,0,,vv,CVDPS,vv,0,1,0,1,676,1128,726,1167,0,0</DatabaseRedaction>
<DatabaseRedaction ID="2">0,0,0,,,,0,0,0,0,0,0,,vv,CVDPS,vv,0,1,0,2,653,1598,682,1623,0,0</DatabaseRedaction>
<DatabaseRedaction ID="3">0,0,0,,,,0,0,0,0,0,0,,vv,CVDPS,vv,0,1,0,3,925,554,951,574,0,0</DatabaseRedaction>
<DatabaseRedaction ID="4">0,0,0,,,,0,0,0,0,0,0,,vv,CVDPS,vv,0,1,0,4,986,551,1064,572,0,0</DatabaseRedaction>
<DatabaseRedaction ID="5">0,0,0,,,,0,0,0,0,0,0,,vv,CVDPS,vv,0,1,0,5,1176,561,1179,564,0,0</DatabaseRedaction>
<DatabaseRedaction ID="6">0,0,0,,,,0,0,0,0,0,0,,vv,CVDPS,vv,0,1,0,6,234,563,256,584,0,0</DatabaseRedaction>
<DatabaseRedaction ID="7">0,0,0,,,,0,0,0,0,0,0,,vv,CVDPS,vv,0,1,0,7,235,581,259,599,0,0</DatabaseRedaction>
<DatabaseRedaction ID="8">0,0,0,,,,0,0,0,0,0,0,,vv,CVDPS,vv,0,1,0,8,127,815,159,833,0,0</DatabaseRedaction>
<DatabaseRedaction ID="9">0,0,0,,,,0,0,0,0,0,0,,vv,CVDPS,vv,0,1,0,9,133,834,151,846,0,0</DatabaseRedaction>
<DatabaseRedaction ID="10">0,0,0,,,,0,0,0,0,0,0,,vv,CVDPS,vv,0,1,0,10,180,829,188,844,0,0</DatabaseRedaction>
<DatabaseRedaction ID="11">0,0,0,,,,0,0,0,0,0,0,,vv,CVDPS,vv,0,1,0,11,205,829,237,846,0,0</DatabaseRedaction>
<DatabaseRedaction ID="12">0,0,0,,,,0,0,0,0,0,0,,vv,CVDPS,vv,0,1,0,12,656,522,736,544,0,0</DatabaseRedaction>
<DatabaseRedaction ID="13">0,0,0,,,,0,0,0,0,0,0,,vv,CVDPS,vv,0,1,0,13,497,1532,636,1551,0,0</DatabaseRedaction>
<DatabaseRedaction ID="14">0,0,0,,,,0,0,0,0,0,0,,vv,CVDPS,vv,0,1,0,14,568,1528,576,1558,0,0</DatabaseRedaction>
<DatabaseRedaction ID="15">0,0,0,,,,0,0,0,0,0,0,,vv,CVDPS,vv,0,1,0,15,580,1532,636,1551,0,0</DatabaseRedaction>
<DatabaseRedaction ID="16">0,0,0,,,,0,0,0,0,0,0,,vv,CVDPS,vv,0,1,0,16,986,551,1160,572,0,0</DatabaseRedaction>
<DatabaseRedaction ID="17">0,0,0,,,,0,0,0,0,0,0,,vv,CVDPS,vv,0,1,0,17,440,586,507,621,0,0</DatabaseRedaction>
<DatabaseRedaction ID="18">0,0,0,,,,0,0,0,0,0,0,,vv,CVDPS,vv,0,1,0,18,1100,790,1162,805,0,0</DatabaseRedaction>
<DatabaseRedaction ID="19">0,0,0,,,,0,0,0,0,0,0,,vv,CVDPS,vv,0,1,0,19,730,895,895,979,0,0</DatabaseRedaction>
<DatabaseRedaction ID="20">0,0,0,,,,0,0,0,0,0,0,,vv,CVDPS,vv,0,1,0,20,759,1475,905,1551,0,0</DatabaseRedaction>
</DatabaseRedactions>
</DataBase>
'''
# Parse the XML data
root = ET.fromstring(xml_data)

# Open a file for writing
with open("output.txt", "w") as file:
    # Find all DatabaseRedaction elements
    database_redactions = root.findall(".//DatabaseRedaction")

    # Iterate over each DatabaseRedaction element
    for redaction in database_redactions:
        # Extract the specific values and join them with spaces
        values = redaction.text.split(',')[20:24]
        # Write the values to the file with spaces
        file.write(' '.join(values) + '\n')