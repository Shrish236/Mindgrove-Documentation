## Documentation: GitHub Project Management and Reporting Tool

This Python script provides a tool for managing and reporting GitHub project tasks. It interacts with the GitHub GraphQL API to retrieve project data and offers functionalities to visualize planned and in-progress tasks, along with deviations in task schedules.

### Requirements

The following requirements were specified:

1. Query github's API to retrive data present in the projects of the organization
2. Analyze the data for planned and in progress tasks.
3. Compute deviation between planned start date and actual start date for in progress task.
4. Enable user to dynamically input the required project for the above analysis
5. Plot tasks planned for employees in the github project card
6. Enable user to easily analyze employee deviation for in progress tasks through data visualization in plotly


### Features Overview:
1. **GitHub API Integration:** Utilizes the GitHub GraphQL API to fetch project-related data.

2. **Data Processing:** Processes the retrieved data to organize tasks based on their status (Planned, In Progress).

3. **Visualization:** Generates interactive visualizations using Plotly Express to represent task occupancy and deviations.

4. **Menu-driven Interface:** Provides an interactive menu-driven interface for users to navigate through different functionalities.

### Dependencies:
Ensure the following Python packages are installed:

- `requests`: For making HTTP requests to the GitHub API.
- `pandas`: For data manipulation and analysis.
- `json`: For handling JSON data.
- `datetime`: For date and time calculations.
- `tabulate`: For generating formatted tables.
- `plotly`: For creating interactive plots and charts.

Install dependencies using pip:
```bash
pip install requests pandas tabulate plotly
```

### GitHub Personal Access Tokens:
The script requires GitHub Personal Access Token (`token`) with appropriate permissions to access GitHub project data. Ensure that you have generated the tokens and replaced them in the script.

### Running the Script:
1. Run the Python script (`occupancyChart.py`).
2. Enter the project number when prompted.
3. Choose from the available options in the main menu to view planned tasks, tasks in progress, or to exit the tool.

### Functionality Overview:
1. **Planned Tasks for Individual Employees:**
   - Displays planned tasks for individual employees.
   - Visualizes employee occupancy levels over time.

2. **Tasks in Progress for All Employees:**
   - Presents tasks currently in progress for all employees.
   - Highlights deviations in task schedules.

### Usage Example:
```python
python occupancyChart.py
```

### Notes:
- Ensure a stable internet connection for accessing the GitHub API.
- Handle GitHub API rate limits and potential errors appropriately.
- Customize the script as per project requirements, such as modifying GraphQL queries or enhancing visualization options.

This documentation provides a comprehensive overview of the GitHub project management and reporting tool, facilitating efficient task tracking and analysis within GitHub projects.