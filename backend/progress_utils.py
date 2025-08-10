import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

def calculate_lesson_deadlines(self, total_lessons: int, course_deadline: str) -> Dict[str, Dict]:
    """Calculate evenly distributed deadlines for lessons based on course deadline"""
    deadlines = {}
    course_end = datetime.fromisoformat(course_deadline)
    now = datetime.now()
    total_days = (course_end - now).days
    days_per_lesson = max(total_days // total_lessons, 1)  # At least 1 day per lesson
    
    for i in range(total_lessons):
        lesson_deadline = now + timedelta(days=days_per_lesson * (i + 1))
        lesson_id = f"lesson_{i + 1}"
        deadlines[lesson_id] = {
            "due_date": lesson_deadline.isoformat(),
            "completed": False,
            "completion_date": None
        }
    
    return deadlines

def update_lesson_progress(self, user_id: str, topic_id: str, lesson_id: str, 
                         progress: float, completion_time: str = None) -> Dict:
    """Update progress for a specific lesson"""
    with open(self.progress_file, 'r+') as f:
        try:
            progress_data = json.load(f)
        except json.JSONDecodeError:
            progress_data = {}
            
        user_progress = progress_data.get(user_id, {})
        topic_progress = user_progress.get(topic_id, {
            "overall_progress": 0,
            "lesson_progress": {},
            "deadlines": {}
        })
        
        # Update lesson progress
        lesson_progress = topic_progress["lesson_progress"].get(lesson_id, {
            "progress": 0,
            "started_at": datetime.now().isoformat(),
            "last_updated": None,
            "completed": False
        })
        
        lesson_progress.update({
            "progress": progress,
            "last_updated": datetime.now().isoformat(),
            "completed": progress >= 100,
            "completion_time": completion_time if progress >= 100 else None
        })
        
        # Update topic progress
        topic_progress["lesson_progress"][lesson_id] = lesson_progress
        completed_lessons = sum(1 for lp in topic_progress["lesson_progress"].values() 
                              if lp.get("completed", False))
        total_lessons = len(topic_progress["lesson_progress"])
        topic_progress["overall_progress"] = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        # Update data
        user_progress[topic_id] = topic_progress
        progress_data[user_id] = user_progress
        
        # Save updated progress
        f.seek(0)
        json.dump(progress_data, f, indent=2)
        f.truncate()
        
        return topic_progress

def get_lesson_deadlines(self, user_id: str, topic_id: str) -> Dict[str, Dict]:
    """Get deadlines for all lessons in a topic"""
    with open(self.progress_file, 'r') as f:
        try:
            progress_data = json.load(f)
            user_progress = progress_data.get(user_id, {})
            topic_progress = user_progress.get(topic_id, {})
            return topic_progress.get("deadlines", {})
        except json.JSONDecodeError:
            return {}

def update_topic_progress(self, user_id: str, topic_id: str, progress: float, 
                         time_spent: int, lesson_completions: Dict = None, 
                         current_section: str = None) -> Dict:
    """Update detailed topic progress"""
    with open(self.progress_file, 'r+') as f:
        try:
            progress_data = json.load(f)
        except json.JSONDecodeError:
            progress_data = {}
            
        user_progress = progress_data.get(user_id, {})
        topic_progress = user_progress.get(topic_id, {
            "overall_progress": 0,
            "time_spent": 0,
            "current_section": "",
            "lesson_completions": {},
            "started_at": datetime.now().isoformat(),
            "last_updated": None
        })
        
        # Update topic data
        topic_progress.update({
            "overall_progress": progress,
            "time_spent": time_spent,
            "current_section": current_section or topic_progress["current_section"],
            "last_updated": datetime.now().isoformat()
        })
        
        # Update lesson completions if provided
        if lesson_completions:
            topic_progress["lesson_completions"].update(lesson_completions)
        
        # Update data
        user_progress[topic_id] = topic_progress
        progress_data[user_id] = user_progress
        
        # Save updated progress
        f.seek(0)
        json.dump(progress_data, f, indent=2)
        f.truncate()
        
        return topic_progress

def get_topic_complete_data(self, user_id: str, topic_id: str) -> Dict:
    """Get complete topic data including progress, deadlines, and analytics"""
    with open(self.progress_file, 'r') as f:
        try:
            progress_data = json.load(f)
            user_progress = progress_data.get(user_id, {})
            topic_progress = user_progress.get(topic_id, {})
            
            # Calculate completion rate and estimated completion
            lesson_completions = topic_progress.get("lesson_completions", {})
            completed = sum(1 for lesson in lesson_completions.values() 
                          if lesson.get("completed", False))
            total = len(lesson_completions) or 1
            completion_rate = completed / total * 100
            
            # Calculate time analysis
            time_spent = topic_progress.get("time_spent", 0)
            started_at = topic_progress.get("started_at")
            if started_at:
                elapsed_days = (datetime.now() - datetime.fromisoformat(started_at)).days
                avg_daily_progress = completion_rate / (elapsed_days or 1)
                days_to_completion = (100 - completion_rate) / avg_daily_progress if avg_daily_progress > 0 else float('inf')
            else:
                avg_daily_progress = 0
                days_to_completion = float('inf')
            
            return {
                **topic_progress,
                "analytics": {
                    "completion_rate": completion_rate,
                    "avg_daily_progress": avg_daily_progress,
                    "estimated_days_to_completion": days_to_completion,
                    "time_analysis": {
                        "total_time_spent": time_spent,
                        "avg_time_per_lesson": time_spent / (completed or 1)
                    }
                }
            }
            
        except json.JSONDecodeError:
            return {}
