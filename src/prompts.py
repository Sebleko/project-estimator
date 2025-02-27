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

Throughout the design process, you will refine the system description and divide components into smaller sub-components as needed.
"""

# 3) Initial System Design Prompt
initial_system_design_prompt = """
You are designing a system architecture for a software project.
Your approach is top-down, breaking the system into components that will be refined iteratively.
You are working with a project description, requirements, and user stories.

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

{format_instructions}
"""

# 4) Component Refinement Prompt
component_refinement_prompt = """
You are refining a system architecture for a software project.
In the previous step, you created an initial system design with component descriptions.
Now, you will iteratively break down components into smaller, more focused sub-components.

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

**Instructions:**
1. Analyze the current system design and identify components that would benefit from further breakdown.
2. Break down identified components into logical sub-components.
3. Update the system description to reflect these refinements.
4. Provide detailed descriptions for all components, including the new sub-components.
5. Ensure the refined architecture remains cohesive and aligned with requirements.
6. Only make incremental, intuitive refinements - don't completely restructure the design.

{format_instructions}
"""

# 5) User Story Validation Prompt
user_story_validation_prompt = """
You are validating a system architecture design against a specific user story.
Your task is to assess whether the current design supports the user story and identify any gaps.

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
1. Create a step-by-step sequence showing how the system would fulfill this user story.
2. Identify any components that would be involved in each step.
3. Critique the design based on this user story - what works well and what's missing?
4. Suggest specific improvements to better support this user story.
5. Provide a clear assessment: Does the current design adequately support this user story? Why or why not?

{format_instructions}
"""

# 6) System Improvement Prompt
system_improvement_prompt = """
You are refining a system architecture based on validation feedback.
In the previous steps, the system design was validated against all user stories and received critique.
Your task is to improve the architecture to address identified gaps and weaknesses.

""" + system_description_format + """

**Current System Description:**
{system_description}

**Current Component Descriptions:**
{component_descriptions}

**Validation Feedback from User Stories:**
{user_stories_and_critique}

**Instructions:**
1. Analyze the validation feedback across all user stories.
2. Identify patterns of gaps or weaknesses in the current design.
3. Update the system description to address these issues.
4. Revise component descriptions to reflect these improvements.
5. Ensure the improved architecture addresses all identified gaps while maintaining clean architectural principles.
6. Focus on architectural concerns rather than implementation details.

{format_instructions}
"""

# 7) Final Architecture Assessment Prompt
final_architecture_assessment_prompt = """
You are conducting a final assessment of a system architecture.
The architecture has gone through several rounds of refinement and validation.
Your task is to evaluate the design for completeness, coherence, and alignment with requirements.

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

**Instructions:**
1. Assess whether the architecture addresses all requirements and user stories.
2. Evaluate the architecture for clarity, cohesion, and separation of concerns.
3. Identify any remaining gaps or potential issues.
4. Provide a final verdict on the architecture's readiness for implementation - either "Ready for Implementation" or "Requires Further Refinement".
5. If further refinement is needed, clearly list the specific issues that need to be addressed.
6. Include a summary of the architecture's strengths and any areas that might need attention during implementation.

{format_instructions}
"""

# 8) Architecture Refinement Based on Final Assessment
architecture_refinement_prompt = """
You are refining a system architecture based on an expert assessment.
The architecture has undergone a comprehensive review that identified specific issues needing attention.
Your task is to address these issues and produce an improved architecture.

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

**Assessment Findings:**
{assessment_findings}

**Instructions:**
1. Address each issue identified in the assessment findings.
2. Update the system description and component descriptions accordingly.
3. Ensure your changes resolve the identified issues while maintaining the overall architectural integrity.
4. If addressing one issue impacts other areas of the design, make sure to update those areas as well.
5. Provide a brief explanation of how each issue was addressed in your revised architecture.

{format_instructions}
"""