import json
import os
import gzip
import time

to_read=[]
data_list=[]

for a,b,c in os.walk(os.curdir):
    for item in c:
      if item.endswith(".json"):
         to_read.append(item)
         
def getkey(node):
    if isinstance(node,dict):
        return node["number"]

    
for file in to_read:
 try:
  with open(file) as file_obj:
    data_list.append(json.load(file_obj))
 except:
      pass


data=[item for sublist in data_list for item in sublist]


data=sorted(data,key=getkey)




with gzip.GzipFile('data.gz','w') as fid_gz:
    
        # get json as type dict
        
        # convert dict to str
        json_str = json.dumps(data)
        json_str=json_str.encode()
    # write string
        fid_gz.write(json_str)


