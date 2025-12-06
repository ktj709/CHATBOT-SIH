"""
Knowledge Base Processor for GyaanSetu RAG Chatbot.
Loads and processes knowledge_base.json into searchable text chunks.
"""
import json
import os
from typing import List, Dict, Any

# Path to knowledge base file
KNOWLEDGE_BASE_PATH = os.path.join(os.path.dirname(__file__), "knowledge_base.json")


def load_knowledge_base() -> Dict[str, Any]:
    """Load the knowledge base JSON file."""
    with open(KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def flatten_dict(d: Dict, parent_key: str = "", sep: str = " > ") -> List[str]:
    """Recursively flatten a nested dictionary into readable text chunks."""
    items = []
    
    for key, value in d.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, sep))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, f"{new_key}[{i}]", sep))
                else:
                    items.append(f"{new_key}: {item}")
        else:
            items.append(f"{new_key}: {value}")
    
    return items


def create_chunks() -> List[Dict[str, str]]:
    """
    Create meaningful text chunks from the knowledge base.
    Returns a list of dicts with 'text' and 'category' keys.
    """
    kb = load_knowledge_base()
    chunks = []
    
    # 1. Project Information
    project = kb.get("project", {})
    chunks.append({
        "category": "Project Overview",
        "text": f"GyaanSetu is {project.get('description', '')}. Tagline: {project.get('tagline', '')}. Version: {project.get('version', '')}. Type: {project.get('type', '')}."
    })
    
    # 2. Architecture Components
    arch = kb.get("architecture", {})
    for component in arch.get("components", []):
        tech = component.get("technology", {})
        tech_str = ", ".join([f"{k}: {v}" for k, v in tech.items()])
        chunks.append({
            "category": "Architecture",
            "text": f"Component: {component.get('name', '')} - Type: {component.get('type', '')}. Technologies: {tech_str}."
        })
    
    # 3. Features
    features = kb.get("features", {})
    
    # User Management
    user_mgmt = features.get("userManagement", {})
    for role_info in user_mgmt.get("roles", []):
        role = role_info.get("role", "")
        capabilities = ", ".join(role_info.get("capabilities", []))
        chunks.append({
            "category": "User Management",
            "text": f"User Role: {role}. Capabilities: {capabilities}."
        })
    
    # Course Management
    course_mgmt = features.get("courseManagement", {})
    for feature in course_mgmt.get("features", []):
        details = ", ".join(feature.get("details", []))
        chunks.append({
            "category": "Course Management",
            "text": f"Course Feature: {feature.get('name', '')}. Details: {details}."
        })
    
    # Certificate System
    cert_sys = features.get("certificateSystem", {})
    blockchain = cert_sys.get("blockchain", {})
    chunks.append({
        "category": "Certificate System",
        "text": f"Certificate System: {cert_sys.get('description', '')}. Network: {blockchain.get('network', '')}. Features: {', '.join(blockchain.get('features', []))}."
    })
    
    for endpoint in cert_sys.get("endpoints", []):
        chunks.append({
            "category": "Certificate API",
            "text": f"Certificate API Endpoint: {endpoint.get('method', 'GET')} {endpoint.get('path', '')} - {endpoint.get('description', '')}."
        })
    
    # Collaborative Whiteboard
    whiteboard = features.get("collaborativeWhiteboard", {})
    chunks.append({
        "category": "Whiteboard",
        "text": f"Collaborative Whiteboard: {whiteboard.get('description', '')}"
    })
    for wb_feature in whiteboard.get("features", []):
        details = ", ".join(wb_feature.get("details", []))
        chunks.append({
            "category": "Whiteboard",
            "text": f"Whiteboard Feature: {wb_feature.get('name', '')}. Details: {details}."
        })
    
    # Audio/Video Classes
    av_classes = features.get("audioVideoClasses", {})
    chunks.append({
        "category": "Audio/Video",
        "text": f"Audio/Video Classes: {av_classes.get('description', '')}"
    })
    for av_feature in av_classes.get("features", []):
        details = ", ".join(av_feature.get("details", []))
        chunks.append({
            "category": "Audio/Video",
            "text": f"Audio/Video Feature: {av_feature.get('name', '')}. Details: {details}."
        })
    
    # Community Portal
    community = features.get("communityPortal", {})
    community_features = ", ".join(community.get("features", []))
    chunks.append({
        "category": "Community",
        "text": f"Community Portal: {community.get('description', '')}. Features: {community_features}."
    })
    
    # Donation System
    donation = features.get("donationSystem", {})
    donation_features = ", ".join(donation.get("features", []))
    chunks.append({
        "category": "Donations",
        "text": f"Donation System: {donation.get('description', '')}. Features: {donation_features}."
    })
    
    # Seminar Management
    seminar = features.get("seminarManagement", {})
    for sem_feature in seminar.get("features", []):
        if isinstance(sem_feature, dict):
            details = ", ".join(sem_feature.get("details", []))
            chunks.append({
                "category": "Seminars",
                "text": f"Seminar Feature: {sem_feature.get('name', '')}. Details: {details}."
            })
    
    # Doubt Resolution
    doubt = features.get("doubtResolution", {})
    doubt_features = ", ".join(doubt.get("features", []))
    chunks.append({
        "category": "Doubts",
        "text": f"Doubt Resolution: {doubt.get('description', '')}. Features: {doubt_features}."
    })
    
    # Digital Library
    library = features.get("digitalLibrary", {})
    library_features = ", ".join(library.get("features", []))
    chunks.append({
        "category": "Library",
        "text": f"Digital Library: {library.get('description', '')}. Features: {library_features}."
    })
    
    # 4. How To Use Guides
    how_to = kb.get("howToUse", {})
    
    # For Students
    for_students = how_to.get("forStudents", {})
    for guide_name, steps in for_students.items():
        steps_text = " ".join([f"{i+1}. {step}" for i, step in enumerate(steps)])
        chunks.append({
            "category": "How To - Students",
            "text": f"Guide for Students - {guide_name}: {steps_text}"
        })
    
    # For Teachers
    for_teachers = how_to.get("forTeachers", {})
    for guide_name, steps in for_teachers.items():
        steps_text = " ".join([f"{i+1}. {step}" for i, step in enumerate(steps)])
        chunks.append({
            "category": "How To - Teachers",
            "text": f"Guide for Teachers - {guide_name}: {steps_text}"
        })
    
    # For Admins
    for_admins = how_to.get("forAdmins", {})
    for guide_name, steps in for_admins.items():
        steps_text = " ".join([f"{i+1}. {step}" for i, step in enumerate(steps)])
        chunks.append({
            "category": "How To - Admins",
            "text": f"Guide for Admins - {guide_name}: {steps_text}"
        })
    
    # 5. FAQs
    faqs = kb.get("faq", [])
    for faq in faqs:
        chunks.append({
            "category": "FAQ",
            "text": f"Q: {faq.get('question', '')} A: {faq.get('answer', '')}"
        })
    
    # 6. Technical Requirements
    tech_req = kb.get("technicalRequirements", {})
    chunks.append({
        "category": "Technical Requirements",
        "text": f"Browser Requirements: {tech_req.get('browser', '')}. Student Requirements: {', '.join(tech_req.get('student', []))}. Teacher Requirements: {', '.join(tech_req.get('teacher', []))}."
    })
    
    # 7. Data Models
    data_models = kb.get("dataModels", {})
    for model_name, model_info in data_models.items():
        fields = ", ".join(model_info.get("fields", []))
        chunks.append({
            "category": "Data Models",
            "text": f"Data Model: {model_name}. Fields: {fields}."
        })
    
    return chunks


def get_all_chunks() -> List[Dict[str, str]]:
    """Get all processed chunks. Main entry point."""
    return create_chunks()


if __name__ == "__main__":
    # Test the processor
    chunks = get_all_chunks()
    print(f"Total chunks created: {len(chunks)}")
    for i, chunk in enumerate(chunks[:5]):
        print(f"\n--- Chunk {i+1} [{chunk['category']}] ---")
        print(chunk['text'][:200] + "...")
