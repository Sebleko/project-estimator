# 1) Combined Requirements and User Stories Generation Prompt
requirements_and_stories_prompt = """
You are analyzing a software project proposal to extract clear requirements and user stories.
A potential customer has approached with a project idea that needs to be translated into concrete specifications.
Your task is to generate both a list of requirements and corresponding user stories for the project.

**Free form Project Description given by the customer:**
{project_description}

**Instructions:**
1. Generate a project description that clarifies the scope and purpose of the project.
2. Generate a list of project requirements. Focus on essential functionality that fulfills the core purpose.
3. For each requirement, generate one or more user stories in the format: "As a [type of user], I want [some goal] so that [some reason]."
4. If necessary, generate a list of max 3 questions that you would ask the customer to clarify the project requirements.

{format_instructions}
"""

# 2) Question Answer Integration Prompt
question_answer_integration_prompt = """
You are analyzing a software project proposal to finalize specifications.
In the previous step, you generated an initial list of requirements and user stories based on the customer's project description.
You also asked some clarifying questions which the customer has now answered.
Your task is to integrate these answers into the final requirements and user stories.

**Free form Project Description given by the customer:**
{project_description}

**Project description generated in previous step:**
{project_description_generated}

**Requirements generated in previous step:**
{requirements}

**User Stores generated in previous step:**
{user_stories}

**Questions and Answers from the previous step:**
{questions_and_answers}

**Instructions:**
1. Integrate the customer's answers into a final project description.
2. Output a final list of requirements that clearly define the project scope.
3. Generate updated user stories that align with the finalized requirements.

{format_instructions}
"""

system_description_format = """
The system architecture is described in terms of components and their interactions.
The system description outlines what components exist and how they interact to produce the full system. 
The component descriptions provide technical details about each component. 
Components might include "Database", "User Interface", "API", "Authentication Service", etc.

Components are written in CAPITAL LETTERS within the system description.
Example overly simple dummy system description:
The FULL SYSTEM consists of three main components: DATABASE, API, and USER INTERFACE.
The DATABASE component stores all the data required for the system.
The API component provides an interface for the USER INTERFACE to interact with the DATABASE.
The USER INTERFACE component is the part of the system that the user interacts with.

Example overly simple component description:
DATABASE is responsible for storing data in a structured manner. It uses a relational database management system.
"""

# Initial System Design Prompt (for first design without validation feedback)
initial_design_prompt = """
You are designing the initial system architecture for a software project.
Your approach is top-down, breaking the system into components that will be refined iteratively.
This is the first architectural design based on the project requirements and user stories.

""" + system_description_format + """

**Project Description:**
{project_description}

**Project Requirements:**
{requirements}

**User Stories:**
{user_stories}

**Instructions:**
1. Create an initial system design description based on the project materials. Mark components in CAPITAL LETTERS.
2. Provide component descriptions with technical details for each component.
3. Include considerations for both functional requirements (core features) and non-functional requirements (security, performance, scalability).
4. Focus on a clean separation of concerns between components.
5. Document key architectural decisions and their rationale.

{format_instructions}
"""

# Redesign Architecture Prompt (for subsequent designs with validation feedback)
redesign_architecture_prompt = """
You are redesigning a system architecture for a software project based on validation feedback.
Your task is to modify the architecture to address identified issues while maintaining what works well.

""" + system_description_format + """

**Project Description:**
{project_description}

**Project Requirements:**
{requirements}

**User Stories:**
{user_stories}

**Current System Description:**
{system_description}

**Current Component Descriptions:**
{component_descriptions}

**Validation Feedback:**
{validation_feedback}

**Instructions:**
1. Carefully analyze the validation feedback and determine what level of architectural changes are needed:
   - For major architectural issues: Make significant structural changes to address fundamental problems
   - For minor issues: Make smaller adjustments while preserving the overall structure
   - If no significant changes are needed: Simply refine and clarify the existing architecture

2. Update the system description, marking components in CAPITAL LETTERS.
3. Provide updated component descriptions with technical details for each component.
4. Document what changes you made from the previous version and why.
5. Focus on addressing the specific issues identified in the validation feedback.

{format_instructions}
"""

# Single User Story Validation Prompt (for parallel processing)
validate_user_story_prompt = """
You are validating a system architecture design against a specific user story.
Your task is to assess whether the current design adequately supports this single user story.

""" + system_description_format + """

**Project Description:**
{project_description}

**Project Requirements:**
{requirements}

**Current System Description:**
{system_description}

**Component Descriptions:**
{component_descriptions}

**User Story to Validate:**
{user_story}

**Instructions:**
1. Create a step-by-step sequence showing how the system would fulfill this specific user story.
2. Identify the components that would be involved in each step.
3. Evaluate whether the current design adequately supports this user story:
   - What aspects of the design work well for this story?
   - Are there any missing components or interactions needed?
   - Are there any architectural issues that prevent fully supporting this story?

4. Categorize any identified issues as:
   - Major architectural issues (fundamental problems requiring significant redesign)
   - Minor implementation issues (can be addressed with targeted refinements)

5. Provide a final verdict on whether this specific user story is adequately supported.
6. Include specific, actionable feedback on how to better support this user story.

{format_instructions}
"""