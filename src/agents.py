import asyncio
from typing import Any, Dict
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.types import interrupt, Command
import tiktoken
from langgraph.checkpoint.memory import MemorySaver


from state import State, save_design_snapshot, increment_iteration, log_error

# Import the new prompts
from prompts import (
    requirements_and_stories_prompt,
    question_answer_integration_prompt,
    initial_system_design_prompt,
    component_refinement_prompt,
    user_story_validation_prompt,
    system_improvement_prompt,
    final_architecture_assessment_prompt,
    architecture_refinement_prompt
)

# Import the new schemas
from schemas import (
    RequirementsAndStoriesOutput,
    IntegratedRequirementsAndStoriesOutput,
    InitialSystemDesignOutput,
    RefinedComponentsOutput,
    UserStoryValidationOutput,
    ImprovedSystemOutput,
    ArchitectureAssessmentOutput,
    RefinedArchitectureOutput,
)

llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

def count_tokens(prompt_text: str, completion_text: str = "", model_name: str = "gpt-4o-mini") -> int:
    encoder = tiktoken.get_encoding("cl100k_base")
    prompt_tokens = len(encoder.encode(prompt_text))
    completion_tokens = len(encoder.encode(completion_text))
    return prompt_tokens + completion_tokens

async def call_llm(prompt_template: str, input_data: Dict[str, Any], schema):
    """
    Calls the LLM with a prompt and parses the output using the specified Pydantic schema.
    Returns a tuple: (parsed_output, tokens_used).
    """
    parser = JsonOutputParser(pydantic_object=schema)
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=[k for k in input_data.keys() if isinstance(input_data[k], str)],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    # Filter out non-string items from the final format
    text_input = {k: v for k, v in input_data.items() if isinstance(v, str)}
    prompt_text = prompt.format(**text_input)

    # Chain the prompt -> LLM -> parser
    output_obj = await (prompt | llm | parser).ainvoke(text_input)
    completion_text = str(output_obj)

    tokens_used = count_tokens(prompt_text, completion_text)
    return output_obj, tokens_used
    
async def process_initial_requirements(state: State) -> State:
    """Process initial project description to extract requirements and user stories."""
    try:
        input_data = {
            "project_description": state.project_description
        }
        
        output, _ = await call_llm(
            requirements_and_stories_prompt, 
            input_data,
            RequirementsAndStoriesOutput
        )
        
        # Update state with the processed requirements and stories
        new_state = state.copy()
        new_state.generated_project_description = output.project_description
        new_state.requirements = output.requirements
        new_state.user_stories = output.user_stories
        new_state.clarification_questions = output.clarification_questions or []
        
        return new_state
    except Exception as e:
        # Log error and return original state
        error_msg = f"Error in requirements analysis: {str(e)}"
        return log_error(state, error_msg)

async def integrate_customer_answers(state: State) -> State:
    """Integrate customer answers to clarification questions into requirements."""
    try:
        questions = state.clarification_questions
        if not questions:
            raise ValueError("No clarification questions to integrate")
        
        answer_by_question = interrupt({ "interrupt_type": "questions", "questions": questions})
        if not answer_by_question.values():
            raise ValueError("No answers provided for clarification questions")
        
        # Format the questions and answers
        qa_text = "\n".join([
            f"Q: {q}\nA: {answer_by_question.get(q, 'No answer provided')}" 
            for q in state.clarification_questions
        ])
        
        input_data = {
            "project_description": state.project_description,
            "project_description_generated": state.generated_project_description,
            "requirements": "\n".join([f"- {r}" for r in state.requirements]),
            "user_stories": "\n".join([s.formatted() for s in state.user_stories]),
            "questions_and_answers": qa_text
        }
        
        output, _ = await call_llm(
            question_answer_integration_prompt, 
            input_data,
            IntegratedRequirementsAndStoriesOutput
        )
        
        # Update state
        new_state = state.copy()
        new_state.generated_project_description = output.project_description
        new_state.requirements = output.requirements
        new_state.user_stories = output.user_stories
        
        return new_state
    except Exception as e:
        error_msg = f"Error integrating customer answers: {str(e)}"
        return log_error(state, error_msg)

async def create_initial_system_design(state: State) -> State:
    """Create the initial system architecture design."""
    try:
        # Format user stories for prompt
        user_stories_text = "\n".join([s.formatted() for s in state.user_stories])
        
        input_data = {
            "project_description": state.generated_project_description,
            "requirements": "\n".join([f"- {r}" for r in state.requirements]),
            "user_stories": user_stories_text
        }
        
        output, _ = await call_llm(
            initial_system_design_prompt, 
            input_data,
            InitialSystemDesignOutput
        )
        
        # Update state
        new_state = state.copy()
        new_state.system_description = output.system_description
        new_state.components = output.components
        
        # Save initial design to history
        return save_design_snapshot(new_state)
    except Exception as e:
        error_msg = f"Error creating initial design: {str(e)}"
        return log_error(state, error_msg)

async def refine_components(state: State) -> State:
    """Refine components by breaking them down into sub-components."""
    try:
        # Format user stories for prompt
        user_stories_text = "\n".join([s.formatted() for s in state.user_stories])
        
        # Format component descriptions
        component_descriptions = "\n\n".join([f"{c.name}:\n{c.description}" for c in state.components])
        
        input_data = {
            "project_description": state.generated_project_description,
            "requirements": "\n".join([f"- {r}" for r in state.requirements]),
            "user_stories": user_stories_text,
            "system_description": state.system_description,
            "component_descriptions": component_descriptions
        }
        
        output, _ = await call_llm(
            component_refinement_prompt, 
            input_data,
            RefinedComponentsOutput
        )
        
        # Update state
        new_state = save_design_snapshot(state)
        new_state.system_description = output.system_description
        new_state.components = output.components
        new_state.needs_further_refinement = output.needs_further_refinement
        
        # Increment iteration counter
        new_state = increment_iteration(new_state, "component_refinement")
        
        return new_state
    except Exception as e:
        error_msg = f"Error refining components: {str(e)}"
        return log_error(state, error_msg)

async def validate_user_stories(state: State) -> State:
    """Validate all user stories in parallel against the current system design."""
    try:
        # Format component descriptions
        component_descriptions = "\n\n".join([f"{c.name}:\n{c.description} {c.technologies or ""}" for c in state.components])
        
        # Process all user stories in parallel
        validation_tasks = []
        story_keys = []
        
        for story in state.user_stories:
            story_key = story.formatted()
            story_keys.append(story_key)
                
            input_data = {
                "project_description": state.generated_project_description,
                "requirements": "\n".join([f"- {r}" for r in state.requirements]),
                "system_description": state.system_description,
                "component_descriptions": component_descriptions,
                "user_story": story_key
            }
            
            validation_tasks.append(
                call_llm(user_story_validation_prompt, input_data, UserStoryValidationOutput)
            )
        
        # Run all validation tasks in parallel
        validation_results = await asyncio.gather(*validation_tasks, return_exceptions=True)
        
        # Update state with validation results
        new_state = state.copy()
        new_state.story_validations = {}  # Clear previous validations
        
        # Check if we got validation results for all stories
        all_validated = True
        
        for i, result in enumerate(validation_results):
            if isinstance(result, Exception):
                # Handle error for this specific story
                error_msg = f"Error validating story '{story_keys[i]}': {str(result)}"
                new_state = log_error(new_state, error_msg)
                all_validated = False
            else:
                output, _ = result
                story_key = story_keys[i]
                new_state.story_validations[story_key] = output
        
        # If we couldn't validate any stories, raise an error
        if len(new_state.story_validations) == 0:
            raise RuntimeError("Failed to validate any user stories")
            
        return new_state
    except Exception as e:
        error_msg = f"Error in story validation: {str(e)}"
        return log_error(state, error_msg)

async def improve_system(state: State) -> State:
    """Improve the system based on validation feedback."""
    try:
        # Format the validation feedback
        validations_text = ""
        for i, story in enumerate(state.user_stories):
            story_text = story.formatted()
            validation = state.story_validations.get(story_text)
            if validation: #and not validation.is_satisfied:
                validations_text += f"User Story {i+1}: {story_text}\n"
                validations_text += f"Satisfied: {validation.is_satisfied}\n"
                validations_text += f"Strengths: {', '.join(validation.strengths)}\n"
                validations_text += f"Weaknesses: {', '.join(validation.weaknesses)}\n"
                validations_text += f"Suggestions: {', '.join(validation.improvement_suggestions)}\n"
                validations_text += f"Assessment: {validation.assessment_summary}\n\n"
        
        # Format component descriptions
        component_descriptions = "\n\n".join([f"{c.name}:\n{c.description} {c.technologies}" for c in state.components])
        
        input_data = {
            "system_description": state.system_description,
            "component_descriptions": component_descriptions,
            "user_stories_and_critique": validations_text
        }
        
        output, _ = await call_llm(
            system_improvement_prompt, 
            input_data,
            ImprovedSystemOutput
        )
        
        # Update state
        new_state = save_design_snapshot(state)
        new_state.system_description = output.system_description
        new_state.components = output.components
        new_state.needs_further_refinement = output.needs_further_improvement  # Corrected field name
        
        # Since we've improved the system, we need to revalidate all user stories
        new_state.story_validations = {}
        
        # Increment iteration counter
        new_state = increment_iteration(new_state, "system_improvement")
        
        return new_state
    except Exception as e:
        error_msg = f"Error improving system: {str(e)}"
        return log_error(state, error_msg)

async def assess_architecture(state: State) -> State:
    """Conduct a final assessment of the architecture."""
    try:
        # Format user stories for prompt
        user_stories_text = "\n".join([s.formatted() for s in state.user_stories])
        
        # Format component descriptions
        component_descriptions = "\n\n".join([f"{c.name}:\n{c.description}" for c in state.components])
        
        input_data = {
            "project_description": state.generated_project_description,
            "requirements": "\n".join([f"- {r}" for r in state.requirements]),
            "user_stories": user_stories_text,
            "system_description": state.system_description,
            "component_descriptions": component_descriptions
        }
        
        output, _ = await call_llm(
            final_architecture_assessment_prompt, 
            input_data,
            ArchitectureAssessmentOutput
        )
        
        # Update state
        new_state = state.copy()
        new_state.assessment_result = output
        
        # The needs_further_refinement is derived from the assessment verdict
        new_state.needs_further_refinement = (output.verdict == "Requires Further Refinement")
        
        return new_state
    except Exception as e:
        error_msg = f"Error assessing architecture: {str(e)}"
        return log_error(state, error_msg)

async def refine_architecture(state: State) -> State:
    """Refine the architecture based on assessment findings."""
    try:
        if not state.assessment_result:
            raise ValueError("Cannot refine architecture without assessment result")
        
        # Format user stories for prompt
        user_stories_text = "\n".join([s.formatted() for s in state.user_stories])
        
        # Format component descriptions
        component_descriptions = "\n\n".join([f"{c.name}:\n{c.description}" for c in state.components])
        
        # Format assessment findings
        assessment_findings = "\n".join([f"- {issue}" for issue in state.assessment_result.issues])
        
        input_data = {
            "project_description": state.generated_project_description,
            "requirements": "\n".join([f"- {r}" for r in state.requirements]),
            "user_stories": user_stories_text,
            "system_description": state.system_description,
            "component_descriptions": component_descriptions,
            "assessment_findings": assessment_findings
        }
        
        output, _ = await call_llm(
            architecture_refinement_prompt, 
            input_data,
            RefinedArchitectureOutput
        )
        
        # Update state
        new_state = save_design_snapshot(state)
        new_state.system_description = output.system_description
        new_state.components = output.components
        new_state.needs_further_refinement = output.needs_further_refinement
        
        # Since we've refined the architecture, clear validation results
        new_state.story_validations = {}
        
        # Increment iteration counter
        new_state = increment_iteration(new_state, "architecture_refinement")
        
        return new_state
    except Exception as e:
        error_msg = f"Error refining architecture: {str(e)}"
        return log_error(state, error_msg)

# Edge condition functions - these determine the next step in the workflow

def check_if_clarification_needed(state: State) -> str:
    """Determine if clarification questions need to be asked."""
    if state.error_log:
        return "end"  # End on errors
    if state.clarification_questions:
        return "clarification"
    else:
        return "initial_design"

def check_component_refinement_loop(state: State) -> str:
    """Determine if component refinement should continue."""
    if state.error_log:
        return "end"  # End on errors
    
    # Continue if the architect recommends it AND we haven't hit the max iterations
    if (state.needs_further_refinement and 
        state.iterations["component_refinement"] < 10):
        return "refine_components"
    else:
        return "validate_stories"

def check_validation_results(state: State) -> str:
    """Determine next step based on validation results."""
    if state.error_log:
        return "end"  # End on errors
    
    # Verify we have validation results for all user stories
    story_keys = {story.formatted() for story in state.user_stories}
    validation_keys = set(state.story_validations.keys())
    
    # If we're missing validations, log an error and end
    if not validation_keys.issuperset(story_keys):
        missing = story_keys - validation_keys
        state = log_error(state, f"Missing validation results for stories: {missing}")
        return "end"
    
    # Check if any stories are unsatisfied
    any_unsatisfied = any(
        not validation.is_satisfied 
        for validation in state.story_validations.values()
    )
    
    if any_unsatisfied:
        return "improve_system"  # Need improvement because some stories aren't satisfied
    else:
        return "final_assessment"  # All stories satisfied, skip improvement

def check_system_improvement_loop(state: State) -> str:
    """Determine next step after system improvement."""
    if state.error_log:
        return "end"  # End on errors
    
    # After improvement, if architect recommends more improvements and we haven't hit limit
    if (state.needs_further_refinement and 
        state.iterations["system_improvement"] < 10):
        return "improve_system"  # Continue improving
    else:
        return "validate_stories"  # Validate to see if improvements fixed the issues

def check_architecture_outcome(state: State) -> str:
    """Unified function to determine next step after assessment or refinement."""
    if state.error_log:
        return "end"  # End on errors
    
    # If no assessment result, exit with error
    if not state.assessment_result:
        state = log_error(state, "Missing assessment result")
        return "end"
    
    # If architecture needs refinement and we haven't hit the limit
    if (state.needs_further_refinement and 
        state.iterations["architecture_refinement"] < 2):
        return "refine_architecture"
    else:
        # If we've hit max refinements but architecture still needs work, log this
        if (state.needs_further_refinement and 
            state.iterations["architecture_refinement"] >= 2):
            state = log_error(state, "Hit maximum architecture refinement iterations but still needs work")
        return "end"

# Build the workflow graph
def build_architecture_design_graph():
    """Create the LangGraph workflow for the architecture design process."""
    
    # Create a new graph
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("initial_requirements", process_initial_requirements)
    workflow.add_node("integrate_answers", integrate_customer_answers)
    workflow.add_node("initial_design", create_initial_system_design)
    workflow.add_node("refine_components", refine_components)
    workflow.add_node("validate_stories", validate_user_stories)
    workflow.add_node("improve_system", improve_system)
    workflow.add_node("final_assessment", assess_architecture)
    workflow.add_node("refine_architecture", refine_architecture)
    
    # Add conditional edges with error handling
    workflow.add_conditional_edges(
        "initial_requirements",
        check_if_clarification_needed,
        {
            "clarification": "integrate_answers",
            "initial_design": "initial_design",
            "end": END  # Terminal state
        }
    )
    
    workflow.add_conditional_edges(
        "integrate_answers",
        lambda state: "end" if state.error_log else "initial_design",
        {
            "initial_design": "initial_design",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "initial_design",
        lambda state: "end" if state.error_log else "refine_components",
        {
            "refine_components": "refine_components",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "refine_components",
        check_component_refinement_loop,
        {
            "refine_components": "refine_components",
            "validate_stories": "validate_stories",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "validate_stories",
        check_validation_results,
        {
            "improve_system": "improve_system",
            "final_assessment": "final_assessment",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "improve_system",
        check_system_improvement_loop,
        {
            "improve_system": "improve_system",
            "validate_stories": "validate_stories",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "final_assessment",
        check_architecture_outcome,
        {
            "refine_architecture": "refine_architecture",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "refine_architecture", 
        lambda state: check_validation_results(state) if not state.error_log else "end",
        {
            "improve_system": "improve_system", 
            "final_assessment": "final_assessment",
            "end": END
        }
    )
    
    # Set the entry point
    workflow.set_entry_point("initial_requirements")
    
    return workflow

# Entry point function to execute the workflow
async def design_system_architecture(project_description: str, questions_and_answers: Dict[str, str] = None):
    """
    Execute the architecture design workflow for a given project description.
    
    Args:
        project_description: The free-form project description from the customer
        questions_and_answers: Optional dictionary of answers to clarification questions
        
    Returns:
        The final state of the workflow
    """
    # Create initial state
    initial_state = State(
        project_description=project_description,
        questions_and_answers=questions_and_answers or {}
    )
    
    # Build and compile the workflow
    workflow = build_architecture_design_graph()
    thread_config = {"configurable": {"thread_id": "1"}}
    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer)
    
    # Execute the workflow
    try:
        result = await app.ainvoke(initial_state, config=thread_config)
        state = app.get_state(thread_config)
        tasks = state.tasks[0].interrupts[0].value

        final_state = None

        if tasks["interrupt_type"] == "questions":
            answers = {}
            for question in tasks["questions"]:
                print(f"Question: {question}")
                answer = input("Answer: ")
                answers[question] = answer

            final_state = await app.ainvoke(Command(resume=answer), config=thread_config)
        else:
            final_state = result
        


        return final_state
    except Exception as e:
        # Handle any top-level errors
        error_state = log_error(initial_state, f"Workflow execution failed: {str(e)}")
        return error_state