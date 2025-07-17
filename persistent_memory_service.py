import json
import os
from typing import List, Optional, Dict, Any

class StudentProfile:
    def __init__(self, student_id: str, profile_data: dict):
        self.student_id = student_id
        self.name = profile_data.get("name")
        self.grade = profile_data.get("grade")
        self.learning_style = profile_data.get("learning_style")
        self.mastered_topics = profile_data.get("mastered_topics", [])
        self.struggling_topics = profile_data.get("struggling_topics", [])
        # Add more fields as needed
        # Accept any extra fields for extensibility
        self._extra = {k: v for k, v in profile_data.items() if k not in {
            "student_id", "name", "grade", "learning_style", "mastered_topics", "struggling_topics"
        }}

    def apply_updates(self, updates: List[Dict[str, Any]]):
        for update in updates:
            op = update.get("operation")
            field = update.get("field")
            value = update.get("value")
            if op == "UPDATE_FIELD" and field:
                setattr(self, field, value)
            elif op == "APPEND_TO_ARRAY" and field:
                arr = getattr(self, field, [])
                if value not in arr:
                    arr.append(value)
                setattr(self, field, arr)
            elif op == "REMOVE_FROM_ARRAY" and field:
                arr = getattr(self, field, [])
                if value in arr:
                    arr.remove(value)
                setattr(self, field, arr)
            # For extensibility: handle extra fields
            elif op == "UPDATE_FIELD" and field not in self.__dict__:
                self._extra[field] = value
            elif op == "APPEND_TO_ARRAY" and field not in self.__dict__:
                arr = self._extra.get(field, [])
                if value not in arr:
                    arr.append(value)
                self._extra[field] = arr
            elif op == "REMOVE_FROM_ARRAY" and field not in self.__dict__:
                arr = self._extra.get(field, [])
                if value in arr:
                    arr.remove(value)
                self._extra[field] = arr
            # Ignore CREATE_SEMANTIC_MEMORY and other ops for LTM persistence

    def to_dict(self) -> dict:
        d = {
            "student_id": self.student_id,
            "name": self.name,
            "grade": self.grade,
            "learning_style": self.learning_style,
            "mastered_topics": self.mastered_topics,
            "struggling_topics": self.struggling_topics,
        }
        d.update(self._extra)
        return d

class MemoryService:
    def __init__(self, ltm_filepath: str, backend_filepath: str):
        self.ltm_filepath = ltm_filepath
        self.backend_filepath = backend_filepath
        self.ltm_data = self._load_from_json(ltm_filepath)
        self.backend_data = self._load_from_json(backend_filepath)

    def _load_from_json(self, filepath: str) -> dict:
        if not os.path.exists(filepath):
            return {}
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def get_student_profile(self, student_id: str) -> StudentProfile:
        if student_id in self.ltm_data:
            return StudentProfile(student_id, self.ltm_data[student_id])
        # New student: use backend data
        backend = self.backend_data.get(student_id)
        if not backend:
            raise ValueError(f"Student {student_id} not found in backend data.")
        # Start with backend fields, add required LTM fields
        profile_data = dict(backend)
        profile_data["student_id"] = student_id
        profile_data.setdefault("learning_style", None)
        profile_data.setdefault("mastered_topics", [])
        profile_data.setdefault("struggling_topics", [])
        return StudentProfile(student_id, profile_data)

    def save_student_profile(self, profile: StudentProfile):
        self.ltm_data[profile.student_id] = profile.to_dict()
        with open(self.ltm_filepath, "w") as f:
            json.dump(self.ltm_data, f, indent=2)

if __name__ == "__main__":
    # --- Setup: create dummy backend and LTM files ---
    backend_data = {
        "student-001": {"name": "Arjun Sharma", "grade": 10},
        "student-002": {"name": "Priya Singh", "grade": 9}
    }
    ltm_data = {
        "student-001": {
            "student_id": "student-001",
            "name": "Arjun Sharma",
            "grade": 10,
            "learning_style": "visual",
            "mastered_topics": ["algebra_linear"],
            "struggling_topics": ["trigonometry_basic"]
        }
    }
    with open("backend_data.json", "w") as f:
        json.dump(backend_data, f, indent=2)
    with open("ltm_profiles.json", "w") as f:
        json.dump(ltm_data, f, indent=2)

    # --- Initialize MemoryService ---
    memory_service = MemoryService("ltm_profiles.json", "backend_data.json")

    # --- Scenario 1: Existing Student ---
    print("\n--- Scenario 1: Existing Student (student-001) ---")
    profile1 = memory_service.get_student_profile("student-001")
    print("Before:", profile1.to_dict())
    # Simulate LTM Consolidation Agent updates
    updates1 = [
        {"operation": "APPEND_TO_ARRAY", "field": "mastered_topics", "value": "trigonometry_basic", "evidence": "Mastered trigonometry."},
        {"operation": "REMOVE_FROM_ARRAY", "field": "struggling_topics", "value": "trigonometry_basic", "evidence": "No longer struggling."},
        {"operation": "UPDATE_FIELD", "field": "learning_style", "value": "visual", "evidence": "Confirmed visual learning."}
    ]
    profile1.apply_updates(updates1)
    memory_service.save_student_profile(profile1)
    print("After:", profile1.to_dict())
    # Verify file
    with open("ltm_profiles.json") as f:
        print("LTM File:", json.load(f))

    # --- Scenario 2: New Student ---
    print("\n--- Scenario 2: New Student (student-002) ---")
    profile2 = memory_service.get_student_profile("student-002")
    print("Before:", profile2.to_dict())
    # Simulate LTM Consolidation Agent updates
    updates2 = [
        {"operation": "APPEND_TO_ARRAY", "field": "struggling_topics", "value": "geometry", "evidence": "Student expressed difficulty with geometry."},
        {"operation": "UPDATE_FIELD", "field": "learning_style", "value": "textual", "evidence": "Prefers text explanations."}
    ]
    profile2.apply_updates(updates2)
    memory_service.save_student_profile(profile2)
    print("After:", profile2.to_dict())
    # Verify file
    with open("ltm_profiles.json") as f:
        print("LTM File:", json.load(f)) 