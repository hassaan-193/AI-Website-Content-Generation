from flask import Flask, render_template, request, jsonify, session
from groq_client import GroqClient
from content_engine import ContentEngine
from dotenv import load_dotenv
import os
import secrets

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Initialize with environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("=" * 60)
    print("ERROR: GROQ_API_KEY not found!")
    print("Please create a .env file with: GROQ_API_KEY=your-key-here")
    print("=" * 60)
    exit(1)

groq_client = GroqClient(GROQ_API_KEY)
content_engine = ContentEngine(groq_client)

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_business():
    """Analyze business description and generate questions"""
    try:
        data = request.json
        description = data.get('description', '').strip()
        
        if not description:
            return jsonify({"error": "Description is required"}), 400
        
        # Create unique project ID
        project_id = secrets.token_urlsafe(8)
        session['project_id'] = project_id
        
        print(f"Creating project {project_id}...")
        
        # Create project and get questions
        result = content_engine.create_project(project_id, description)
        
        print(f"Project created successfully!")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in analyze_business: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/submit-answers', methods=['POST'])
def submit_answers():
    """Save user answers"""
    try:
        project_id = session.get('project_id')
        if not project_id:
            return jsonify({"error": "No active project"}), 400
        
        data = request.json
        answers = data.get('answers', {})
        
        print(f"Saving answers for project {project_id}...")
        
        success = content_engine.save_answers(project_id, answers)
        
        if success:
            return jsonify({"status": "success"})
        else:
            return jsonify({"error": "Failed to save answers"}), 500
            
    except Exception as e:
        print(f"Error in submit_answers: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate/<page_type>', methods=['POST'])
def generate_content(page_type):
    """Generate content for a specific page"""
    try:
        project_id = session.get('project_id')
        if not project_id:
            return jsonify({"error": "No active project"}), 400
        
        print(f"Generating {page_type} content for project {project_id}...")
        
        content = content_engine.generate_content(project_id, page_type)
        
        print(f"Content generated successfully!")
        
        return jsonify({
            "page_type": page_type,
            "content": content
        })
        
    except Exception as e:
        print(f"Error in generate_content: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/project', methods=['GET'])
def get_project():
    """Get current project data"""
    try:
        project_id = session.get('project_id')
        if not project_id:
            return jsonify({"error": "No active project"}), 400
        
        project = content_engine.get_project(project_id)
        
        if project:
            return jsonify(project)
        else:
            return jsonify({"error": "Project not found"}), 404
            
    except Exception as e:
        print(f"Error in get_project: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 AI Website Content Planner")
    print("=" * 60)
    print(f"Server running at: http://localhost:5000")
    print(f"Groq API Key configured: {'✓' if GROQ_API_KEY else '✗'}")
    print("=" * 60)
    app.run(debug=True, port=5000)