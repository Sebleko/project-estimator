from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Dict, Union, Literal
import re

# 1. Schema for Requirements and User Stories Generation
class UserStory(BaseModel):
    role: str = Field(..., description="The type of user in the story (e.g., 'administrator', 'customer')")
    goal: str = Field(..., description="What the user wants to accomplish")
    reason: str = Field(..., description="Why the user wants to accomplish this goal")
    
    def formatted(self) -> str:
        """Return formatted user story in standard format"""
        return f"As a {self.role}, I want {self.goal} so that {self.reason}"

class RequirementsAndStoriesOutput(BaseModel):
    project_description: str = Field(
        ..., 
        description="A clear, concise description of the project that defines its scope and purpose"
    )
    requirements: List[str] = Field(
        ...,
        description="List of specific, actionable requirements that define what the system must do"
    )
    user_stories: List[UserStory] = Field(
        ...,
        description="User stories that capture functionality from an end-user perspective (minimum 1 stories required)",
        min_length=1
    )
    clarification_questions: Optional[List[str]] = Field(
        None,
        description="Questions to ask the customer to clarify requirements (maximum 3 questions)",
        max_length=3
    )
    
    @model_validator(mode='after')
    def validate_minimum_stories(self) -> 'RequirementsAndStoriesOutput':
        """Validate that at least 1 user stories are provided."""
        if len(self.user_stories) < 1:
            raise ValueError("At least 1 user stories must be provided to ensure comprehensive coverage")
        return self

# 2. Schema for Question Answer Integration
class IntegratedRequirementsAndStoriesOutput(BaseModel):
    project_description: str = Field(
        ..., 
        description="Updated project description incorporating customer's answers to clarification questions"
    )
    requirements: List[str] = Field(
        ...,
        description="Finalized list of requirements incorporating insights from clarification answers"
    )
    user_stories: List[UserStory] = Field(
        ...,
        description="Updated user stories aligned with the finalized requirements (minimum 3 stories required)"
    )
    
    @model_validator(mode='after')
    def validate_minimum_stories(self) -> 'IntegratedRequirementsAndStoriesOutput':
        """Validate that at least 3 user stories are provided."""
        if len(self.user_stories) < 3:
            raise ValueError("At least 3 user stories must be provided to ensure comprehensive coverage")
        return self

# 3. Schema for Initial System Design
class Component(BaseModel):
    name: str = Field(
        ...,
        description="Name of the component (should be in CAPITAL LETTERS in system description)"
    )
    description: str = Field(
        ...,
        description="Detailed technical description of the component and its responsibilities"
    )
    technologies: Optional[List[str]] = Field(
        None,
        description="Optional list of suggested technologies or standards for implementing this component"
    )

class InitialSystemDesignOutput(BaseModel):
    system_description: str = Field(
        ...,
        description="Narrative description of the overall system, its components and their interactions, with components in CAPITAL LETTERS"
    )
    components: List[Component] = Field(
        ...,
        description="Detailed descriptions of each component mentioned in the system description"
    )
    
    @model_validator(mode='after')
    def validate_components(self) -> 'InitialSystemDesignOutput':
        """Validate that all component names appear in the system description and that all components are described."""
        for component in self.components:
            if component.name not in self.system_description:
                raise ValueError(f"Component {component.name} is not mentioned in the system description")
            
        # Regex to find all components in the system description
        components_found = re.findall(r'[A-Z]+', self.system_description)
        components_found = list(set(components_found))
        for component in components_found:
            if component not in [c.name for c in self.components]:
                raise ValueError(f"Component {component} is missing from the component descriptions")
        return self

# 4. Schema for Component Refinement
class RefinedComponentsOutput(BaseModel):
    system_description: str = Field(
        ...,
        description="Updated system description with components broken down into sub-components where appropriate"
    )
    components: List[Component] = Field(
        ...,
        description="Updated and expanded list of component descriptions, including new sub-components"
    )
    refinement_rationale: Optional[List[str]] = Field(
        None,
        description="Optional explanation of why certain components were broken down further"
    )
    needs_further_refinement: bool = Field(
        ...,
        description="Whether the architect recommends another refinement iteration"
    )
    
    @model_validator(mode='after')
    def validate_components(self) -> 'RefinedComponentsOutput':
        """Validate that all component names appear in the system description."""
        for component in self.components:
            if component.name not in self.system_description:
                raise ValueError(f"Component {component.name} is not mentioned in the system description")
        
        components_found = re.findall(r'[A-Z]+', self.system_description)
        components_found = list(set(components_found))
        for component in components_found:
            if component not in [c.name for c in self.components]:
                raise ValueError(f"Component {component} is missing from the component descriptions")
        return self

# 5. Schema for User Story Validation
class UserStoryValidationOutput(BaseModel):
    execution_path: List[str] = Field(
        ...,
        description="Step-by-step sequence showing how the system fulfills the user story"
    )
    involved_components: List[str] = Field(
        ...,
        description="Names of components involved in fulfilling the user story"
    )
    strengths: List[str] = Field(
        ...,
        description="Aspects of the current design that effectively support this user story"
    )
    weaknesses: List[str] = Field(
        ...,
        description="Gaps or issues in the current design related to this user story"
    )
    improvement_suggestions: List[str] = Field(
        ...,
        description="Specific suggestions to improve the architecture for this user story"
    )
    is_satisfied: bool = Field(
        ...,
        description="Whether the current design adequately supports this user story"
    )
    assessment_summary: str = Field(
        ...,
        description="Brief summary explaining why the user story is or isn't adequately supported"
    )

# 6. Schema for System Improvement
class ImprovedSystemOutput(BaseModel):
    system_description: str = Field(
        ...,
        description="Updated system description addressing the gaps identified in user story validations"
    )
    components: List[Component] = Field(
        ...,
        description="Updated component descriptions reflecting architectural improvements"
    )
    addressed_issues: Dict[str, str] = Field(
        ...,
        description="Mapping of identified issues to how they were addressed in the improved design"
    )
    needs_further_improvement: bool = Field(
        ...,
        description="Whether the architect recommends another improvement iteration"
    )
    
    @model_validator(mode='after')
    def validate_components(self) -> 'ImprovedSystemOutput':
        """Validate that all component names appear in the system description."""
        for component in self.components:
            if component.name not in self.system_description:
                raise ValueError(f"Component {component.name} is not mentioned in the system description")
        return self

# 7. Schema for Final Architecture Assessment
class ArchitectureAssessmentOutput(BaseModel):
    requirement_coverage: Dict[str, bool] = Field(
        ...,
        description="Mapping of requirements to whether they are adequately addressed by the architecture"
    )
    user_story_coverage: Dict[str, bool] = Field(
        ...,
        description="Mapping of user stories to whether they are adequately supported by the architecture"
    )
    strengths: List[str] = Field(
        ...,
        description="Strengths of the architecture design"
    )
    issues: List[str] = Field(
        ...,
        description="Remaining issues or gaps in the architecture"
    )
    verdict: Literal["Ready for Implementation", "Requires Further Refinement"] = Field(
        ...,
        description="Final verdict on whether the architecture is ready for implementation"
    )
    implementation_considerations: List[str] = Field(
        ...,
        description="Important points to consider during implementation"
    )

# 8. Schema for Architecture Refinement
class RefinedArchitectureOutput(BaseModel):
    system_description: str = Field(
        ...,
        description="Updated system description that addresses the issues identified in the assessment"
    )
    components: List[Component] = Field(
        ...,
        description="Updated component descriptions reflecting the refinements"
    )
    issue_resolutions: Dict[str, str] = Field(
        ...,
        description="Mapping of each identified issue to an explanation of how it was resolved"
    )
    side_effects: Optional[List[str]] = Field(
        None,
        description="Any side effects or trade-offs resulting from the refinements made"
    )
    needs_further_refinement: bool = Field(
        ...,
        description="Whether the architect recommends another refinement iteration"
    )
    
    @model_validator(mode='after')
    def validate_components(self) -> 'RefinedArchitectureOutput':
        """Validate that all component names appear in the system description."""
        for component in self.components:
            if component.name not in self.system_description:
                raise ValueError(f"Component {component.name} is not mentioned in the system description")
        return self