"""
Compass AI - Phase 2 Knowledge Base Test Suite
Validates dataset structure, references, and integrity.
"""
import os

import pandas as pd


def test_knowledge_base():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    
    goals_path = os.path.join(data_dir, "goals.csv")
    skills_path = os.path.join(data_dir, "skills.csv")
    goal_skills_path = os.path.join(data_dir, "goal_skills.csv")
    resources_path = os.path.join(data_dir, "resources.csv")
    
    # 1. Load Datasets
    assert os.path.exists(goals_path), "goals.csv missing!"
    assert os.path.exists(skills_path), "skills.csv missing!"
    assert os.path.exists(goal_skills_path), "goal_skills.csv missing!"
    assert os.path.exists(resources_path), "resources.csv missing!"
    
    df_goals = pd.read_csv(goals_path)
    df_skills = pd.read_csv(skills_path)
    df_goal_skills = pd.read_csv(goal_skills_path)
    df_resources = pd.read_csv(resources_path)
    
    print(f"✓ Loaded {len(df_goals)} goals.")
    print(f"✓ Loaded {len(df_skills)} skills.")
    print(f"✓ Loaded {len(df_goal_skills)} goal-skill mappings.")
    print(f"✓ Loaded {len(df_resources)} resources.")
    
    # 2. Validate Non-Empty
    assert len(df_goals) >= 3, "Minimum 3 goals required"
    assert len(df_skills) >= 10, "Minimum 10 skills required"
    assert len(df_resources) >= 20, "Minimum 20 resources required"
    
    # 3. Referencing Integrity: goal_skills.csv -> goals.csv
    valid_goals = set(df_goals["goal"].unique())
    mapped_goals = set(df_goal_skills["goal"].unique())
    invalid_goals = mapped_goals - valid_goals
    assert len(invalid_goals) == 0, f"Invalid goals found in mapping: {invalid_goals}"
    
    # 4. Referencing Integrity: goal_skills.csv -> skills.csv
    valid_skills = set(df_skills["skill"].unique())
    mapped_skills = set(df_goal_skills["skill"].unique())
    invalid_mapped_skills = mapped_skills - valid_skills
    assert len(invalid_mapped_skills) == 0, f"Invalid skills found in goal mapping: {invalid_mapped_skills}"
    
    # 5. Referencing Integrity: resources.csv -> skills.csv
    resource_skills = set(df_resources["skill"].unique())
    invalid_resource_skills = resource_skills - valid_skills
    assert len(invalid_resource_skills) == 0, f"Invalid skills found in resources: {invalid_resource_skills}"
    
    # 6. Check prerequisite references
    for _, row in df_skills.iterrows():
        prereqs = row["prerequisites"]
        if pd.notna(prereqs) and prereqs != "none":
            for p in prereqs.split(";"):
                p_clean = p.strip()
                assert p_clean in valid_skills, f"Unknown prerequisite '{p_clean}' for skill '{row['skill']}'"
                
    print("✓ ALL KNOWLEDGE BASE DATASET TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_knowledge_base()
