from typing import Dict, Optional

class ContentEngine:
    """Manages the content planning workflow and knowledge storage"""
    
    def __init__(self, groq_client):
        self.groq = groq_client
        self.projects = {}  # In-memory storage
    
    def create_project(self, project_id: str, description: str) -> Dict:
        """Create a new content planning project"""
        # Analyze the business
        analysis = self.groq.analyze_business(description)
        
        # Generate questions
        questions = self.groq.generate_questions(analysis)
        
        # Store project
        self.projects[project_id] = {
            "description": description,
            "analysis": analysis,
            "questions": questions,
            "answers": {},
            "generated_content": {}
        }
        
        return {
            "project_id": project_id,
            "analysis": analysis,
            "questions": questions
        }
    
    def save_answers(self, project_id: str, answers: Dict) -> bool:
        """Save user answers to questions"""
        if project_id not in self.projects:
            return False
        
        self.projects[project_id]["answers"] = answers
        return True
    
    def generate_content(self, project_id: str, page_type: str) -> str:
        """Generate content for a specific page"""
        if project_id not in self.projects:
            raise ValueError("Project not found")
        
        project = self.projects[project_id]
        
        # Build knowledge base
        knowledge_base = {
            "business_description": project["description"],
            "business_analysis": project["analysis"],
            "user_answers": project["answers"]
        }
        
        # Generate content
        content = self.groq.generate_page_content(page_type, knowledge_base)
        
        # Store generated content
        project["generated_content"][page_type] = content
        
        return content
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """Retrieve project data"""
        return self.projects.get(project_id)