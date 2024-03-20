from flask import Flask, render_template, request, session
import requests
import pandas as pd
import json
import plotly.express as px
from datetime import datetime
from tabulate import tabulate
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

app = Flask(__name__)
app.secret_key = 'any random string'
project_map = {}

pd.set_option('display.width', 180)

token= "YOUR_PERSONAL_ACCESS_TOKEN"

# importing libraries

employee_email_IDs = {                              # Add email ID's of employees in
    "app1357":"aparajeeth02@gmail.com",             # your organization here
    "Shrish236":"shrishrajamohan@gmail.com",
    # "RohitSrinivasRG" : "rohit@mindgrovetech.in",
    #  "maheswaransg" : "umamaheswaran@mindgrovetech.in"
}

def callemail(name, message_text, message_html, subject):
    port = 465                                      # For SSL
    smtp_server = "smtp.gmail.com"                  # SMTP server to send email
    sender_email = "apshmindgrove23@gmail.com"      # Sender email address
    receiver_email = employee_email_IDs.get(name)   # Receiver email address
    password = "ririecrdonmjrajv"                   # App password created through google account

    # Add details of the email here
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = formataddr(('Mindgrove Technologies', sender_email))
    message["To"] = receiver_email

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(message_text, "plain")
    part2 = MIMEText(message_html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Sending email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent! to " + name)


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

def calc_occupancy(output_planned, name):
  events = []
  for person, tasks in output_planned.items():
    if person == name:
      for data in tasks:
        events.append((data['Planned Start'], 'start'))
        events.append((data['Planned End'], 'end'))

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


@app.route('/')
def home_page():
    return render_template("index.html")

@app.route('/effort-variance-form', methods=['GET'])
def effort_variance_form():
    query="""
        query{
            organization(login: "Mindgrove-Technologies") {
            projectsV2(first: 50) {
                nodes {
                id
                title
                url
                }
            }
            }
        }
    """
    variables ={
      "number" : "1"
    }
    result = run_query(query, variables)    # execute query
    global project_map
    proj_map=dict()
    project_list = []
    # print(json.dumps(result, indent=2))
    for projs in result['data']['organization']['projectsV2']['nodes']:
        proj_map[projs["title"]]={ 'id' : projs["id"], 'url': projs['url']}
        project_list.append(projs["title"])
    # print(proj_map)
    project_map = proj_map
    return render_template('effort_variance_form.html', projects=project_list)

@app.route('/effort-variance-table', methods=['POST'])
def effort_variance_display():
    if request.method == 'POST':
        project_name = request.form['project-title']
        query = """
            query($id: ID!){
                node(id: $id){
                ... on ProjectV2{
                        items(first: 20) {
                        nodes{
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
                                ... on ProjectV2ItemFieldTextValue {
                                text
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
                                id
                                assignees(first: 10) {
                                    nodes{
                                    login
                                    }
                                }
                                }
                                ...on Issue {
                                title
                                id
                                assignees(first: 10) {
                                    nodes{
                                    login
                                    }
                                }
                                }
                                ...on PullRequest {
                                title
                                id
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
            "id" : project_map[project_name]['id']
        }
        result = run_query(query, variables) 
        # print(json.dumps(result, indent=2))
        # print(request.form['project-title'])
        output_planned = {}
        planned = []
        output_inProgress = {}
        in_progress = []
        output_completed = {}
        completed = []
        dependency_map = {}
        for fields in result['data']['node']['items']['nodes']:
            d = dict()
            if fields['fieldValueByName']!=None:
                if fields['fieldValueByName']['name'] == "Todo":
                    d['Task Name'] = fields['content']['title']
                    for data in fields['fieldValues']['nodes']:
                        if len(data)!=0:
                            if(data.get('date')!=None):
                                d[data['field']['name']] = data['date']
                            if(data.get('text')!=None and data['field']['name'] == 'Dependency'):
                                d[data['field']['name']] = data['text']
                                dependencies = data['text']
                                temp = [x.strip() for x in dependencies.split(',')]
                                dependency_map[d['Task Name']] = temp

                    if(d.get('Planned Start')==None or d.get('Planned End')==None):
                        for employee in fields['content']['assignees']['nodes']:
                            subject = "Update task details"
                            message_text = f"""\

                                    Hi there @{employee['login']},

                                    Please fill the planned dates in the {project_name} Project in Mingrove-Technologies Project Board.

                                    Task Title: {d['Task Name']}

                                """
                            message_html = f"""\

                                    Hi there <b>@{employee['login']}</b>,<br/><br/>

                                    Please fill the planned dates in the <b>{project_name}</b> Project in <a href={project_map[project_name]['url']}><i>Mingrove-Technologies Project Board</i></a><br/><br/>

                                    <b>Task Title:</b> {d['Task Name']}<br/>
                                    <b>Assignee:</b> {employee['login']}<br/>

                                """
                            # callemail(employee['login'], message_text, message_html, subject)
                    else:
                        for employee in fields['content']['assignees']['nodes']:
                            if(output_planned.get(employee['login']) == None):
                                output_planned[employee['login']] = [d]
                            else:
                                output_planned[employee['login']].append(d)

                if fields['fieldValueByName']['name'] == "In Progress":
                    d['Task Name'] = fields['content']['title']
                    for data in fields['fieldValues']['nodes']:
                        if len(data)!=0:
                            if(data.get('date')!=None):
                                d[data['field']['name']] = data['date']
                            if(data.get('text')!=None and data['field']['name'] == 'Dependency'):
                                d[data['field']['name']] = data['text']
                                dependencies = data['text']
                                temp = [x.strip() for x in dependencies.split(',')]
                                dependency_map[d['Task Name']] = temp

                    if(d.get('Planned Start')==None or d.get('Planned End')==None or d.get('Actual Start')==None):
                        for employee in fields['content']['assignees']['nodes']:
                            subject = "Update task details"
                            message_text = f"""\

                                    Hi there @{employee['login']},

                                    Please fill the planned/actual dates in the {project_name} Project in Mingrove-Technologies Project Board.

                                    Task Title: {d['Task Name']}

                                """
                            message_html = f"""\

                                    Hi there <b>@{employee['login']}</b>,<br/><br/>

                                    Please fill the planned/actual dates in the <b>{project_name}</b> Project in <a href={project_map[project_name]['url']}><i>Mingrove-Technologies Project Board</i></a><br/><br/>

                                    <b>Task Title:</b> {d['Task Name']}<br/>
                                    <b>Assignee:</b> {employee['login']}<br/>

                                """
                            # callemail(employee['login'], message_text, message_html, subject)
                    else:
                        for employee in fields['content']['assignees']['nodes']:
                            if(output_inProgress.get(employee['login']) == None):
                                output_inProgress[employee['login']] = [d]
                            else:
                                output_inProgress[employee['login']].append(d)

                if fields['fieldValueByName']['name'] == "Done":
                    d['Task Name'] = fields['content']['title']
                    for data in fields['fieldValues']['nodes']:
                        if len(data)!=0:
                            if(data.get('date')!=None):
                                d[data['field']['name']] = data['date']
                            if(data.get('text')!=None and data['field']['name'] == 'Dependency'):
                                d[data['field']['name']] = data['text']
                                dependencies = data['text']
                                temp = [x.strip() for x in dependencies.split(',')]
                                dependency_map[d['Task Name']] = temp

                        # Computing effort variance

                    if(d.get('Planned Start')==None or d.get('Planned End')==None or d.get('Actual Start')==None or d.get('Actual End')==None):
                        for employee in fields['content']['assignees']['nodes']:
                            subject = "Update task details"
                            message_text = f"""\
                                    Hi there @{employee['login']},

                                    Please fill the planned/actual dates in the {project_name} Project in Mingrove-Technologies Project Board.

                                    Task Title: {d['Task Name']}

                                """
                            message_html = f"""\

                                    Hi there <b>@{employee['login']}</b>,<br/><br/>

                                    Please fill the planned/actual dates in the <b>{project_name}</b> Project in <a href={project_map[project_name]['url']}><i>Mingrove-Technologies Project Board</i></a><br/><br/>

                                    <b>Task Title:</b> {d['Task Name']}<br/>
                                    <b>Assignee:</b> {employee['login']}<br/>

                                """
                            # callemail(employee['login'], message_text, message_html, subject)

                    else:
                        
                        d["Planned Effort (days)"] = calc_days(d['Planned Start'], d['Planned End'])
                        d['Actual Effort (days)'] = calc_days(d['Actual Start'], d['Actual End'])
                        if(d['Planned Effort (days)'] == 0):
                            d["Planned Effort (days)"] = 1
                        if(d['Actual Effort (days)'] == 0):
                            d['Actual Effort (days)'] = 1
                        d['Effort variance'] = ((d['Actual Effort (days)'] - d["Planned Effort (days)"])/d["Planned Effort (days)"])*100
                        for employee in fields['content']['assignees']['nodes']:
                            if(output_completed.get(employee['login']) == None):
                                output_completed[employee['login']] = [d]
                            else:
                                output_completed[employee['login']].append(d)
        
        if len(output_planned)!=0:
            # print("\nPlanned tasks:\n")
            flat_data = []
            n=1
            for person, tasks in output_planned.items():
                for i, task in enumerate(tasks):
                    flat_data.append({**task, 'S.No': n, 'Person': person})
                    n+=1

            planned = flat_data
            # print(flat_data)
            # df = pd.DataFrame(flat_data)
            # column_order = ["S.No", "Person", "Task Name"] + [col for col in df.columns if col != "Person" and col!= "Task Name" and col!="S.No"]
            # df = df[column_order]

            # print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))

        if len(output_inProgress)!=0:
            # print("\nTasks in Progress:\n")
            flat_data = []
            n=1
            for person, tasks in output_inProgress.items():
                for i, task in enumerate(tasks):
                    flat_data.append({**task, 'S.No': n, 'Person': person})
                    n+=1

            in_progress = flat_data
            # df = pd.DataFrame(flat_data)
            # column_order = ["S.No", "Person", "Task Name"] + [col for col in df.columns if col != "Person" and col!= "Task Name" and col!="S.No"]
            # df = df[column_order]

            # print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))

        if len(output_completed)!=0:
            # print("\nTasks Completed:\n")
            flat_data = []
            n=1
            for person, tasks in output_completed.items():
                for i, task in enumerate(tasks):
                    flat_data.append({**task, 'S.No': n, 'Person': person})
                    n+=1

            completed = flat_data
            # df = pd.DataFrame(flat_data)
            # column_order = ["S.No", "Person", "Task Name"] + [col for col in df.columns if col != "Person" and col!= "Task Name" and col!="S.No"]
            # df = df[column_order]

            # print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))
    return render_template("effort_variance_table.html", name=project_name, planned=planned, in_progress=in_progress, completed=completed)

@app.route('/occupancy-chart-form')
def occupancy_chart_form():
    query="""
        query{
            organization(login: "Mindgrove-Technologies") {
            projectsV2(first: 50) {
                nodes {
                id
                title
                url
                }
            }
            }
        }
    """
    variables ={
      "number" : "1"
    }
    result = run_query(query, variables)    # execute query
    global project_map
    proj_map=dict()
    project_list = []
    # print(json.dumps(result, indent=2))
    for projs in result['data']['organization']['projectsV2']['nodes']:
        proj_map[projs["title"]]={ 'id' : projs["id"], 'url': projs['url']}
        project_list.append(projs["title"])
    # print(proj_map)
    project_map = proj_map
    return render_template('occupancy_chart_form.html', projects=project_list)

@app.route('/occupancy-chart', methods = ['POST'])
def occupancy_chart_display():
    if request.method == "POST":
        project_name = ""
        if 'occupancy-project' in session:
            project_name = session['occupancy-project']
        else:
            project_name = request.form['project-title']
            session['occupancy-project'] = project_name

        query = """
            query($id: ID!){
                node(id: $id){
                ... on ProjectV2{
                        items(first: 20) {
                        nodes{
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
                                ... on ProjectV2ItemFieldTextValue {
                                text
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
                                id
                                assignees(first: 10) {
                                    nodes{
                                    login
                                    }
                                }
                                }
                                ...on Issue {
                                title
                                id
                                assignees(first: 10) {
                                    nodes{
                                    login
                                    }
                                }
                                }
                                ...on PullRequest {
                                title
                                id
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
            "id" : project_map[project_name]['id']
        }
        result = run_query(query, variables) 
        # print(json.dumps(result, indent=2))
        # print(request.form['project-title'])
        output_planned = {}
        planned = []
        output_inProgress = {}
        in_progress = []
        output_completed = {}
        completed = []
        dependency_map = {}
        for fields in result['data']['node']['items']['nodes']:
            d = dict()
            if fields['fieldValueByName']!=None:
                if fields['fieldValueByName']['name'] == "Todo":
                    d['Task Name'] = fields['content']['title']
                    for data in fields['fieldValues']['nodes']:
                        if len(data)!=0:
                            if(data.get('date')!=None):
                                d[data['field']['name']] = data['date']
                            if(data.get('text')!=None and data['field']['name'] == 'Dependency'):
                                d[data['field']['name']] = data['text']
                                dependencies = data['text']
                                temp = [x.strip() for x in dependencies.split(',')]
                                dependency_map[d['Task Name']] = temp

                    if(d.get('Planned Start')==None or d.get('Planned End')==None):
                        for employee in fields['content']['assignees']['nodes']:
                            subject = "Update task details"
                            message_text = f"""\

                                    Hi there @{employee['login']},

                                    Please fill the planned dates in the {project_name} Project in Mingrove-Technologies Project Board.

                                    Task Title: {d['Task Name']}

                                """
                            message_html = f"""\

                                    Hi there <b>@{employee['login']}</b>,<br/><br/>

                                    Please fill the planned dates in the <b>{project_name}</b> Project in <a href={project_map[project_name]['url']}><i>Mingrove-Technologies Project Board</i></a><br/><br/>

                                    <b>Task Title:</b> {d['Task Name']}<br/>
                                    <b>Assignee:</b> {employee['login']}<br/>

                                """
                            # callemail(employee['login'], message_text, message_html, subject)
                    else:
                        for employee in fields['content']['assignees']['nodes']:
                            if(output_planned.get(employee['login']) == None):
                                output_planned[employee['login']] = [d]
                            else:
                                output_planned[employee['login']].append(d)

                if fields['fieldValueByName']['name'] == "In Progress":
                    d['Task Name'] = fields['content']['title']
                    for data in fields['fieldValues']['nodes']:
                        if len(data)!=0:
                            if(data.get('date')!=None):
                                d[data['field']['name']] = data['date']
                            if(data.get('text')!=None and data['field']['name'] == 'Dependency'):
                                d[data['field']['name']] = data['text']
                                dependencies = data['text']
                                temp = [x.strip() for x in dependencies.split(',')]
                                dependency_map[d['Task Name']] = temp

                    if(d.get('Planned Start')==None or d.get('Planned End')==None or d.get('Actual Start')==None):
                        for employee in fields['content']['assignees']['nodes']:
                            subject = "Update task details"
                            message_text = f"""\

                                    Hi there @{employee['login']},

                                    Please fill the planned/actual dates in the {project_name} Project in Mingrove-Technologies Project Board.

                                    Task Title: {d['Task Name']}

                                """
                            message_html = f"""\

                                    Hi there <b>@{employee['login']}</b>,<br/><br/>

                                    Please fill the planned/actual dates in the <b>{project_name}</b> Project in <a href={project_map[project_name]['url']}><i>Mingrove-Technologies Project Board</i></a><br/><br/>

                                    <b>Task Title:</b> {d['Task Name']}<br/>
                                    <b>Assignee:</b> {employee['login']}<br/>

                                """
                            # callemail(employee['login'], message_text, message_html, subject)
                    else:
                        for employee in fields['content']['assignees']['nodes']:
                            if(output_inProgress.get(employee['login']) == None):
                                output_inProgress[employee['login']] = [d]
                            else:
                                output_inProgress[employee['login']].append(d)

                if fields['fieldValueByName']['name'] == "Done":
                    d['Task Name'] = fields['content']['title']
                    for data in fields['fieldValues']['nodes']:
                        if len(data)!=0:
                            if(data.get('date')!=None):
                                d[data['field']['name']] = data['date']
                            if(data.get('text')!=None and data['field']['name'] == 'Dependency'):
                                d[data['field']['name']] = data['text']
                                dependencies = data['text']
                                temp = [x.strip() for x in dependencies.split(',')]
                                dependency_map[d['Task Name']] = temp

                        # Computing effort variance

                    if(d.get('Planned Start')==None or d.get('Planned End')==None or d.get('Actual Start')==None or d.get('Actual End')==None):
                        for employee in fields['content']['assignees']['nodes']:
                            subject = "Update task details"
                            message_text = f"""\
                                    Hi there @{employee['login']},

                                    Please fill the planned/actual dates in the {project_name} Project in Mingrove-Technologies Project Board.

                                    Task Title: {d['Task Name']}

                                """
                            message_html = f"""\

                                    Hi there <b>@{employee['login']}</b>,<br/><br/>

                                    Please fill the planned/actual dates in the <b>{project_name}</b> Project in <a href={project_map[project_name]['url']}><i>Mingrove-Technologies Project Board</i></a><br/><br/>

                                    <b>Task Title:</b> {d['Task Name']}<br/>
                                    <b>Assignee:</b> {employee['login']}<br/>

                                """
                            # callemail(employee['login'], message_text, message_html, subject)

                    else:
                        
                        d["Planned Effort (days)"] = calc_days(d['Planned Start'], d['Planned End'])
                        d['Actual Effort (days)'] = calc_days(d['Actual Start'], d['Actual End'])
                        if(d['Planned Effort (days)'] == 0):
                            d["Planned Effort (days)"] = 1
                        if(d['Actual Effort (days)'] == 0):
                            d['Actual Effort (days)'] = 1
                        d['Effort variance'] = ((d['Actual Effort (days)'] - d["Planned Effort (days)"])/d["Planned Effort (days)"])*100
                        for employee in fields['content']['assignees']['nodes']:
                            if(output_completed.get(employee['login']) == None):
                                output_completed[employee['login']] = [d]
                            else:
                                output_completed[employee['login']].append(d)
        
        # if len(output_planned)!=0:
        #     # print("\nPlanned tasks:\n")
        #     flat_data = []
        #     n=1
        #     for person, tasks in output_planned.items():
        #         for i, task in enumerate(tasks):
        #             flat_data.append({**task, 'S.No': n, 'Person': person})
        #             n+=1

        #     planned = flat_data
        #     # print(flat_data)
        #     # df = pd.DataFrame(flat_data)
        #     # column_order = ["S.No", "Person", "Task Name"] + [col for col in df.columns if col != "Person" and col!= "Task Name" and col!="S.No"]
        #     # df = df[column_order]

        #     # print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))

        # if len(output_inProgress)!=0:
        #     # print("\nTasks in Progress:\n")
        #     flat_data = []
        #     n=1
        #     for person, tasks in output_inProgress.items():
        #         for i, task in enumerate(tasks):
        #             flat_data.append({**task, 'S.No': n, 'Person': person})
        #             n+=1

        #     in_progress = flat_data
        #     # df = pd.DataFrame(flat_data)
        #     # column_order = ["S.No", "Person", "Task Name"] + [col for col in df.columns if col != "Person" and col!= "Task Name" and col!="S.No"]
        #     # df = df[column_order]

        #     # print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))

        # if len(output_completed)!=0:
        #     # print("\nTasks Completed:\n")
        #     flat_data = []
        #     n=1
        #     for person, tasks in output_completed.items():
        #         for i, task in enumerate(tasks):
        #             flat_data.append({**task, 'S.No': n, 'Person': person})
        #             n+=1

        #     completed = flat_data
        html1 = ""
        html2 = ""
        employees = []
        employee = ""
        if(len(output_planned)!=0):
            for person, tasks in output_planned.items():
                employees.append(person)
            if(request.form.get('employee-name')!=None):
                employee = request.form['employee-name']
                sorted_dates, task_counts = calc_occupancy(output_planned, employee)
                # fig = px.line(x=sorted_dates, y=task_counts, title="Employee Occupancy Chart", markers=True).update_layout(
                #     xaxis_title="Dates", yaxis_title="Occupancy level"
                # )
                # fig.show()

                fig2 = px.bar(x=sorted_dates, y=task_counts, title="Employee Occupancy Chart").update_layout(
                    xaxis_title="Dates", yaxis_title="Occupancy level"
                )
                html2 = fig2.to_html()

        if(len(output_inProgress)!=0):
            inProgressTask_map = {}
            for person, tasks in output_inProgress.items():
                inProgressTask_map[person] = len(tasks)
            
            # print(inProgressTask_map)
            # employees = inProgressTask_map.keys()
            inProgressTask_map = dict(sorted(inProgressTask_map.items(), key=lambda item: item[1]))
            fig = px.bar(x=inProgressTask_map.keys(), y=inProgressTask_map.values(), title="Employee Current Occupancy Chart").update_layout(
                xaxis_title="Employees", yaxis_title="Occupancy level"
            )

            html1 = fig.to_html()
            # iframe = """
            # <iframe id="plotly-figure" src="{}"></iframe>
            # """.format(html)
        
    return render_template('occupancy_chart_display.html', iframe=html1, project=project_name, employees=employees, iframe2=html2, employee=employee)

@app.route('/email-notification', methods=['GET', 'POST'])
def email_notification():
    query="""
        query{
            organization(login: "Mindgrove-Technologies") {
            projectsV2(first: 50) {
                nodes {
                id
                title
                url
                }
            }
            }
        }
    """
    variables ={
      "number" : "1"
    }
    result = run_query(query, variables)    # execute query
    global project_map
    proj_map=dict()
    project_list = []
    # print(json.dumps(result, indent=2))
    for projs in result['data']['organization']['projectsV2']['nodes']:
        proj_map[projs["title"]]={ 'id' : projs["id"], 'url': projs['url']}
        project_list.append(projs["title"])
    # print(proj_map)
    project_map = proj_map
    project = ""
    if request.method == 'POST':
        project_name = request.form['project-title']
        query = """
            query($id: ID!){
                node(id: $id){
                ... on ProjectV2{
                        items(first: 20) {
                        nodes{
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
                                ... on ProjectV2ItemFieldTextValue {
                                text
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
                                id
                                assignees(first: 10) {
                                    nodes{
                                    login
                                    }
                                }
                                }
                                ...on Issue {
                                title
                                id
                                assignees(first: 10) {
                                    nodes{
                                    login
                                    }
                                }
                                }
                                ...on PullRequest {
                                title
                                id
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
            "id" : project_map[project_name]['id']
        }
        result = run_query(query, variables) 
        # print(json.dumps(result, indent=2))
        # print(request.form['project-title'])
        output_planned = {}
        output_inProgress = {}
        output_completed = {}
        dependency_map = {}
        for fields in result['data']['node']['items']['nodes']:
            d = dict()
            if fields['fieldValueByName']!=None:
                if fields['fieldValueByName']['name'] == "Todo":
                    d['Task Name'] = fields['content']['title']
                    for data in fields['fieldValues']['nodes']:
                        if len(data)!=0:
                            if(data.get('date')!=None):
                                d[data['field']['name']] = data['date']
                            if(data.get('text')!=None and data['field']['name'] == 'Dependency'):
                                d[data['field']['name']] = data['text']
                                dependencies = data['text']
                                temp = [x.strip() for x in dependencies.split(',')]
                                dependency_map[d['Task Name']] = temp

                    if(d.get('Planned Start')==None or d.get('Planned End')==None):
                        for employee in fields['content']['assignees']['nodes']:
                            subject = "Update task details"
                            message_text = f"""\

                                    Hi there @{employee['login']},

                                    Please fill the planned dates in the {project_name} Project in Mingrove-Technologies Project Board.

                                    Task Title: {d['Task Name']}

                                """
                            message_html = f"""\

                                    Hi there <b>@{employee['login']}</b>,<br/><br/>

                                    Please fill the planned dates in the <b>{project_name}</b> Project in <a href={project_map[project_name]['url']}><i>Mingrove-Technologies Project Board</i></a><br/><br/>

                                    <b>Task Title:</b> {d['Task Name']}<br/>
                                    <b>Assignee:</b> {employee['login']}<br/>

                                """
                            project = project_name
                            callemail(employee['login'], message_text, message_html, subject)
                    else:
                        for employee in fields['content']['assignees']['nodes']:
                            if(output_planned.get(employee['login']) == None):
                                output_planned[employee['login']] = [d]
                            else:
                                output_planned[employee['login']].append(d)

                if fields['fieldValueByName']['name'] == "In Progress":
                    d['Task Name'] = fields['content']['title']
                    for data in fields['fieldValues']['nodes']:
                        if len(data)!=0:
                            if(data.get('date')!=None):
                                d[data['field']['name']] = data['date']
                            if(data.get('text')!=None and data['field']['name'] == 'Dependency'):
                                d[data['field']['name']] = data['text']
                                dependencies = data['text']
                                temp = [x.strip() for x in dependencies.split(',')]
                                dependency_map[d['Task Name']] = temp

                    if(d.get('Planned Start')==None or d.get('Planned End')==None or d.get('Actual Start')==None):
                        for employee in fields['content']['assignees']['nodes']:
                            subject = "Update task details"
                            message_text = f"""\

                                    Hi there @{employee['login']},

                                    Please fill the planned/actual dates in the {project_name} Project in Mingrove-Technologies Project Board.

                                    Task Title: {d['Task Name']}

                                """
                            message_html = f"""\

                                    Hi there <b>@{employee['login']}</b>,<br/><br/>

                                    Please fill the planned/actual dates in the <b>{project_name}</b> Project in <a href={project_map[project_name]['url']}><i>Mingrove-Technologies Project Board</i></a><br/><br/>

                                    <b>Task Title:</b> {d['Task Name']}<br/>
                                    <b>Assignee:</b> {employee['login']}<br/>

                                """
                            project = project_name
                            callemail(employee['login'], message_text, message_html, subject)
                    else:
                        for employee in fields['content']['assignees']['nodes']:
                            if(output_inProgress.get(employee['login']) == None):
                                output_inProgress[employee['login']] = [d]
                            else:
                                output_inProgress[employee['login']].append(d)

                if fields['fieldValueByName']['name'] == "Done":
                    d['Task Name'] = fields['content']['title']
                    for data in fields['fieldValues']['nodes']:
                        if len(data)!=0:
                            if(data.get('date')!=None):
                                d[data['field']['name']] = data['date']
                            if(data.get('text')!=None and data['field']['name'] == 'Dependency'):
                                d[data['field']['name']] = data['text']
                                dependencies = data['text']
                                temp = [x.strip() for x in dependencies.split(',')]
                                dependency_map[d['Task Name']] = temp

                        # Computing effort variance

                    if(d.get('Planned Start')==None or d.get('Planned End')==None or d.get('Actual Start')==None or d.get('Actual End')==None):
                        for employee in fields['content']['assignees']['nodes']:
                            subject = "Update task details"
                            message_text = f"""\
                                    Hi there @{employee['login']},

                                    Please fill the planned/actual dates in the {project_name} Project in Mingrove-Technologies Project Board.

                                    Task Title: {d['Task Name']}

                                """
                            message_html = f"""\

                                    Hi there <b>@{employee['login']}</b>,<br/><br/>

                                    Please fill the planned/actual dates in the <b>{project_name}</b> Project in <a href={project_map[project_name]['url']}><i>Mingrove-Technologies Project Board</i></a><br/><br/>

                                    <b>Task Title:</b> {d['Task Name']}<br/>
                                    <b>Assignee:</b> {employee['login']}<br/>

                                """
                            project = project_name
                            callemail(employee['login'], message_text, message_html, subject)

                    else:
                        
                        d["Planned Effort (days)"] = calc_days(d['Planned Start'], d['Planned End'])
                        d['Actual Effort (days)'] = calc_days(d['Actual Start'], d['Actual End'])
                        if(d['Planned Effort (days)'] == 0):
                            d["Planned Effort (days)"] = 1
                        if(d['Actual Effort (days)'] == 0):
                            d['Actual Effort (days)'] = 1
                        d['Effort variance'] = ((d['Actual Effort (days)'] - d["Planned Effort (days)"])/d["Planned Effort (days)"])*100
                        for employee in fields['content']['assignees']['nodes']:
                            if(output_completed.get(employee['login']) == None):
                                output_completed[employee['login']] = [d]
                            else:
                                output_completed[employee['login']].append(d)

    return render_template("email_notification.html", projects=project_map, project=project)

if __name__ == "__main__":
    app.run(debug=True)