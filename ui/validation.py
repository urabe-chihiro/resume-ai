"""Input validation functions."""

from typing import Tuple, List


def validate_user_input(user_data: dict) -> Tuple[bool, List[str]]:
    """Validate user input data.
    
    Args:
        user_data: User input dictionary
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Required fields
    if not user_data.get("name"):
        errors.append("氏名は必須です")
    
    if not user_data.get("email"):
        errors.append("メールアドレスは必須です")
    elif "@" not in user_data["email"]:
        errors.append("有効なメールアドレスを入力してください")
    
    # At least one work experience
    if not user_data.get("work_experiences"):
        errors.append("少なくとも1つの職務経歴を入力してください")
    
    return len(errors) == 0, errors


def validate_job_requirements(job_data: dict) -> Tuple[bool, List[str]]:
    """Validate job requirements data.
    
    Args:
        job_data: Job requirements dictionary
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Required fields
    if not job_data.get("job_title"):
        errors.append("職種は必須です")
    
    company_info = job_data.get("company_info", {})
    if not company_info.get("name"):
        errors.append("企業名は必須です")
    
    if not job_data.get("job_description"):
        errors.append("職務内容は必須です")
    
    return len(errors) == 0, errors
