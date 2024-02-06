from flask import Flask, request, Response
import sendemail

app = Flask(__name__)

@app.route('/handle_post', methods=['GET', 'POST'])
def hello_world1():
    if request.method == 'POST':
        data = request.json
        if data["action"] == "assigned":
            print(data['assignee']['login'])
            subject = "New issue has been assigned"
            message_text = f"""\

                Hi there @{data['assignee']['login']},

                You have been assigned a new task in the {data["repository"]["name"]} repository.

                <b>Issue Title: {data['issue']['title']}
                <b>Issue Number: {data['issue']['number']}
                <b>Assignee: {data['assignee']['login']}

            """
            message_html = f"""\

                Hi there <b>@{data['assignee']['login']}</b>,<br/><br/>

                You have been assigned a new task in the <b>{data["repository"]["name"]}</b> repository.<br/><br/>

                <b>Issue Title:</b> <a href="{data['issue']['html_url']}"><i>{data['issue']['title']}</i></a><br/>
                <b>Issue Number:</b> {data['issue']['number']}<br/>
                <b>Assignee:</b> {data['assignee']['login']}<br/>

            """


            sendemail.callemail(data['assignee']['login'], message_text, message_html, subject)

        return Response("{'Webhook Response':'Success'}", status=200, mimetype='application/json')

    return "Success"