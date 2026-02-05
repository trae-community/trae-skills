import os
import sys
import yaml

def parse_frontmatter(file_path):
    """
    Extracts YAML frontmatter from a markdown file.
    Returns the parsed dictionary or None if not found/invalid.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if not content.startswith('---'):
            return None
            
        parts = content.split('---', 2)
        if len(parts) < 3:
            return None
            
        frontmatter_content = parts[1]
        return yaml.safe_load(frontmatter_content)
    except Exception as e:
        print(f"Error reading/parsing {file_path}: {e}")
        return None

def validate_skill_file(file_path):
    print(f"Validating {file_path}...")
    
    frontmatter = parse_frontmatter(file_path)
    
    if frontmatter is None:
        print(f"❌ Error: {file_path} does not have valid YAML frontmatter (must start with --- and end with ---).")
        return False
        
    if not isinstance(frontmatter, dict):
        print(f"❌ Error: {file_path} frontmatter is not a dictionary.")
        return False
        
    # Check required fields
    required_fields = ['name', 'description']
    missing_fields = [field for field in required_fields if field not in frontmatter]
    
    if missing_fields:
        print(f"❌ Error: {file_path} is missing required metadata: {', '.join(missing_fields)}")
        return False
        
    # Check name format (lowercase-hyphenated)
    name = frontmatter.get('name', '')
    import re
    if not re.match(r'^[a-z0-9-]+$', name):
        print(f"⚠️ Warning: Skill name '{name}' should use lowercase and hyphens only.")
        # Not failing for now, just warning
    
    print(f"✅ {file_path} is valid.")
    return True

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    skills_dir = os.path.join(root_dir, 'skills')
    
    if not os.path.exists(skills_dir):
        print("Skills directory not found.")
        sys.exit(1)
        
    has_error = False
    
    for skill_name in os.listdir(skills_dir):
        skill_path = os.path.join(skills_dir, skill_name)
        
        if os.path.isdir(skill_path):
            if skill_name.startswith('.'):
                continue
                
            skill_md_path = os.path.join(skill_path, 'SKILL.md')
            
            if os.path.exists(skill_md_path):
                if not validate_skill_file(skill_md_path):
                    has_error = True
            else:
                print(f"⚠️ Warning: Directory {skill_name} does not contain SKILL.md")
                
    if has_error:
        sys.exit(1)
    else:
        print("All skills validated successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()
