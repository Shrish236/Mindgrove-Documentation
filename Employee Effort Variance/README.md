## Documentation: Retrieving GitHub Project Data and Generating Reports

### Introduction

This documentation outlines a Python script that utilizes the GitHub GraphQL API to retrieve project data and generates reports on planned, in-progress, and completed tasks. The script collects task details such as task name, assignees, status, and dates.

### Requirements

The following requirements were specified:

1. Query github's API to retrive data present in the projects of the organization
2. Analyze the data for planned, in progress and completed tasks.
3. Calculate employee effort variance for completed tasks, by computing actual and planned effort
4. Enable user to dynamically input the required project for the above analysis
5. Display planned, in progress and completed tasks as separate tables.

### Script Overview

The Python script performs the following tasks:

1. Imports necessary libraries including `requests`, `pandas`, `json`, `datetime`, and `tabulate`.
2. Defines a function `calc_days()` to calculate the difference in days between two dates.
3. Defines a function `run_query()` to execute GraphQL queries to the GitHub API.
4. Prompts the user to enter the project number.
5. Constructs a GraphQL query to retrieve project data based on the project number.
6. Parses the GraphQL response and organizes task data into dictionaries based on task status (Planned, In Progress, Done).
7. Converts the organized data into a tabular format using Pandas DataFrame.
8. Prints tabulated reports for planned, in-progress, and completed tasks.

### Required Access Tokens

Ensure you have appropriate GitHub Personal Access Tokens (`token`) with the necessary permissions to access project data from GitHub.

### Dependencies

Ensure you have the following Python packages installed:

- `requests`
- `pandas`
- `json`
- `datetime`
- `tabulate`

Install the dependencies using pip:

```bash
pip install requests pandas tabulate
```

### Running the Script

1. Run the Python script.
2. Enter the project number when prompted.
3. The script retrieves project data from GitHub, processes it, and generates tabulated reports for planned, in-progress, and completed tasks.
4. The reports are displayed on the console.

### Example Usage

```python
python effortVariance.py
```

### Note

- Ensure that you have a stable internet connection to communicate with the GitHub API.
- Handle GitHub API rate limits and potential errors gracefully in production scenarios.
- Customize the script according to your specific project requirements, such as modifying the GraphQL query or adjusting data processing logic.

This documentation provides a comprehensive overview of the Python script for retrieving GitHub project data and generating reports.
