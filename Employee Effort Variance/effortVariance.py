import requests
import pandas as pd
import json
from datetime import datetime
from tabulate import tabulate
pd.set_option('display.width', 180)

token= "PERSONAL_ACCESS_TOKEN"

employee_username_map = {
    "Shrish236": "Shrish",
    "app1357": "Aparajeeth"
}
def calc_days(date1, date2):
  date_format = "%Y-%m-%d"

  a = datetime.strptime(date1, date_format)
  b = datetime.strptime(date2, date_format)

  delta = b - a

  return delta.days

def run_query(query, variables):
    headers = {"Authorization": "Bearer " + token}
    request = requests.post('https://api.github.com/graphql', json={'query': query, 'variables' : variables}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


project_number = int(input("\nEnter project number: "))
query = """

    query($number: Int!){
      user(login: "Shrish236"){
        projectV2(number: $number){
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
    "number" : project_number
}
result = run_query(query, variables)
# print(json.dumps(result, indent=2))
output_planned = {}
output_inProgress = {}
output_completed = {}
for fields in result['data']['user']['projectV2']['items']['nodes']:
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
    d["Planned Effort (days)"] = calc_days(d['Planned Start Date'], d['Planned End Date'])
    d['Actual Effort (days)'] = calc_days(d['Actual Start Date'], d['Actual End Date'])
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
      flat_data.append({**task, 'S.No': n, 'Person': employee_username_map[person]})
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
      flat_data.append({**task, 'S.No': n, 'Person': employee_username_map[person]})
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
      flat_data.append({**task, 'S.No': n, 'Person': employee_username_map[person]})
      n+=1

df = pd.DataFrame(flat_data)
column_order = ["S.No", "Person", "Task Name"] + [col for col in df.columns if col != "Person" and col!= "Task Name" and col!="S.No"]
df = df[column_order]

print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))
# df.to_csv("Employee.csv", header=True, index=False)
