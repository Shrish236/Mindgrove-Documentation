import requests
import pandas as pd
import json
from datetime import datetime
from tabulate import tabulate
pd.set_option('display.width', 180)

token= "Enter token here"

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


# Get user input for project number
project_name = input(("\nEnter project name: "))

# GraphQL query
# query = """
#     query($number: String!){

#         node(id: $number) {
#             ...on projectV2{
#             items(first: 10) {
#               nodes{
#                 id
#                 fieldValueByName(name: "Status") {
#                   ... on ProjectV2ItemFieldSingleSelectValue {
#                     name
#                   }
#                 }
#                 fieldValues(first: 8) {
#                   nodes{
#                     ... on ProjectV2ItemFieldDateValue {
#                       date
#                       field {
#                         ... on ProjectV2FieldCommon {
#                           name
#                         }
#                       }
#                     }
#                   }
#                 }
#                 content{
#                     ... on DraftIssue {
#                       title
#                       body
#                       assignees(first: 10) {
#                         nodes{
#                           login
#                         }
#                       }
#                     }
#                     ...on Issue {
#                       title
#                       assignees(first: 10) {
#                         nodes{
#                           login
#                         }
#                       }
#                     }
#                     ...on PullRequest {
#                       title
#                       assignees(first: 10) {
#                         nodes{
#                           login
#                         }
#                       }
#                     }
#                 }
#               }
#             }
#         }

#     }
# """
query = """
    query($id: ID!){
    node(id: $id) {
        ... on ProjectV2 {
          items(first: 20) {
            nodes{
              id
                fieldValueByName(name: "Status") {
                  ... on ProjectV2ItemFieldSingleSelectValue {
                    name
                  }
                }
                fieldValues(first: 8) {
                  nodes{
                    ... on ProjectV2ItemFieldDateValue {
                      date
                      field {
                        ... on ProjectV2FieldCommon {
                          name
                        }
                      }
                    }
                  }
                }
                content{
                    ... on DraftIssue {
                      title
                      body
                      assignees(first: 10) {
                        nodes{
                          login
                        }
                      }
                    }
                    ...on Issue {
                      title
                      assignees(first: 10) {
                        nodes{
                          login
                        }
                      }
                    }
                    ...on PullRequest {
                      title
                      assignees(first: 10) {
                        nodes{
                          login
                        }
                      }
                    }
                }
            }
          }
        }
      }
    }
"""

variables ={
    "id" : proj_map[project_name]
}
result = run_query(query, variables)    # execute query

print(json.dumps(result, indent=2))

# Parse through retrieved data
output_planned = {}
output_inProgress = {}
output_completed = {}
for fields in result['data']['node']['items']['nodes']:
  d = dict()
  if fields['fieldValueByName']['name'] == "Todo":
    for data in fields['fieldValues']['nodes']:
      if len(data)!=0:
        d[data['field']['name']] = data['date']
    d['Task Name'] = fields['content']['title']
    for employee in fields['content']['assignees']['nodes']:
      if(output_planned.get(employee['login']) == None):
        output_planned[employee['login']] = [d]
      else:
        output_planned[employee['login']].append(d)

  if fields['fieldValueByName']['name'] == "In Progress":
    for data in fields['fieldValues']['nodes']:
      if len(data)!=0:
        d[data['field']['name']] = data['date']
    d['Task Name'] = fields['content']['title']
    for employee in fields['content']['assignees']['nodes']:
      if(output_inProgress.get(employee['login']) == None):
        output_inProgress[employee['login']] = [d]
      else:
        output_inProgress[employee['login']].append(d)

  if fields['fieldValueByName']['name'] == "Done":
    for data in fields['fieldValues']['nodes']:
      if len(data)!=0:
        d[data['field']['name']] = data['date']

    # Computing effort variance
    d["Planned Effort (days)"] = calc_days(d['Planned Start'], d['Planned End'])
    d['Actual Effort (days)'] = calc_days(d['Start Date'], d['End Date'])
    d['Effort variance'] = ((d['Actual Effort (days)'] - d["Planned Effort (days)"])/d["Planned Effort (days)"])*100
    d['Task Name'] = fields['content']['title']
    for employee in fields['content']['assignees']['nodes']:
      if(output_completed.get(employee['login']) == None):
        output_completed[employee['login']] = [d]
      else:
        output_completed[employee['login']].append(d)

print("\nPlanned tasks:\n")
flat_data = []
n=1
for person, tasks in output_planned.items():
    for i, task in enumerate(tasks):
      flat_data.append({**task, 'S.No': n, 'Person': person})
      n+=1

df = pd.DataFrame(flat_data)
column_order = ["S.No", "Person", "Task Name"] + [col for col in df.columns if col != "Person" and col!= "Task Name" and col!="S.No"]
df = df[column_order]

print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))

print("\nTasks in Progress:\n")
flat_data = []
n=1
for person, tasks in output_inProgress.items():
    for i, task in enumerate(tasks):
      flat_data.append({**task, 'S.No': n, 'Person': person})
      n+=1

df = pd.DataFrame(flat_data)
column_order = ["S.No", "Person", "Task Name"] + [col for col in df.columns if col != "Person" and col!= "Task Name" and col!="S.No"]
df = df[column_order]

print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))

print("\nTasks Completed:\n")
flat_data = []
n=1
for person, tasks in output_completed.items():
    for i, task in enumerate(tasks):
      flat_data.append({**task, 'S.No': n, 'Person': person})
      n+=1

df = pd.DataFrame(flat_data)
column_order = ["S.No", "Person", "Task Name"] + [col for col in df.columns if col != "Person" and col!= "Task Name" and col!="S.No"]
df = df[column_order]

print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))
# df.to_csv("Employee.csv", header=True, index=False