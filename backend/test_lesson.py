from profai_engine import ProfAIEngine

engine = ProfAIEngine()

# Test user creation
user_id = engine.create_user("Test User")
print(f"Created user: {user_id}")

# Get user profile
user_profile = engine.get_user(user_id)
print(f"User profile: {user_profile}")

# Test lesson generation
print("Testing lesson generation...")
try:
    lesson = engine.generate_lesson_content("Types of AI Models", user_profile)
    print(f"Lesson generated successfully!")
    print(f"Lesson keys: {lesson.keys() if lesson else 'None'}")
except Exception as e:
    print(f"Error generating lesson: {e}")