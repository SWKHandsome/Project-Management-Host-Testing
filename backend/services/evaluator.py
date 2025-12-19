"""
Assignment evaluation service
Evaluates programming logic assignments based on rubric
"""
import re
from config import Config
from models.assessment import Assessment

class AssignmentEvaluator:
    """Rubric-based assignment evaluator"""
    
    def __init__(self):
        self.rubric = Config.RUBRIC
    
    def evaluate(self, submission):
        """Evaluate a submission and return assessment"""
        try:
            # Get file content
            file_content = submission.get('file_content', '')
            
            # Evaluate each rubric category
            breakdown = {}
            breakdown['logic_design'] = self.evaluate_logic_design(file_content)
            breakdown['flowchart'] = self.evaluate_flowchart(file_content)
            breakdown['pseudocode'] = self.evaluate_pseudocode(file_content)
            breakdown['formatting'] = self.evaluate_formatting(file_content)
            breakdown['documentation'] = self.evaluate_documentation(file_content)
            
            # Calculate total score
            total_score = Assessment.calculate_total_score(breakdown)
            grade = Assessment.get_grade(total_score)
            
            # Generate feedback
            feedback = self.generate_feedback(breakdown, total_score)
            
            return {
                'breakdown': breakdown,
                'total_score': total_score,
                'grade': grade,
                'feedback': feedback,
                'strengths': feedback['strengths'],
                'improvements': feedback['improvements'],
                'recommendations': feedback['recommendations']
            }
            
        except Exception as e:
            print(f"  ✗ Error during evaluation: {e}")
            return self.default_assessment()
    
    def evaluate_logic_design(self, content):
        """Evaluate logic design (30%)"""
        weight = self.rubric['logic_design']['weight']
        score = 0
        feedback = []
        
        # Check for minimum content quality - be very strict
        words = [w for w in content.split() if len(w) > 2 and not w.isdigit()]
        unique_words = set(word.lower() for word in words)
        lines = [l for l in content.split('\n') if l.strip()]
        
        # Reject garbage/minimal content
        if (len(content.strip()) < 200 or 
            len(words) < 40 or 
            len(unique_words) < 25 or 
            len(lines) < 5):
            feedback.append("Insufficient meaningful content - needs at least 40+ words, 25+ unique words, 5+ lines")
            return {
                'score': 0,
                'max_score': weight,
                'percentage': 0,
                'feedback': feedback
            }
        
        # Check for problem understanding keywords
        problem_keywords = ['problem', 'objective', 'goal', 'requirement', 'input', 'output', 'task', 'assignment', 'question', 'need', 'ask']
        problem_score = sum(1 for keyword in problem_keywords if keyword.lower() in content.lower())
        if problem_score >= 1:
            score += min(problem_score * 3, 12)
            feedback.append("Problem understanding demonstrated")
        
        # Check for solution elements
        solution_keywords = ['algorithm', 'solution', 'approach', 'method', 'process', 'steps', 'procedure', 'way', 'how']
        solution_score = sum(1 for keyword in solution_keywords if keyword.lower() in content.lower())
        if solution_score >= 1:
            score += min(solution_score * 3, 10)
            feedback.append("Solution approach identified")
        
        # Check for logical flow
        if 'if' in content.lower() or 'else' in content.lower() or 'when' in content.lower() or 'case' in content.lower():
            score += 8
            feedback.append("Conditional logic present")
        
        # Check for loop constructs
        loop_keywords = ['while', 'for', 'repeat', 'loop', 'iterate', 'do while', 'until', 'each']
        if any(keyword in content.lower() for keyword in loop_keywords):
            score += 8
            feedback.append("Loop structures identified")
        
        # Check for edge cases
        edge_keywords = ['edge', 'validation', 'error', 'check', 'validate', 'boundary', 'condition', 'test']
        edge_count = sum(1 for keyword in edge_keywords if keyword.lower() in content.lower())
        if edge_count >= 1:
            score += min(edge_count * 3, 8)
            feedback.append("Edge case consideration present")
        
        # Check for variables and data handling
        var_patterns = [r'\b[a-z_][a-z0-9_]*\s*=', r'variable', r'var\s+', r'data', r'value', r'store']
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in var_patterns):
            score += 5
            feedback.append("Variable usage identified")
        
        # Bonus for having reasonable content length
        if len(content) > 500:
            score += 8
            feedback.append("Comprehensive content")
        elif len(content) > 300:
            score += 5
            feedback.append("Good content depth")
        elif len(content) > 150:
            score += 3
            feedback.append("Adequate content")
        
        # Bonus for having multiple lines (shows effort)
        if len(content.split('\n')) > 10:
            score += 4
            feedback.append("Well-structured content")
        
        # Normalize to weight
        final_score = min((score / 62) * weight, weight)
        
        return {
            'score': round(final_score, 2),
            'max_score': weight,
            'percentage': round((final_score / weight) * 100, 2),
            'feedback': feedback if feedback else ['Logic design could be more explicit']
        }
    
    def evaluate_flowchart(self, content):
        """Evaluate flowchart (25%)"""
        weight = self.rubric['flowchart']['weight']
        score = 0
        feedback = []
        
        # Check for minimum content quality
        words = [w for w in content.split() if len(w) > 2 and not w.isdigit()]
        if len(words) < 30:
            feedback.append("Insufficient content - needs at least 30+ meaningful words")
            return {
                'score': 0,
                'max_score': weight,
                'percentage': 0,
                'feedback': feedback
            }
        
        # Check for flowchart indicators (be more flexible)
        flowchart_keywords = ['flowchart', 'flow chart', 'diagram', 'flow', 'chart', 'visual', 'graph', 'figure']
        flowchart_score = sum(1 for keyword in flowchart_keywords if keyword.lower() in content.lower())
        if flowchart_score >= 1:
            score += min(flowchart_score * 3, 8)
            feedback.append("Flowchart/diagram present")
        
        # Check for flowchart symbols
        symbols = ['start', 'end', 'process', 'decision', 'input', 'output', 'step', 'box', 'action']
        symbol_score = sum(1 for symbol in symbols if symbol.lower() in content.lower())
        
        if symbol_score >= 3:
            score += 12
            feedback.append("Good variety of flowchart symbols")
        elif symbol_score >= 2:
            score += 8
            feedback.append("Basic flowchart symbols present")
        elif symbol_score >= 1:
            score += 5
            feedback.append("Some flowchart elements present")
        
        # Check for flow direction
        if 'arrow' in content.lower() or '->' in content or '=>' in content or 'direction' in content.lower() or 'next' in content.lower():
            score += 5
            feedback.append("Flow direction indicated")
        
        # Check for proper structure
        if 'start' in content.lower() or 'begin' in content.lower():
            score += 4
            feedback.append("Has starting point")
        
        if 'end' in content.lower() or 'stop' in content.lower():
            score += 3
            feedback.append("Has ending point")
        
        # Bonus for any visual/diagram content
        visual_keywords = ['show', 'display', 'illustrate', 'represent', 'draw']
        if any(keyword in content.lower() for keyword in visual_keywords):
            score += 5
            feedback.append("Visual representation described")
        
        # Bonus for reasonable length
        if len(content) > 200:
            score += 4
        
        # Normalize to weight
        final_score = min((score / 41) * weight, weight)
        
        return {
            'score': round(final_score, 2),
            'max_score': weight,
            'percentage': round((final_score / weight) * 100, 2),
            'feedback': feedback if feedback else ['Include clear flowchart with proper symbols']
        }
    
    def evaluate_pseudocode(self, content):
        """Evaluate pseudocode (25%)"""
        weight = self.rubric['pseudocode']['weight']
        score = 0
        feedback = []
        
        # Check for minimum content quality
        words = [w for w in content.split() if len(w) > 2 and not w.isdigit()]
        if len(words) < 30:
            feedback.append("Insufficient content - needs at least 30+ meaningful words")
            return {
                'score': 0,
                'max_score': weight,
                'percentage': 0,
                'feedback': feedback
            }
        
        # Check for pseudocode indicators (be more flexible)
        pseudo_keywords = ['pseudocode', 'pseudo code', 'pseudo', 'code', 'algorithm', 'logic', 'program']
        has_pseudo = any(keyword in content.lower() for keyword in pseudo_keywords)
        
        if has_pseudo:
            score += 6
            feedback.append("Pseudocode section identified")
        
        # Check for structure
        if ('begin' in content.lower() or 'start' in content.lower()) and 'end' in content.lower():
            score += 8
            feedback.append("Proper pseudocode structure")
        elif 'begin' in content.lower() or 'start' in content.lower() or 'end' in content.lower():
            score += 4
            feedback.append("Has structure keywords")
        
        # Check for variables
        var_patterns = [r'\b[a-z_][a-z0-9_]*\s*=', r'variable', r'set\s+', r'let\s+', r'get\s+']
        var_matches = sum(1 for pattern in var_patterns for _ in re.finditer(pattern, content, re.IGNORECASE))
        if var_matches >= 1:
            score += min(var_matches * 3, 8)
            feedback.append("Variable usage present")
        
        # Check for indentation (proxy for structure)
        lines = content.split('\n')
        indented_lines = sum(1 for line in lines if line.startswith('    ') or line.startswith('\t'))
        total_lines = len([l for l in lines if l.strip()])
        
        if total_lines > 3 and indented_lines >= 1:
            score += 6
            feedback.append("Good code structure")
        elif indented_lines >= 1:
            score += 3
        
        # Check for control structures
        control_keywords = ['if', 'then', 'else', 'while', 'for', 'repeat', 'loop', 'do', 'when']
        control_count = sum(1 for keyword in control_keywords if keyword.lower() in content.lower())
        if control_count >= 1:
            score += min(control_count * 3, 8)
            feedback.append("Control structures included")
        
        # Bonus for reasonable structure
        if total_lines > 5:
            score += 4
            feedback.append("Adequate code length")
        
        # Bonus for any logical thinking shown
        thinking_keywords = ['calculate', 'compute', 'determine', 'find', 'get', 'set', 'update']
        if any(keyword in content.lower() for keyword in thinking_keywords):
            score += 5
            feedback.append("Logical operations present")
        
        # Normalize to weight
        final_score = min((score / 44) * weight, weight)
        
        return {
            'score': round(final_score, 2),
            'max_score': weight,
            'percentage': round((final_score / weight) * 100, 2),
            'feedback': feedback if feedback else ['Improve pseudocode clarity and structure']
        }
    
    def evaluate_formatting(self, content):
        """Evaluate formatting (10%)"""
        weight = self.rubric['formatting']['weight']
        score = 0
        feedback = []
        
        lines = content.split('\n')
        words = content.split()
        
        # Check for minimum content quality
        real_words = [w for w in words if len(w) > 2 and not w.isdigit()]
        if len(content.strip()) < 200 or len(real_words) < 40:
            feedback.append("Insufficient content length - needs at least 40+ meaningful words")
            return {
                'score': 0,
                'max_score': weight,
                'percentage': 0,
                'feedback': feedback
            }
        
        # Check for sections/headers
        header_patterns = [r'^[A-Z][A-Za-z\s]+:', r'^#+\s+', r'^\d+\.', r'^[A-Z][A-Za-z\s]{3,}$']
        headers = sum(1 for line in lines if any(re.match(pattern, line) for pattern in header_patterns))
        
        if headers >= 2:
            score += 4
            feedback.append("Well-organized with sections")
        elif headers >= 1:
            score += 3
            feedback.append("Some organization present")
        
        # Check for consistent formatting
        empty_lines = sum(1 for line in lines if line.strip() == '')
        non_empty = len([l for l in lines if l.strip()])
        
        if non_empty > 3:
            score += 3
            feedback.append("Good content structure")
        
        # Check for adequate content length
        if len(content) > 300:
            score += 4
            feedback.append("Good content length")
        elif len(content) > 150:
            score += 3
            feedback.append("Adequate content length")
        
        # Check for professional appearance
        if not re.search(r'[a-z]{80,}', content):
            score += 3
            feedback.append("Professional appearance")
        
        # Bonus for showing any effort
        if non_empty >= 5:
            score += 3
            feedback.append("Shows adequate effort")
        
        # Normalize to weight
        final_score = min((score / 17) * weight, weight)
        
        return {
            'score': round(final_score, 2),
            'max_score': weight,
            'percentage': round((final_score / weight) * 100, 2),
            'feedback': feedback if feedback else ['Improve document organization']
        }
    
    def evaluate_documentation(self, content):
        """Evaluate documentation (10%)"""
        weight = self.rubric['documentation']['weight']
        score = 0
        feedback = []
        
        # Check for minimum content quality
        words = [w for w in content.split() if len(w) > 2 and not w.isdigit()]
        if len(words) < 30:
            feedback.append("Insufficient content for documentation - needs at least 30+ meaningful words")
            return {
                'score': 0,
                'max_score': weight,
                'percentage': 0,
                'feedback': feedback
            }
        
        # Check for comments
        comment_indicators = ['//', '/*', '#', 'comment', 'note', 'remarks', 'explanation', 'describe']
        comment_score = sum(1 for indicator in comment_indicators if indicator.lower() in content.lower())
        
        if comment_score >= 1:
            score += min(comment_score * 3, 6)
            feedback.append("Comments/documentation present")
        
        # Check for explanations
        explanation_keywords = ['explain', 'description', 'purpose', 'because', 'this will', 'in order to', 'to', 'function', 'used for', 'how', 'why', 'what']
        explain_score = sum(1 for keyword in explanation_keywords if keyword.lower() in content.lower())
        
        if explain_score >= 1:
            score += min(explain_score * 2, 6)
            feedback.append("Explanations provided")
        
        # Bonus for any descriptive text
        if len(content) > 200:
            score += 4
            feedback.append("Good documentation length")
        
        # Normalize to weight
        final_score = min((score / 16) * weight, weight)
        
        return {
            'score': round(final_score, 2),
            'max_score': weight,
            'percentage': round((final_score / weight) * 100, 2),
            'feedback': feedback if feedback else ['Add more comments and explanations']
        }
    
    def generate_feedback(self, breakdown, total_score):
        """Generate overall feedback based on assessment"""
        strengths = []
        improvements = []
        recommendations = []
        
        # Analyze each category
        for category, data in breakdown.items():
            percentage = data['percentage']
            category_name = category.replace('_', ' ').title()
            
            if percentage >= 80:
                strengths.append(f"Strong {category_name} ({percentage}%)")
            elif percentage < 60:
                improvements.append(f"{category_name} needs improvement ({percentage}%)")
        
        # Generate recommendations based on total score
        if total_score >= 85:
            recommendations.append("Excellent work! Keep maintaining this high standard.")
        elif total_score >= 70:
            recommendations.append("Good job overall. Focus on the weaker areas for improvement.")
        elif total_score >= 50:
            recommendations.append("Satisfactory work. Review the rubric and strengthen weak areas.")
        else:
            recommendations.append("Needs significant improvement. Seek help and review course materials.")
        
        # Add specific recommendations
        if breakdown['logic_design']['percentage'] < 70:
            recommendations.append("Improve problem-solving approach and algorithm design.")
        
        if breakdown['flowchart']['percentage'] < 70:
            recommendations.append("Include detailed flowcharts with proper symbols.")
        
        if breakdown['pseudocode']['percentage'] < 70:
            recommendations.append("Write clearer pseudocode with proper structure.")
        
        if breakdown['documentation']['percentage'] < 70:
            recommendations.append("Add more comments and explanations to your work.")
        
        return {
            'strengths': strengths if strengths else ['Continue practicing programming logic'],
            'improvements': improvements if improvements else ['Maintain current performance level'],
            'recommendations': recommendations
        }
    
    def default_assessment(self):
        """Return default assessment for errors"""
        return {
            'breakdown': {},
            'total_score': 0,
            'grade': 'F',
            'feedback': {
                'strengths': [],
                'improvements': ['Unable to evaluate submission'],
                'recommendations': ['Please resubmit with correct file format']
            },
            'strengths': [],
            'improvements': ['Unable to evaluate submission'],
            'recommendations': ['Please resubmit with correct file format']
        }
