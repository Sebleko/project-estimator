# Variables for system design prompt template

project_description = """
TaskFlow is a team collaboration and task management platform designed for small to medium-sized businesses. 
The system allows teams to create projects, assign tasks, track progress, and share documents in one centralized 
location. TaskFlow aims to improve team productivity, enhance transparency in project status, and simplify 
communication between team members working remotely or in-office.
"""

requirements = """
## Functional Requirements

[FR-1] **User Management**
   - [FR-1.1] System must support user registration, authentication, and profile management
   - [FR-1.2] System must implement role-based permissions (admin, project manager, team member)

[FR-2] **Project Management**
   - [FR-2.1] Users must be able to create, update, and archive projects
   - [FR-2.2] Projects must support deadlines, descriptions, and team assignments

[FR-3] **Task Management**
   - [FR-3.1] Users must be able to create, assign, and track tasks within projects
   - [FR-3.2] Tasks must support priorities, deadlines, attachments, and status updates

[FR-4] **Team Collaboration**
   - [FR-4.1] System must provide a comment thread for each task and project
   - [FR-4.2] System must allow file sharing and document collaboration
   - [FR-4.3] System must send notifications for relevant updates and approaching deadlines

[FR-5] **Reporting**
   - [FR-5.1] System must generate progress reports for projects and tasks
   - [FR-5.2] System must provide basic analytics on team and individual productivity

## Non-functional Requirements

[NFR-1] **Performance**
   - [NFR-1.1] System must support up to 100 concurrent users
   - [NFR-1.2] Page load times must be under 2 seconds
   - [NFR-1.3] File uploads must support documents up to 25MB

[NFR-2] **Reliability**
   - [NFR-2.1] System must be available 99.5% of the time
   - [NFR-2.2] All data must be backed up daily
   - [NFR-2.3] System must handle errors gracefully with appropriate user feedback

[NFR-3] **Security**
   - [NFR-3.1] All data transmission must be encrypted
   - [NFR-3.2] Passwords must be securely hashed
   - [NFR-3.3] System must implement session timeout after 30 minutes of inactivity

[NFR-4] **Usability**
   - [NFR-4.1] Interface must be responsive and work on desktop and mobile devices
   - [NFR-4.2] System must provide intuitive navigation and search functionality
   - [NFR-4.3] System must be accessible according to WCAG 2.1 AA standards
"""

user_stories = """
[US-01] As a team administrator, I want to create new projects and assign team members so that work can be properly organized.

[US-02] As a project manager, I want to set task priorities and deadlines so that team members know what to focus on.

[US-03] As a team member, I want to update my task status so that everyone can see my progress without requiring meetings.

[US-04] As a team member, I want to receive notifications when I'm assigned new tasks so that I don't miss important work.

[US-05] As a team member, I want to attach files to tasks so that relevant documents are easily accessible.

[US-06] As a project manager, I want to generate progress reports so that I can share updates with stakeholders.

[US-07] As a team administrator, I want to manage user permissions so that information is shared appropriately.

[US-08] As a team member, I want to filter and search tasks so that I can quickly find what I need to work on.

[US-09] As a new user, I want to have an intuitive interface so that I can start using the system without extensive training.

[US-10] As a project manager, I want to see a dashboard of all project statuses so that I can identify bottlenecks quickly.
"""