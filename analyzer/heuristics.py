from datetime import datetime, timezone

def analyze_complexity(code_files):
    """
    Estimates complexity based on file length and imports.
    Cheap CPU heuristic.
    """
    if not code_files: return "Low"
    
    # Calculate average line length of the code snippets
    # (Assuming code_files contains raw string content of files)
    avg_len = sum(len(c) for c in code_files) / len(code_files)
    
    # Rough count of imports to see if it uses external libraries
    imports = sum(c.count("import ") for c in code_files)
    
    # Arbitrary thresholds for the hackathon demo
    if avg_len > 2000 and imports > 5: return "High"
    if avg_len > 500: return "Medium"
    return "Low"

def analyze_maturity(repos):
    """
    Checks if the project looks real or just a tutorial copy.
    """
    score = 0
    for r in repos:
        # If it has stars, people like it -> likely real
        if r['stars'] > 0: score += 1
        # If it's larger than 500KB, it's likely not just a "hello world"
        if r['size'] > 500: score += 1 
        
    if score > 3: return "Maintained"
    if score > 1: return "Developing"
    return "Experimental"

def analyze_consistency(repos, skill_name):
    """
    Checks if the skill appears across multiple projects.
    """
    count = 0
    skill_lower = skill_name.lower()
    
    for r in repos:
        # Check language field
        if r['language'] and skill_lower in r['language'].lower():
            count += 1
            continue
            
        # Check description
        if r['description'] and skill_lower in r['description'].lower():
            count += 1
            
    if count >= 3: return "Consistent"
    if count >= 1: return "Occasional"
    return "One-off"

def analyze_recency(repos):
    """
    Checks if the user has pushed code recently.
    """
    if not repos: return "Dormant"
    
    # Sort repos by update time to find the latest one
    latest = max(repos, key=lambda x: x['updated_at'])
    last_update = latest['updated_at']
    
    # Ensure last_update is timezone-aware
    if last_update.tzinfo is None:
        last_update = last_update.replace(tzinfo=timezone.utc)
    
    now = datetime.now(timezone.utc)
    delta = (now - last_update).days
    
    if delta < 90: return "Active"   # Last 3 months
    if delta < 365: return "Stale"   # Last year
    return "Dormant"