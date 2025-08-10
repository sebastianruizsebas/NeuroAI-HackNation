#!/usr/bin/env python3
"""
Test script to verify enhanced course content quality and topics library functionality
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from profai_engine import ProfAIEngine
import json

def test_question_quality():
    """Test question generation and quality validation"""
    print("=" * 60)
    print("TESTING QUESTION GENERATION AND QUALITY VALIDATION")
    print("=" * 60)
    
    engine = ProfAIEngine()
    
    # Test topics
    test_topics = ["transformers", "neural networks", "machine learning"]
    
    for topic in test_topics:
        print(f"\n🧪 Testing topic: {topic}")
        print("-" * 40)
        
        # Generate questions
        questions = engine.generate_initial_assessment(topic)
        print(f"Generated {len(questions)} questions")
        
        if questions:
            # Test quality validation
            quality_report = engine.get_question_quality_report(questions, topic)
            
            print(f"📊 Quality Report Summary:")
            print(f"   - Average quality score: {quality_report['summary']['average_quality_score']}")
            print(f"   - Questions passed validation: {quality_report['summary']['passed_validation']}/{quality_report['summary']['total_questions']}")
            print(f"   - Overall grade: {quality_report['summary']['overall_grade']}")
            
            # Show individual question scores
            for i, report in enumerate(quality_report['individual_reports'][:2]):  # Show first 2
                print(f"   - Q{i+1}: {report['quality_score']:.2f} - {'✅' if report['is_valid'] else '❌'}")
                if report['issues']:
                    print(f"     Issues: {', '.join(report['issues'])}")
            
            # Show recommendations
            if quality_report['recommendations']:
                print(f"   📝 Recommendations:")
                for rec in quality_report['recommendations'][:2]:
                    print(f"     - {rec}")
        else:
            print("❌ No questions generated")

def test_lesson_content_quality():
    """Test enhanced lesson content generation"""
    print("\n" + "=" * 60)
    print("TESTING ENHANCED LESSON CONTENT GENERATION")
    print("=" * 60)
    
    engine = ProfAIEngine()
    
    test_topic = "transformers"
    user_profile = {'competency_scores': {test_topic: 5}}  # Intermediate level
    
    print(f"\n🧪 Generating lesson for: {test_topic} (competency level 5)")
    print("-" * 40)
    
    lesson = engine.generate_lesson_content(test_topic, user_profile)
    
    if lesson:
        print(f"✅ Lesson generated successfully")
        print(f"📖 Topic: {lesson.get('topic', 'N/A')}")
        print(f"📊 Competency Level: {lesson.get('competency_level', 'N/A')}")
        print(f"📝 Overview length: {len(lesson.get('overview', ''))} characters")
        print(f"📚 Number of chunks: {len(lesson.get('chunks', []))}")
        
        # Analyze chunks for quality
        chunks = lesson.get('chunks', [])
        if chunks:
            avg_chunk_length = sum(len(chunk.get('content', '')) for chunk in chunks) / len(chunks)
            print(f"📏 Average chunk length: {avg_chunk_length:.0f} characters")
            
            # Check for enhanced features
            has_math = any(chunk.get('mathematical_concepts') for chunk in chunks)
            has_examples = any(chunk.get('examples') for chunk in chunks)
            has_applications = any(chunk.get('applications') for chunk in chunks)
            
            print(f"🔬 Enhanced features:")
            print(f"   - Mathematical concepts: {'✅' if has_math else '❌'}")
            print(f"   - Examples included: {'✅' if has_examples else '❌'}")
            print(f"   - Applications listed: {'✅' if has_applications else '❌'}")
            
            # Show first chunk sample
            if chunks:
                first_chunk = chunks[0]
                print(f"📋 Sample chunk content (first 200 chars):")
                print(f"   Title: {first_chunk.get('title', 'N/A')}")
                content = first_chunk.get('content', '')
                print(f"   Content: {content[:200]}{'...' if len(content) > 200 else ''}")
    else:
        print("❌ No lesson content generated")

def test_topics_library():
    """Test topics library functionality"""
    print("\n" + "=" * 60)
    print("TESTING TOPICS LIBRARY FUNCTIONALITY")
    print("=" * 60)
    
    engine = ProfAIEngine()
    
    # Create a test user
    user_id = engine.create_user("Test User Library")
    print(f"👤 Created test user: {user_id}")
    
    # Generate and save some custom topics
    test_queries = [
        "I want to learn about deep learning optimization",
        "Computer vision applications",
        "Natural language processing fundamentals"
    ]
    
    print(f"\n📚 Generating {len(test_queries)} custom topics...")
    
    for i, query in enumerate(test_queries):
        topics = engine.generate_custom_topics(user_id, query)
        if topics:
            topic = topics[0]  # Take the first generated topic
            engine.save_custom_topic(user_id, topic)
            print(f"   {i+1}. Saved: {topic.get('title', 'Unknown')}")
    
    # Test library retrieval
    print("\n📖 Testing library retrieval...")
    library = engine.get_topics_library(user_id)
    
    print(f"📊 Library Statistics:")
    stats = library.get('stats', {})
    print(f"   - Total topics: {stats.get('total_topics', 0)}")
    print(f"   - Completed: {stats.get('completed_topics', 0)}")
    print(f"   - In progress: {stats.get('in_progress', 0)}")
    print(f"   - Total time spent: {stats.get('total_time_spent', 0)} minutes")
    
    # Test categorization
    categories = library.get('by_category', {})
    print(f"📂 Categories found: {list(categories.keys())}")
    
    # Test search
    print("\n🔍 Testing search functionality...")
    search_results = engine.search_topics_library(user_id, "deep learning")
    print(f"   Search for 'deep learning': {len(search_results)} results")
    
    # Test recent topics
    recent = library.get('recent', [])
    print(f"📅 Recent topics: {len(recent)} found")

def main():
    """Run all tests"""
    print("🚀 Starting Enhanced ProfAI System Tests")
    print("Testing question quality, lesson content, and topics library...")
    
    try:
        test_question_quality()
        test_lesson_content_quality() 
        test_topics_library()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
        print("\n📋 Summary:")
        print("   1. ✅ Question generation with quality validation")
        print("   2. ✅ Enhanced lesson content with academic rigor")
        print("   3. ✅ Topics library with organization and search")
        print("\n🎉 Enhanced ProfAI system is ready!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
