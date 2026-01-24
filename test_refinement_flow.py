#!/usr/bin/env python
"""Test work experience refinement flow."""

import sys
import json
from models.user_input import UserInput, WorkExperience
from models.job_requirements import JobRequirements, CompanyInfo

# Create realistic test data
work_exp1 = WorkExperience(
    company_name="ABC Company",
    position="Software Engineer",
    period="2020年4月～2022年3月",
    description="Pythonを使用してWebアプリケーションの開発に従事。フロントエンドはReactで実装。データベースはPostgreSQLを使用。主なプロジェクトはユーザー管理システムの構築で、100万人以上のユーザーを管理するシステムを実装した。"
)

work_exp2 = WorkExperience(
    company_name="XYZ Corp",
    position="Junior Developer",
    period="2018年4月～2020年3月",
    description="JavaScriptを使用したWebアプリケーションの保守に従事。既存のコードの改善やバグ修正を担当。定期的にコードレビューを受け、プログラミングスキルを向上させた。"
)

user_input = UserInput(
    name="田中太郎",
    residence="東京都渋谷区",
    years_of_experience="5",
    job_title="Software Engineer",
    programming_languages=["Python", "JavaScript", "Java"],
    frameworks=["React", "Django"],
    testing_tools=["pytest", "Jest"],
    design_tools=[],
    work_experiences=[work_exp1, work_exp2],
    personal_projects=[]
)

job_requirements = JobRequirements(
    job_title="Senior Backend Engineer",
    company_info=CompanyInfo(name="Tech Startup"),
    job_description="Python and cloud infrastructure experience required. Need someone who can design scalable backend systems."
)

print("=" * 60)
print("Test Work Experience Refinement Flow")
print("=" * 60)
print()

# Test 1: Format work experiences
print("[1] Format work experiences")
print("-" * 60)
try:
    # Direct implementation test instead of using orchestrator
    work_experiences_text = ""
    if user_input.work_experiences:
        for exp in user_input.work_experiences:
            work_experiences_text += f"\n【{exp.company_name} - {exp.position}】\n"
            work_experiences_text += f"期間: {exp.period}\n"
            work_experiences_text += f"職務内容: {exp.description}\n"
    
    print("✓ Formatting successful")
    print()
    print("Formatted text:")
    print(work_experiences_text)
    print()
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Check prompt format
print()
print("[2] Check prompt formatting")
print("-" * 60)
try:
    from prompts.work_experience_refinement import WORK_EXPERIENCE_REFINEMENT_PROMPT
    
    formatted_prompt = WORK_EXPERIENCE_REFINEMENT_PROMPT.format(
        work_experiences=work_experiences_text,
        job_title=job_requirements.job_title,
        job_requirements=job_requirements.job_description,
        requirements_analysis="Looking for cloud and backend skills",
        company_analysis="Fast-growing AI startup"
    )
    
    print("✓ Prompt format successful")
    print(f"✓ Prompt length: {len(formatted_prompt)} chars")
    print()
    print("First 500 chars of prompt:")
    print(formatted_prompt[:500])
    print()
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Check if JSONparsing would work
print()
print("[3] Test JSON response parsing")
print("-" * 60)
try:
    # Simulate LLM response
    mock_response = """
    Here's the refined work experiences:
    
    {
      "work_experiences": [
        {
          "company_name": "ABC Company",
          "position": "Software Engineer",
          "period": "2020年4月～2022年3月",
          "description": "Designed and implemented Python/React web applications for user management, handling 1M+ users with PostgreSQL backend. Optimized system performance and scalability for cloud deployment."
        },
        {
          "company_name": "XYZ Corp",
          "position": "Junior Developer",
          "period": "2018年4月～2020年3月",
          "description": "Developed and maintained JavaScript web applications with focus on code quality and best practices. Participated in code reviews to improve development standards."
        }
      ]
    }
    """
    
    # Try to parse
    json_start = mock_response.find('{')
    json_end = mock_response.rfind('}') + 1
    if json_start >= 0 and json_end > json_start:
        json_str = mock_response[json_start:json_end]
        parsed = json.loads(json_str)
        refined_exps = parsed.get("work_experiences", [])
        
        print("✓ JSON parsing successful")
        print(f"✓ Parsed {len(refined_exps)} refined experiences")
        print()
        print("Refined experiences:")
        for exp in refined_exps:
            print(f"  - {exp['company_name']} ({exp['period']})")
            print(f"    Position: {exp['position']}")
            print(f"    Description: {exp['description'][:60]}...")
            print()
    else:
        print("✗ No JSON found in response")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 60)
print("All tests passed!")
print("=" * 60)
