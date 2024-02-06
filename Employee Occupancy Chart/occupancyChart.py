import requests
import pandas as pd
import json
from datetime import datetime
from tabulate import tabulate
import plotly.express as px

pd.set_option('display.width', 180)

token = "PERSONAL_ACCESS_TOKEN"

# Employee username map
employee_map = {
    "Shrish": "Shrish236",
    "Aparajeeth": "app1357"
}

# Username employee map
employee_username_map = {
    "Shrish236": "Shrish",
    "app1357": "Aparajeeth"
}

def run_query(query, variables):
  headers = {"Authorization": "Bearer " + token}
  request = requests.post('https://api.github.com/graphql', json={'query': query, 'variables' : variables}, headers=headers)
  if request.status_code == 200:
    return request.json()
  else:
    raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

def calc_days(date1, date2):
  date_format = "%Y-%m-%d"

  a = datetime.strptime(date1, date_format)
  b = datetime.strptime(date2, date_format)

  delta = b - a

  return delta.days

def calc_occupancy(output_planned):
  print("This is a list of your employees")
  for person, data in employee_map.items():
    print(person)
  name = input("\n\nEnter name of employee to check occupancy: ")
  print()
  events = []
  for person, tasks in output_planned.items():
    if person == employee_map[name]:
      for data in tasks:
        events.append((data['Planned Start Date'], 'start'))
        events.append((data['Planned End Date'], 'end'))

  events.sort(key=lambda x: x[0])
  task_count = {}
  result_dates = []

  current_tasks = 0

  for event in events:
      date, event_type = event
      if event_type == 'start':
          current_tasks += 1
      else:
          current_tasks -= 1

      task_count[date] = current_tasks

      if date not in result_dates:
          result_dates.append(date)

  result_dates.sort()

  return result_dates, [task_count[date] for date in result_dates]

def planned_tasks(output_planned):
  print("\n\nPlanned tasks:\n")
  sorted_dates, task_counts = calc_occupancy(output_planned)
  fig = px.line(x=sorted_dates, y=task_counts, title="Employee Occupancy Chart", markers=True).update_layout(
      xaxis_title="Dates", yaxis_title="Occupancy level"
  )
  fig.show()

  fig = px.bar(x=sorted_dates, y=task_counts, title="Employee Occupancy Chart").update_layout(
      xaxis_title="Dates", yaxis_title="Occupancy level"
  )
  fig.show()


def individual_deviation(df):
  name = input("\n    Enter employee name to check deviation for in progress tasks: ")
  print()
  df_new = df[df['Person'] == name]

  fig = px.bar(x=df_new["Task Name"], y=df_new['Deviation'], title="Employee Deviation Chart").update_layout(
      xaxis_title="Task Name", yaxis_title="Deviation (days)"
  )
  fig.show()

def inProgress_tasks(output_inProgress):
  inProgressTask_map = {}
  for person, tasks in output_inProgress.items():
    inProgressTask_map[employee_username_map[person]] = len(tasks)

  inProgressTask_map = dict(sorted(inProgressTask_map.items(), key=lambda item: item[1]))
  fig = px.bar(x=inProgressTask_map.keys(), y=inProgressTask_map.values(), title="Employee Current Occupancy Chart").update_layout(
      xaxis_title="Employees", yaxis_title="Occupancy level"
  )
  fig.show()
  print()
  print(tabulate(pd.DataFrame.from_dict(inProgressTask_map, orient='index', columns=['Current Tasks']), headers='keys', tablefmt='pretty', showindex=True))
  print()
  print("\n\nDeviation of individual employees in current tasks\n\n")

  flat_data = []
  n=1
  # print(output_inProgress)
  for person, tasks in output_inProgress.items():
    for i, task in enumerate(tasks):
      flat_data.append({**task, 'S.No': n, 'Person': employee_username_map[person]})
      n+=1


  flat_data = sorted(flat_data, key=lambda x: x['S.No'])
  df = pd.DataFrame(flat_data)
  column_order = ["S.No", "Person", "Task Name"] + [col for col in df.columns if col != "Person" and col!= "Task Name" and col!="S.No"]
  df = df[column_order]

  while(True):
    print("\n   1. View deviation of current tasks of individual employees")
    print("\n   2. View deviation of current tasks of all employees")
    print("\n   3. Exit to main menu")
    choice = int(input("\n    Enter your choice: "))
    print()
    if(choice == 3):
      break
    if(choice == 2):
      print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))
    if(choice == 1):
      individual_deviation(df)

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

variables = {
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
    d['Deviation'] = calc_days(d['Planned Start Date'], d['Actual Start Date'])
    # print(d['Task Name'], d['Deviation'])
    for employee in fields['content']['assignees']['nodes']:
      if(output_inProgress.get(employee['login']) == None):
        output_inProgress[employee['login']] = [d]
      else:
        # print(employee['login'], d)
        output_inProgress[employee['login']].append(d)

print()

while(1):
  print("\n******Main Menu******")
  print("\nOption 1: Planned tasks for individual employees")
  print("\nOption 2: Tasks in Progress for all employees")
  print("\nOption 3: Exit")
  choice = int(input("\nEnter your choice: "))
  print()
  if(choice == 1):
    planned_tasks(output_planned)
  elif(choice == 2):
    inProgress_tasks(output_inProgress)
  elif(choice == 3):
    print("\n******Thank You******")
    break
