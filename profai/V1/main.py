from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import track
from profai_engine import ProfAIEngine
import time

console = Console()
engine = ProfAIEngine()

def welcome():
    """Welcome screen"""
    console.print(Panel.fit(
        "[bold blue]Welcome to ProfAI![/bold blue]\n"
        "Your AI-powered learning companion with emotional intelligence",
        title="🎓 ProfAI"
    ))

def get_or_create_user():
    """Get existing user or create new one"""
    console.print("\n[bold]User Setup[/bold]")
    name = Prompt.ask("What's your name?")
    
    # For simplicity, just create a new user each time
    # In a real app, you'd check for existing users
    user_id = engine.create_user(name)
    console.print(f"[green]Welcome {name}! Your ID is {user_id}[/green]")
    return user_id

def run_assessment(topic: str):
    """Run pre-lesson assessment"""
    console.print(f"\n[bold]📝 Assessment: {topic}[/bold]")
    console.print("Let's see what you already know...")
    
    questions = engine.generate_assessment_questions(topic)
    if not questions:
        console.print("[red]Error generating questions. Using default score.[/red]")
        return 5.0
    
    correct = 0
    for i, q in enumerate(questions, 1):
        console.print(f"\n[bold]Question {i}:[/bold] {q['question']}")
        for option in q['options']:
            console.print(f"  {option}")
        
        answer = Prompt.ask("Your answer (A/B/C/D)").upper()
        if answer == q['correct']:
            correct += 1
            console.print("[green]✓ Correct![/green]")
        else:
            console.print(f"[red]✗ Incorrect. The answer was {q['correct']}[/red]")
    
    score = (correct / len(questions)) * 10
    console.print(f"\n[bold]Assessment Score: {score:.1f}/10[/bold]")
    return score

def run_lesson(topic: str, user_id: str):
    """Run the main lesson"""
    user = engine.get_user(user_id)
    
    console.print(f"\n[bold]📚 Generating personalized lesson: {topic}[/bold]")
    lesson = engine.generate_lesson_content(topic, user)
    
    if not lesson:
        console.print("[red]Error generating lesson content.[/red]")
        return
    
    # Show overview
    console.print(Panel(lesson['overview'], title="📋 Lesson Overview"))
    
    if not Confirm.ask("Ready to start the lesson?"):
        return
    
    # Go through each chunk
    sentiment_data = []
    for i, chunk in enumerate(lesson['chunks'], 1):
        console.print(f"\n[bold blue]📖 Part {i}: {chunk['title']}[/bold blue]")
        console.print(chunk['content'])
        console.print(f"\n[bold]Key Point:[/bold] {chunk['key_point']}")
        
        # Get user feedback
        response = Prompt.ask("\nIn your own words, what did you understand from this section?")
        
        # Analyze sentiment
        sentiment = engine.analyze_sentiment(response)
        sentiment_data.append(sentiment)
        
        # Provide feedback based on sentiment
        if sentiment['confusion_level'] > 0.6:
            console.print(f"[yellow]💡 {sentiment['suggestion']}[/yellow]")
        elif sentiment['confidence_level'] > 0.7:
            console.print("[green]🎉 Great understanding! Let's continue.[/green]")
        
        if i < len(lesson['chunks']):
            if not Confirm.ask("Ready for the next section?"):
                break
    
    # Show key takeaways
    console.print("\n[bold green]🎯 Key Takeaways:[/bold green]")
    for takeaway in lesson['key_takeaways']:
        console.print(f"  • {takeaway}")
    
    return sentiment_data

def main():
    """Main application loop"""
    welcome()
    
    # User setup
    user_id = get_or_create_user()
    
    # Choose topic (for MVP, just use a fixed topic)
    topic = "Types of AI Models"
    console.print(f"\n[bold]Today's Topic: {topic}[/bold]")
    
    try:
        # Pre-assessment
        assessment_score = run_assessment(topic)
        
        # Update user competency
        engine.update_user_competency(user_id, topic, assessment_score)
        
        # Run lesson
        sentiment_data = run_lesson(topic, user_id)
        
        # Save session
        session_data = {
            'topic': topic,
            'pre_assessment_score': assessment_score,
            'sentiment_analysis': sentiment_data,
            'completed': True
        }
        engine.save_session(user_id, session_data)
        
        # Final message
        console.print(Panel.fit(
            "[bold green]🎉 Lesson Complete![/bold green]\n"
            f"Your progress has been saved.\n"
            f"Pre-assessment score: {assessment_score:.1f}/10",
            title="Session Summary"
        ))
        
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Thanks for using ProfAI![/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    main()