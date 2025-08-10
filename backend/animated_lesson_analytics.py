import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server environments
import numpy as np
import json
import os
import io
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from profai_engine import ProfAIEngine

class AnimatedLessonAnalytics:
    def __init__(self):
        self.engine = ProfAIEngine()
        
    def get_user_lesson_time_data(self, user_id: str) -> Dict:
        """Extract time spent data for each lesson from user sessions."""
        try:
            # Load session data
            sessions = self.engine.load_data(self.engine.sessions_file)
            user_sessions = [s for s in sessions if s.get('user_id') == user_id]
            
            # Initialize lesson time tracking
            lesson_times = {}
            
            # Process each session
            for session in user_sessions:
                topic = session.get('topic', 'Unknown Topic')
                
                # Calculate session duration
                duration = 0
                if 'start_time' in session and 'end_time' in session:
                    try:
                        start = datetime.fromisoformat(session['start_time'])
                        end = datetime.fromisoformat(session['end_time'])
                        duration = (end - start).total_seconds() / 60  # Convert to minutes
                    except:
                        duration = session.get('duration_minutes', 30)
                else:
                    duration = session.get('estimated_duration', 30)
                
                # Add to lesson times
                if topic in lesson_times:
                    lesson_times[topic] += duration
                else:
                    lesson_times[topic] = duration
            
            # If no session data, use sample data
            if not lesson_times:
                lesson_times = {
                    "Neural Networks": 65,
                    "Deep Learning": 85,
                    "Machine Learning": 45,
                    "AI Ethics": 30,
                    "Computer Vision": 55
                }
            
            return lesson_times
            
        except Exception as e:
            print(f"Error getting lesson time data: {e}")
            return {
                "Neural Networks": 65,
                "Deep Learning": 85,
                "Machine Learning": 45,
                "AI Ethics": 30,
                "Computer Vision": 55
            }
    
    def create_animated_pie_chart_frames(self, user_id: str, chart_style: str = 'default', 
                                       num_frames: int = 60) -> List[str]:
        """Create frames for an animated pie chart that fills up progressively."""
        try:
            # Get lesson time data
            lesson_times = self.get_user_lesson_time_data(user_id)
            
            if not lesson_times:
                return [self._create_no_data_chart()]
            
            # Prepare data
            lessons = list(lesson_times.keys())
            times = list(lesson_times.values())
            total_time = sum(times)
            
            # Color schemes
            color_schemes = {
                'professional': ['#2E8B57', '#4682B4', '#DAA520', '#CD853F', '#9370DB', '#DC143C'],
                'vibrant': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'],
                'monochrome': ['#2C3E50', '#34495E', '#7F8C8D', '#95A5A6', '#BDC3C7', '#ECF0F1'],
                'default': ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FF99CC', '#99CCFF']
            }
            colors = color_schemes.get(chart_style, color_schemes['default'])[:len(lessons)]
            
            frames = []
            
            # Create animation frames
            for frame in range(num_frames + 1):
                # Calculate progress (0 to 1)
                progress = frame / num_frames
                
                # Apply easing function for smooth animation
                eased_progress = self._ease_in_out_cubic(progress)
                
                # Calculate current values
                current_times = [time * eased_progress for time in times]
                current_total = sum(current_times)
                
                # Create figure
                fig, ax = plt.subplots(figsize=(10, 8), dpi=100)
                
                if current_total > 0:
                    # Create pie chart with current values
                    wedges, texts, autotexts = ax.pie(
                        current_times,
                        labels=lessons,
                        autopct=lambda pct: f'{pct:.1f}%\n({int(pct/100*current_total):.0f} min)' if pct > 0 else '',
                        startangle=90,
                        colors=colors,
                        explode=[0.05] * len(lessons),
                        shadow=True,
                        textprops={'fontsize': 10, 'weight': 'bold'}
                    )
                    
                    # Customize text
                    for autotext in autotexts:
                        autotext.set_color('white')
                        autotext.set_fontweight('bold')
                        autotext.set_fontsize(9)
                    
                    # Add progress indicator
                    ax.text(0, -1.3, f'Loading Progress: {progress*100:.0f}%', 
                           ha='center', va='center', fontsize=14, fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))
                
                # Title with animation state
                title = f'Time Spent on Lessons\nTotal: {current_total:.0f} minutes'
                if progress < 1:
                    title += f' (Loading... {progress*100:.0f}%)'
                
                ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
                
                # Equal aspect ratio
                ax.axis('equal')
                
                # Add legend
                if current_total > 0:
                    ax.legend(wedges, [f"{lesson}: {time:.0f} min" for lesson, time in zip(lessons, current_times)],
                             title="Lessons",
                             loc="center left",
                             bbox_to_anchor=(1, 0, 0.5, 1),
                             fontsize=10)
                
                plt.tight_layout()
                
                # Convert to base64
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100,
                           facecolor='white', edgecolor='none')
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                buffer.close()
                plt.close(fig)
                
                frames.append(image_base64)
            
            return frames
            
        except Exception as e:
            print(f"Error creating animated frames: {e}")
            return [self._create_error_chart()]
    
    def create_web_animated_pie_chart(self, user_id: str, chart_style: str = 'default') -> str:
        """Create an HTML/CSS/JavaScript animated pie chart for web display."""
        lesson_times = self.get_user_lesson_time_data(user_id)
        
        if not lesson_times:
            return self._create_web_no_data_chart()
        
        lessons = list(lesson_times.keys())
        times = list(lesson_times.values())
        total_time = sum(times)
        
        # Calculate percentages and cumulative angles
        percentages = [(time / total_time) * 100 for time in times]
        cumulative_angles = []
        current_angle = 0
        
        for percentage in percentages:
            angle = (percentage / 100) * 360
            cumulative_angles.append((current_angle, current_angle + angle))
            current_angle += angle
        
        # Color schemes
        color_schemes = {
            'professional': ['#2E8B57', '#4682B4', '#DAA520', '#CD853F', '#9370DB', '#DC143C'],
            'vibrant': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'],
            'monochrome': ['#2C3E50', '#34495E', '#7F8C8D', '#95A5A6', '#BDC3C7', '#ECF0F1'],
            'default': ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FF99CC', '#99CCFF']
        }
        colors = color_schemes.get(chart_style, color_schemes['default'])[:len(lessons)]
        
        # Generate SVG pie chart with CSS animations
        html_content = f"""
        <div class="animated-pie-container">
            <div class="pie-chart-title">
                <h3>Time Spent on Lessons</h3>
                <p class="total-time">Total: <span id="animated-total">0</span> minutes</p>
            </div>
            
            <div class="pie-wrapper">
                <svg class="pie-chart" viewBox="0 0 200 200" width="400" height="400">
                    <!-- Background circle -->
                    <circle cx="100" cy="100" r="80" fill="none" stroke="#f0f0f0" stroke-width="4"/>
                    
                    <!-- Animated pie slices -->
                    {''.join([self._create_svg_slice(i, lesson, time, percentage, cumulative_angles[i], colors[i]) 
                             for i, (lesson, time, percentage) in enumerate(zip(lessons, times, percentages))])}
                </svg>
                
                <!-- Legend -->
                <div class="pie-legend">
                    {''.join([f'''
                    <div class="legend-item" style="animation-delay: {i * 0.2 + 1}s;">
                        <div class="legend-color" style="background-color: {colors[i]};"></div>
                        <span class="legend-text">{lesson}: <span class="lesson-time" data-target="{time}">{time:.0f}</span> min</span>
                    </div>
                    ''' for i, (lesson, time) in enumerate(zip(lessons, times))])}
                </div>
            </div>
            
            <style>
                .animated-pie-container {{
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 20px auto;
                    padding: 20px;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }}
                
                .pie-chart-title {{
                    text-align: center;
                    margin-bottom: 20px;
                }}
                
                .pie-chart-title h3 {{
                    margin: 0;
                    color: #2c3e50;
                    font-size: 1.5em;
                }}
                
                .total-time {{
                    margin: 10px 0;
                    color: #7f8c8d;
                    font-size: 1.1em;
                }}
                
                .pie-wrapper {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 40px;
                    flex-wrap: wrap;
                }}
                
                .pie-chart {{
                    transform: rotate(-90deg);
                    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
                }}
                
                .pie-slice {{
                    stroke-dasharray: 0 1000;
                    animation: fillSlice 2s ease-in-out forwards;
                    transform-origin: 100px 100px;
                }}
                
                .pie-legend {{
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                    min-width: 250px;
                }}
                
                .legend-item {{
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    opacity: 0;
                    animation: fadeInLegend 0.5s ease-in-out forwards;
                }}
                
                .legend-color {{
                    width: 16px;
                    height: 16px;
                    border-radius: 50%;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.2);
                }}
                
                .legend-text {{
                    font-size: 14px;
                    color: #2c3e50;
                    font-weight: 500;
                }}
                
                @keyframes fillSlice {{
                    from {{
                        stroke-dasharray: 0 1000;
                    }}
                    to {{
                        stroke-dasharray: var(--dash-array) 1000;
                    }}
                }}
                
                @keyframes fadeInLegend {{
                    from {{
                        opacity: 0;
                        transform: translateX(-20px);
                    }}
                    to {{
                        opacity: 1;
                        transform: translateX(0);
                    }}
                }}
                
                @keyframes countUp {{
                    from {{ opacity: 0; }}
                    to {{ opacity: 1; }}
                }}
                
                /* Responsive design */
                @media (max-width: 768px) {{
                    .pie-wrapper {{
                        flex-direction: column;
                        gap: 20px;
                    }}
                    
                    .pie-chart {{
                        width: 300px;
                        height: 300px;
                    }}
                    
                    .pie-legend {{
                        width: 100%;
                        max-width: 300px;
                    }}
                }}
            </style>
            
            <script>
                // Animate the total time counter
                function animateCounter(element, target, duration = 2000) {{
                    let start = 0;
                    const startTime = performance.now();
                    
                    function updateCounter(currentTime) {{
                        const elapsed = currentTime - startTime;
                        const progress = Math.min(elapsed / duration, 1);
                        const current = Math.floor(start + (target - start) * progress);
                        
                        element.textContent = current;
                        
                        if (progress < 1) {{
                            requestAnimationFrame(updateCounter);
                        }}
                    }}
                    
                    requestAnimationFrame(updateCounter);
                }}
                
                // Start animations when the chart is visible
                const observer = new IntersectionObserver((entries) => {{
                    entries.forEach(entry => {{
                        if (entry.isIntersecting) {{
                            // Animate total time
                            const totalElement = document.getElementById('animated-total');
                            animateCounter(totalElement, {total_time:.0f});
                            
                            // Animate individual lesson times
                            document.querySelectorAll('.lesson-time').forEach((element, index) => {{
                                const target = parseFloat(element.getAttribute('data-target'));
                                setTimeout(() => {{
                                    animateCounter(element, target, 1500);
                                }}, index * 200 + 500);
                            }});
                            
                            observer.unobserve(entry.target);
                        }}
                    }});
                }});
                
                observer.observe(document.querySelector('.animated-pie-container'));
            </script>
        </div>
        """
        
        return html_content
    
    def _create_svg_slice(self, index: int, lesson: str, time: float, percentage: float, 
                         angles: Tuple[float, float], color: str) -> str:
        """Create an SVG slice for the animated pie chart."""
        start_angle, end_angle = angles
        
        # Calculate the stroke-dasharray for the slice
        circumference = 2 * 3.14159 * 80  # radius = 80
        dash_length = (percentage / 100) * circumference
        
        # Calculate path for the slice
        start_rad = start_angle * 3.14159 / 180
        end_rad = end_angle * 3.14159 / 180
        
        # Large arc flag
        large_arc = 1 if (end_angle - start_angle) > 180 else 0
        
        # Calculate coordinates
        x1 = 100 + 80 * np.cos(start_rad)
        y1 = 100 + 80 * np.sin(start_rad)
        x2 = 100 + 80 * np.cos(end_rad)
        y2 = 100 + 80 * np.sin(end_rad)
        
        if percentage > 0:
            path = f"M 100 100 L {x1} {y1} A 80 80 0 {large_arc} 1 {x2} {y2} Z"
        else:
            path = ""
        
        return f'''
        <path class="pie-slice" 
              d="{path}"
              fill="{color}"
              stroke="white"
              stroke-width="2"
              style="--dash-array: {dash_length:.2f}; animation-delay: {index * 0.3}s;"
              opacity="0.9">
            <title>{lesson}: {time:.0f} minutes ({percentage:.1f}%)</title>
        </path>
        '''
    
    def _ease_in_out_cubic(self, t: float) -> float:
        """Cubic easing function for smooth animation."""
        if t < 0.5:
            return 4 * t * t * t
        return 1 - pow(-2 * t + 2, 3) / 2
    
    def _create_no_data_chart(self) -> str:
        """Create a placeholder chart when no data is available."""
        plt.figure(figsize=(8, 6), dpi=100)
        plt.text(0.5, 0.5, 'No lesson data available\nStart learning to see your progress!', 
                ha='center', va='center', fontsize=16, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))
        plt.xlim(0, 1)
        plt.ylim(0, 1)
        plt.axis('off')
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100,
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        plt.close()
        
        return image_base64
    
    def _create_web_no_data_chart(self) -> str:
        """Create a web-based no data chart."""
        return """
        <div style="text-align: center; padding: 40px; background: white; border-radius: 12px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            <h3 style="color: #7f8c8d;">No lesson data available</h3>
            <p style="color: #95a5a6;">Start learning to see your animated progress!</p>
        </div>
        """
    
    def _create_error_chart(self) -> str:
        """Create an error chart when chart generation fails."""
        plt.figure(figsize=(8, 6), dpi=100)
        plt.text(0.5, 0.5, 'Error generating chart\nPlease try again later', 
                ha='center', va='center', fontsize=16, fontweight='bold', color='red',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.7))
        plt.xlim(0, 1)
        plt.ylim(0, 1)
        plt.axis('off')
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100,
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        plt.close()
        
        return image_base64

# Example usage
if __name__ == "__main__":
    analytics = AnimatedLessonAnalytics()
    
    # Test animated frames
    print("Creating animated pie chart frames...")
    frames = analytics.create_animated_pie_chart_frames("user_1", "vibrant", 30)
    print(f"Created {len(frames)} animation frames")
    
    # Test web animation
    print("Creating web-based animated pie chart...")
    web_chart = analytics.create_web_animated_pie_chart("user_1", "professional")
    
    # Save web chart for testing
    with open('animated_pie_chart.html', 'w', encoding='utf-8') as f:
        f.write(web_chart)
    print("Web animated chart saved as 'animated_pie_chart.html'")
