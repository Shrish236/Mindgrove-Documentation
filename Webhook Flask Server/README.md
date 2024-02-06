## Documentation: GitHub Project Management and Reporting Tool

This Python Flask server provides a tool for receiving webhook data from github projects. It receives data posted by the github webhook and processes the data for further tasks. The current version of this tool sends an email to the corresponding assignees of the particular task if a new issue is assigned to a repository.

### Requirements

The following requirements were specified:

1. Set up a dynamic email system to send an email notification if a new issue is assigned to a assignee in github projects.

### Setting up webhooks

1. Access Repository Settings:
2. Log in to your GitHub account.
3. Navigate to the repository where you want to set up the webhook.
4. Click on the "Settings" tab in the repository.
5. Select the "Webhooks" option from the menu on the left.
6. Add New Webhook:
7. Click on the "Add webhook" button.
8. Configure Webhook:
9. Enter the Payload URL: This is the URL of the endpoint in your receiver application where GitHub will send the webhook payload.
10. Choose Content Type: Select the content type for the webhook payload (e.g., JSON).
11. Select Events: Choose the events that should trigger the webhook (e.g., push, pull request, etc.).
12. Optionally, configure other settings such as SSL verification, secret token, etc.
13. Save Webhook
14. Once configured, click on the "Add webhook" or "Create webhook" button to save the webhook configuration

### Flask Server

The flask server is hosted remotely at pythonanywhere.com, the github webhook posts the selected events data in the selected format to the server accordingly.

### Dependencies:
Ensure the following Python packages are installed:

- `requests`: For making HTTP requests to the GitHub API.
- `json`: For handling JSON data.
- `flask`: For setting up a flask server

Install dependencies using pip:
```bash
pip install requests json requests flask
```

### Functionality Overview

#### Flask Application (flask_app.py):

1. Defines a Flask application with an endpoint /handle_post to handle POST requests from a GitHub webhook.
2. Extracts relevant information from the received JSON data and sends an email notification to the assignee if an issue is assigned.
3. Returns a JSON response indicating the success or failure of the webhook processing.


#### sendemail.py Module:

1. Provides a function send_email() to send email notifications to employees.
2. Utilizes the smtplib library to connect to the SMTP server and send emails securely.
3. Retrieves employee email IDs from a dictionary and sends emails using the provided content and subject.
4. These components work together to create a system that sends email notifications to employees when issues are assigned to them via GitHub. 
5. Ensure to replace placeholder values such as YOUR_ORG_EMAIL and YOUR_GOOGLE_APP_PASSWORD with actual values.

This documentation provides a comprehensive overview of the utilizing dynamic webhook data in github and performing required tasks using the posted data.