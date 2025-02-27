from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from langgraph import State as LanggraphState
from schemas import (
    UserStory,
    Component,
    UserStoryValidationOutput,
    ArchitectureAssessmentOutput,
)

class State(LanggraphState):
    """State for the Software Design Architecture workflow."""
    
    # Initial inputs
    project_description: str = Field(
        default="",
        description="The original project description provided by the customer"
    )
    
    # Generated/refined project understanding
    generated_project_description: str = Field(
        default="",
        description="The generated project description based on the original customer input"
    )
    requirements: List[str] = Field(
        default_factory=list,
        description="List of requirements for the project"
    )
    user_stories: List[UserStory] = Field(
        default_factory=list,
        description="List of user stories derived from requirements"
    )
    
    # Clarification process
    clarification_questions: List[str] = Field(
        default_factory=list,
        description="Questions to ask the customer for clarification"
    )
    questions_and_answers: Dict[str, str] = Field(
        default_factory=dict,
        description="Dictionary mapping questions to customer's answers"
    )
    
    # System design
    system_description: str = Field(
        default="",
        description="Description of the system architecture with components in CAPITAL LETTERS"
    )
    components: List[Component] = Field(
        default_factory=list,
        description="Detailed descriptions of each component in the system"
    )
    
    # Validation results (for all user stories)
    story_validations: Dict[str, UserStoryValidationOutput] = Field(
        default_factory=dict,
        description="Validation results for each user story"
    )
    
    # Assessment and refinement
    assessment_result: Optional[ArchitectureAssessmentOutput] = Field(
        default=None,
        description="Final assessment of the architecture"
    )
    
    # Refinement decisions - each node explicitly indicates if it wants another iteration
    needs_further_refinement: bool = Field(
        default=False,
        description="Whether the current step suggests further refinement"
    )
    
    # Iteration counters - hard limits on iterations
    iterations: Dict[str, int] = Field(
        default_factory=lambda: {
            "component_refinement": 0,
            "system_improvement": 0,
            "architecture_refinement": 0
        },
        description="Count of iterations for each iterative stage"
    )

    # Error handling
    error_log: List[str] = Field(
        default_factory=list,
        description="Log of errors encountered during processing"
    )
    
    # Historical versions for comparison
    design_history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="History of system designs for comparison and rollback if needed"
    )

# Helper functions for state transitions

def save_design_snapshot(state: State) -> State:
    """Save the current design to history before making changes."""
    snapshot = {
        "system_description": state.system_description,
        "components": state.components.copy(),
        "iterations": state.iterations.copy()
    }
    
    # Create a new state with updated history
    new_state = state.copy()
    new_state.design_history.append(snapshot)
    return new_state

def increment_iteration(state: State, stage_name: str) -> State:
    """Increment the iteration counter for a specific stage."""
    new_state = state.copy()
    if stage_name in new_state.iterations:
        new_state.iterations[stage_name] += 1
    return new_state

def log_error(state: State, error_message: str) -> State:
    """Add an error message to the error log."""
    new_state = state.copy()
    new_state.error_log.append(error_message)
    return new_state