#!/usr/bin/env python3
"""
Test script to verify that lesson content properly reflects the title and uses material from chunk JSON files.

This script tests the alignment between:
1. Lesson titles and their content
2. Lesson content and source material from chunks
3. Educational quality and depth
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from profai_engine import ProfAIEngine
from rag_utils import load_all_chunks, find_relevant_chunks
import json

def test_lesson_alignment():
    """Test lesson generation and alignment with source material."""
    
    print("="*80)
    print("TESTING LESSON CONTENT ALIGNMENT WITH TITLES AND SOURCE MATERIAL")
    print("="*80)
    
    # Initialize the engine
    engine = ProfAIEngine()
    
    # Test topics that should have good coverage in the chunks
    test_topics = [
        "Building Neural Networks for Pattern Recognition",
        "Implementing Support Vector Machines",
        "Understanding Machine Learning Fundamentals",
        "Applying Statistical Learning Theory",
        "Optimizing Models with Gradient Descent"
    ]
    
    for topic in test_topics:
        print(f"\n{'='*60}")
        print(f"TESTING TOPIC: {topic}")
        print(f"{'='*60}")
        
        # Check what chunks are available for this topic
        try:
            base_dir = os.path.dirname(__file__)
            chunk_files = [
                os.path.join(base_dir, 'math_ml_chunks.json'),
                os.path.join(base_dir, 'mit_ocw_chunks.json'),
            ]
            chunks = load_all_chunks(chunk_files)
            relevant_chunks = find_relevant_chunks(topic, chunks, top_k=5)
            
            print(f"\nSOURCE MATERIAL ANALYSIS:")
            print(f"Found {len(relevant_chunks)} relevant chunks for '{topic}'")
            
            if relevant_chunks:
                for i, (fname, chunk) in enumerate(relevant_chunks, 1):
                    print(f"\nChunk {i} from {fname}:")
                    print(f"Content preview: {chunk[:200]}...")
            else:
                print("WARNING: No relevant chunks found for this topic!")
                
        except Exception as e:
            print(f"Error loading chunks: {e}")
            relevant_chunks = []
        
        # Generate lesson
        print(f"\nGENERATING LESSON:")
        user_profile = {'competency_scores': {topic: 5}}  # Intermediate level
        
        try:
            lesson = engine.generate_lesson_content(topic, user_profile)
            
            if lesson:
                print(f"✓ Lesson generated successfully")
                
                # Analyze lesson content
                print(f"\nLESSON ANALYSIS:")
                print(f"Topic: {lesson.get('topic')}")
                print(f"Overview length: {len(lesson.get('overview', ''))}")
                print(f"Number of chunks: {len(lesson.get('chunks', []))}")
                
                # Check validation report if available
                if 'validation_report' in lesson:
                    report = lesson['validation_report']
                    print(f"\nVALIDATION REPORT:")
                    print(f"Overall Score: {report['overall_score']:.2f}")
                    print(f"Title Alignment: {report['title_alignment_score']:.2f}")
                    print(f"Source Material Usage: {report['source_material_usage_score']:.2f}")
                    print(f"Content Depth: {report['content_depth_score']:.2f}")
                    print(f"Validation Passed: {report['validation_passed']}")
                    
                    if report['issues']:
                        print(f"Issues:")
                        for issue in report['issues']:
                            print(f"  - {issue}")
                    
                    if report['recommendations']:
                        print(f"Recommendations:")
                        for rec in report['recommendations']:
                            print(f"  - {rec}")
                
                # Analyze content depth
                print(f"\nCONTENT DEPTH ANALYSIS:")
                total_content_length = sum(len(chunk.get('content', '')) for chunk in lesson.get('chunks', []))
                avg_chunk_length = total_content_length / max(len(lesson.get('chunks', [])), 1)
                print(f"Average chunk length: {avg_chunk_length:.0f} characters")
                
                # Check for mathematical content
                lesson_text = lesson.get('overview', '') + ' '
                for chunk in lesson.get('chunks', []):
                    lesson_text += chunk.get('content', '') + ' '
                
                math_keywords = ['equation', 'formula', 'theorem', 'algorithm', 'optimization', 'gradient', 'matrix', 'statistical']
                math_count = sum(1 for keyword in math_keywords if keyword.lower() in lesson_text.lower())
                print(f"Mathematical content indicators: {math_count}/{len(math_keywords)}")
                
                # Check for source material references
                source_indicators = ['lecture', 'course', 'mit', 'theorem', 'definition', 'proof']
                source_count = sum(1 for indicator in source_indicators if indicator.lower() in lesson_text.lower())
                print(f"Source material references: {source_count}/{len(source_indicators)}")
                
                # Display first chunk as sample
                if lesson.get('chunks'):
                    first_chunk = lesson['chunks'][0]
                    print(f"\nSAMPLE CONTENT (First Chunk):")
                    print(f"Title: {first_chunk.get('title')}")
                    print(f"Content: {first_chunk.get('content', '')[:300]}...")
                    print(f"Key Point: {first_chunk.get('key_point')}")
                
            else:
                print("✗ Failed to generate lesson")
                
        except Exception as e:
            print(f"✗ Error generating lesson: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*80}")
    print("LESSON ALIGNMENT TEST COMPLETED")
    print(f"{'='*80}")

def test_chunk_retrieval_quality():
    """Test the quality of chunk retrieval for various topics."""
    
    print(f"\n{'='*80}")
    print("TESTING CHUNK RETRIEVAL QUALITY")
    print(f"{'='*80}")
    
    try:
        base_dir = os.path.dirname(__file__)
        chunk_files = [
            os.path.join(base_dir, 'math_ml_chunks.json'),
            os.path.join(base_dir, 'mit_ocw_chunks.json'),
        ]
        chunks = load_all_chunks(chunk_files)
        
        print(f"Loaded chunks from {len(chunk_files)} files")
        total_chunks = sum(len(chunk_list) for chunk_list in chunks.values())
        print(f"Total chunks available: {total_chunks}")
        
        # Test various queries
        test_queries = [
            "neural networks",
            "support vector machines", 
            "gradient descent",
            "machine learning",
            "classification",
            "statistical learning theory",
            "optimization",
            "convex functions",
            "empirical risk minimization"
        ]
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            relevant_chunks = find_relevant_chunks(query, chunks, top_k=3)
            print(f"Found {len(relevant_chunks)} relevant chunks")
            
            for i, (fname, chunk) in enumerate(relevant_chunks, 1):
                # Calculate relevance score manually
                query_words = set(query.lower().split())
                chunk_words = set(chunk.lower().split())
                overlap = len(query_words.intersection(chunk_words))
                print(f"  {i}. {fname} (overlap: {overlap} words)")
                print(f"     Preview: {chunk[:100]}...")
    
    except Exception as e:
        print(f"Error in chunk retrieval test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting lesson alignment tests...")
    
    # Test chunk retrieval first
    test_chunk_retrieval_quality()
    
    # Test lesson alignment
    test_lesson_alignment()
    
    print("\nAll tests completed!")
