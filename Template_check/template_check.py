import requests
import pandas as pd
import json
from datetime import datetime
from tabulate import tabulate
pd.set_option('display.width', 180)

token= "Enter your token here"

# Employee github username and corresponding Names
# employee_username_map = {
#     "Shrish236": "Shrish",
#     "app1357": "Aparajeeth"
# }

# Function to calculate number of days between two dates
def calc_days(date1, date2):
  date_format = "%Y-%m-%d"

  a = datetime.strptime(date1, date_format)
  b = datetime.strptime(date2, date_format)

  delta = b - a

  return delta.days

# Function to execute graphQL query to retrieve data
def run_query(query, variables):
    headers = {"Authorization": "Bearer " + token}
    request = requests.post('https://api.github.com/graphql', json={'query': query, 'variables' : variables}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


# GraphQL query
query = """

     query{
  node(id: "PVT_kwDOBTvaZ84AYtff") {
    ... on ProjectV2 {
      fields(first: 100) {
        nodes {
          ... on ProjectV2Field {
            id
            name
          }
          ... on ProjectV2IterationField {
            id
            name
            configuration {
              iterations {
                startDate
                id
              }
            }
          }
          ... on ProjectV2SingleSelectField {
            id
            name
            options {
              id
              name
            }
          }
        }
      }
    }
  }
}


"""
benchmarks=[]
templist=[]
fielddict={}
variables ={
    "number" : project_number
}
result = run_query(query, variables)    # execute query
print(json.dumps(result, indent=2))
for fields in result["data"]["node"]["fields"]["nodes"]:
    benchmarks.append(fields["name"])
fielddict["Coherent Core Complex"]=benchmarks
for titlenames in proj_map.keys():
  templist.clear()
  for fields in result["data"]["node"]["fields"]["nodes"]:
    templist.append(fields["name"])
  fielddict[titlenames]=templist
faultytemp=set()
for titlenames in fielddict.keys():
  if len(fielddict[titlenames])!=len(fielddict["Coherent Core Complex"]):
    faultytemp.add(titlenames)
  else:
    if fielddict[titlenames]!=fielddict["Coherent Core Complex"]:
      faultytemp.add(titlenames)
print(fielddict["Vision SoC"])
print(faultytemp)