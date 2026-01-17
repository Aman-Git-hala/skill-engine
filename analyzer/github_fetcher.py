from github import Github
from github import Auth
import os

def fetch_user_data(username: str, token: str):
    """
    Fetches public repos for a user.
    """
    try:
        auth = Auth.Token(token)
        g = Github(auth=auth)
        user = g.get_user(username)
        
        # ⚡️ OPTIMIZATION: Only fetch top 10 most recent repos
        repos = user.get_repos(sort="updated", direction="desc")[:10]
        
        repo_data = []
        # print(f"   (Debug) Scanning {len(repos)} repositories for {username}...")
        
        for repo in repos:
            repo_data.append({
                "name": repo.name,
                "description": repo.description,
                "language": repo.language,
                "updated_at": repo.updated_at,
                "created_at": repo.created_at,
                "stars": repo.stargazers_count,
                "size": repo.size, 
                "object": repo 
            })
            
        return repo_data
    except Exception as e:
        print(f"Error fetching GitHub data: {e}")
        return []

def fetch_file_content(repo_object, extension_filter_list):
    """
    Recursively searches for code files with Strict Limits.
    """
    files_content = []
    # Queue: (path, depth)
    dirs_to_check = [("", 0)]
    
    max_files = 3       # ⚡️ STOP after finding 3 good files (was 5 or 10)
    max_depth = 3       # Depth limit (folder inside folder inside folder)
    max_dirs_scanned = 20 # ⚡️ HARD LIMIT: Don't check more than 20 folders per repo
    
    scanned_count = 0
    
    try:
        while dirs_to_check and len(files_content) < max_files:
            if scanned_count > max_dirs_scanned:
                break # Give up on this repo, it's too big/messy
            
            scanned_count += 1
            current_path, depth = dirs_to_check.pop(0)
            
            if depth > max_depth: continue

            # Get contents
            try:
                contents = repo_object.get_contents(current_path)
            except:
                continue # Skip if permission denied or empty
            
            for file_content in contents:
                if file_content.type == "file":
                    # Check extensions
                    if any(file_content.path.endswith(ext) for ext in extension_filter_list):
                        try:
                            decoded = file_content.decoded_content.decode('utf-8')
                            # Only keep files between 50 and 100,000 chars to avoid memory crashes
                            if 50 < len(decoded) < 100000:
                                files_content.append(decoded)
                                # print(f"      [Found] {file_content.path}")
                                if len(files_content) >= max_files: break
                        except:
                            pass 

                elif file_content.type == "dir":
                    # Smart Skip: Ignore huge dependency folders
                    if file_content.name not in ["node_modules", "venv", ".git", "build", "dist", "vendor", "ios", "android"]:
                        dirs_to_check.append((file_content.path, depth + 1))
                        
    except Exception as e:
        pass
        
    return files_content