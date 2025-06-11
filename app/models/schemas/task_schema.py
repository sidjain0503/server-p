"""
Task Schema Definition

Task and project management schema with comprehensive field definitions
for task tracking, priority management, and project organization.
"""

from app.meta_engine.schema_definition import (
    SchemaDefinition, FieldDefinition, FieldType, 
    ValidationRule, PermissionLevel, CommonFields
)


def get_task_schema() -> SchemaDefinition:
    """
    Get the Task schema definition.
    
    This schema represents a task with all necessary fields
    for project management, priority tracking, and status updates.
    
    Returns:
        SchemaDefinition: Complete task schema definition
    """
    return SchemaDefinition(
        name="Task",
        title="Task",
        description="Task and project management",
        fields=[
            FieldDefinition(
                name="title",
                field_type=FieldType.STRING,
                required=True,
                max_length=200,
                description="Task title"
            ),
            FieldDefinition(
                name="description",
                field_type=FieldType.TEXT,
                description="Detailed task description"
            ),
            FieldDefinition(
                name="priority",
                field_type=FieldType.CHOICE,
                choices=[
                    {"value": "low", "label": "Low"},
                    {"value": "medium", "label": "Medium"},
                    {"value": "high", "label": "High"},
                    {"value": "critical", "label": "Critical"}
                ],
                default="medium",
                required=True,
                description="Task priority level"
            ),
            FieldDefinition(
                name="status",
                field_type=FieldType.CHOICE,
                choices=[
                    {"value": "todo", "label": "Todo"},
                    {"value": "in_progress", "label": "In Progress"},
                    {"value": "review", "label": "Review"},
                    {"value": "done", "label": "Done"},
                    {"value": "cancelled", "label": "Cancelled"}
                ],
                default="todo",
                required=True,
                description="Current task status"
            ),
            FieldDefinition(
                name="due_date",
                field_type=FieldType.DATETIME,
                description="Task due date and time"
            ),
            FieldDefinition(
                name="estimated_hours",
                field_type=FieldType.FLOAT,
                min_value=0.1,
                description="Estimated hours to complete"
            ),
            FieldDefinition(
                name="labels",
                field_type=FieldType.MULTI_CHOICE,
                choices=[
                    {"value": "urgent", "label": "Urgent"},
                    {"value": "important", "label": "Important"},
                    {"value": "bug", "label": "Bug"},
                    {"value": "feature", "label": "Feature"},
                    {"value": "enhancement", "label": "Enhancement"}
                ],
                description="Task labels"
            ),
            FieldDefinition(
                name="is_urgent",
                field_type=FieldType.BOOLEAN,
                default=False,
                description="Whether task is urgent"
            )
        ],
        enable_timestamps=True,
        enable_audit=True,
        enable_soft_delete=True
    ) 