"""
Vercel Serverless Function for Score Checker
Production-ready Flask app for Vercel deployment
"""

from flask import Flask, request, jsonify
import json
from typing import List, Dict, Set, Tuple, Optional, Any

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Define custom types
Frame = Tuple[int, Optional[int]]
Frames = List[Frame]
Painting = Dict[str, Any]

# ----------------------------------------------------------
# CORE LOGIC FUNCTIONS
# ----------------------------------------------------------

def read_and_verify_output(content: str) -> Tuple[Optional[Frames], List[str]]:
    """Reads the output file content and returns frames and warnings."""
    frames: Frames = []
    used_ids: Set[int] = set()
    line_number = 0
    warnings = []
    
    lines = content.strip().split('\n')
    if not lines:
        return None, ["ERROR: Output file is empty."]
    
    try:
        declared_frames = int(lines[0].strip())
    except (ValueError, IndexError):
        return None, ["ERROR: First line must be a valid number for frame count."]
    
    for i in range(1, len(lines)):
        line = lines[i].strip()
        if not line:
            continue
        
        line_number = i + 1
        parts = line.split()
        
        try:
            if len(parts) == 2 and parts[0] == parts[1]:
                return None, [f"ERROR on line {line_number}: Duplicate painting ID '{parts[0]}' used in the same frame."]
            
            for part in parts:
                painting_id = int(part)
                if painting_id in used_ids:
                    return None, [f"ERROR on line {line_number}: Duplicate painting ID '{painting_id}' is used more than once."]
                used_ids.add(painting_id)
            
            if len(parts) == 1:
                frames.append((int(parts[0]), None))
            elif len(parts) == 2:
                frames.append((int(parts[0]), int(parts[1])))
            else:
                warnings.append(f"WARNING on line {line_number}: Line has invalid number of parts. Skipping.")
        
        except ValueError:
            warnings.append(f"WARNING on line {line_number}: Skipping invalid line: '{line}'")
    
    if declared_frames != len(frames):
        return None, [f"ERROR: The file declared {declared_frames} frames, but found {len(frames)}."]
    
    return frames, warnings

def read_input_file(content: str) -> Tuple[Optional[Dict[int, Painting]], List[str]]:
    """Reads the input file content and returns paintings and warnings."""
    paintings: Dict[int, Painting] = {}
    warnings = []
    
    lines = content.strip().split('\n')
    if not lines:
        return None, ["ERROR: Input file is empty."]
    
    try:
        num_paintings = int(lines[0].strip())
    except (ValueError, IndexError):
        return None, ["ERROR: First line of input file must be a number."]
    
    for i in range(1, min(len(lines), num_paintings + 1)):
        line = lines[i].strip()
        if not line:
            continue
        
        parts = line.split()
        if len(parts) < 2:
            warnings.append(f"WARNING: Skipping invalid line {i+1} in input file.")
            continue
        
        orientation = parts[0]
        if orientation not in ['L', 'P']:
            warnings.append(f"WARNING: Invalid orientation '{orientation}' on line {i+1}. Skipping.")
            continue
        
        try:
            num_tags = int(parts[1])
            if len(parts) < 2 + num_tags:
                warnings.append(f"WARNING: Not enough tags on line {i+1}. Expected {num_tags}, got {len(parts)-2}.")
                continue
            
            tags = parts[2:2+num_tags]
            painting_id = i - 1
            
            paintings[painting_id] = {
                'id': painting_id,
                'orientation': orientation,
                'tags': tags
            }
        except ValueError:
            warnings.append(f"WARNING: Invalid number of tags on line {i+1}. Skipping.")
            continue
    
    if len(paintings) != num_paintings:
        warnings.append(f"WARNING: Expected {num_paintings} paintings, but parsed {len(paintings)}.")
    
    return paintings, warnings

def compute_frameglass_tags(frame: Frame, paintings: Dict[int, Painting]) -> Set[str]:
    """Computes the tags for a frameglass."""
    painting_id1, painting_id2 = frame
    
    if painting_id2 is None:
        if painting_id1 not in paintings:
            return set()
        return set(paintings[painting_id1]['tags'])
    else:
        if painting_id1 not in paintings or painting_id2 not in paintings:
            return set()
        tags1 = set(paintings[painting_id1]['tags'])
        tags2 = set(paintings[painting_id2]['tags'])
        return tags1.union(tags2)

def compute_transition_score(tags1: Set[str], tags2: Set[str]) -> int:
    """Computes the score between two consecutive frameglasses."""
    common_tags = tags1.intersection(tags2)
    only_in_tags1 = tags1 - tags2
    only_in_tags2 = tags2 - tags1
    return min(len(common_tags), len(only_in_tags1), len(only_in_tags2))

def compute_global_score(frames: Frames, paintings: Dict[int, Painting]) -> Optional[int]:
    """Computes the global score for all frameglasses."""
    if len(frames) < 2:
        return 0
    
    frameglass_tags: List[Set[str]] = []
    for frame in frames:
        tags = compute_frameglass_tags(frame, paintings)
        frameglass_tags.append(tags)
    
    total_score = 0
    for i in range(len(frameglass_tags) - 1):
        score = compute_transition_score(frameglass_tags[i], frameglass_tags[i + 1])
        total_score += score
    
    return total_score

# ----------------------------------------------------------
# FLASK ROUTES
# ----------------------------------------------------------

@app.route('/', methods=['GET', 'POST', 'OPTIONS'])
def handler():
    if request.method == 'GET':
        # Serve the HTML file for GET requests
        import os
        # Try different possible paths for index.html
        possible_paths = [
            'index.html',
            '../index.html',
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'index.html')
        ]
        for path in possible_paths:
            try:
                with open(path, 'r') as f:
                    return f.read(), 200, {'Content-Type': 'text/html'}
            except FileNotFoundError:
                continue
        # If file not found, return a simple HTML response
        return '''
        <!DOCTYPE html>
        <html>
        <head><title>Score Checker</title></head>
        <body>
            <h1>Score Checker API</h1>
            <p>Use POST /api/check to submit files</p>
        </body>
        </html>
        ''', 200, {'Content-Type': 'text/html'}
    
    # Handle POST requests for API
    return check_files()

def check_files():
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        # Handle JSON or form data
        if request.is_json:
            data = request.get_json()
            input_content = data.get('input_content', '')
            output_content = data.get('output_content', '')
        else:
            if 'input_file' not in request.files or 'output_file' not in request.files:
                response = jsonify({'success': False, 'error': 'Both input and output files are required.'})
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response
            
            input_file = request.files['input_file']
            output_file = request.files['output_file']
            
            if input_file.filename == '' or output_file.filename == '':
                response = jsonify({'success': False, 'error': 'Please select both files.'})
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response
            
            input_content = input_file.read().decode('utf-8')
            output_content = output_file.read().decode('utf-8')
        
        # Validate output file
        frames, output_warnings = read_and_verify_output(output_content)
        if frames is None:
            response = jsonify({
                'success': False,
                'error': 'Output file validation failed.',
                'warnings': output_warnings
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        
        # Read input file
        paintings, input_warnings = read_input_file(input_content)
        if paintings is None:
            response = jsonify({
                'success': False,
                'error': 'Input file validation failed.',
                'warnings': input_warnings
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        
        # Compute score
        global_score = compute_global_score(frames, paintings)
        if global_score is None:
            response = jsonify({
                'success': False,
                'error': 'Could not compute score.'
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        
        # Combine warnings
        all_warnings = output_warnings + input_warnings
        
        response = jsonify({
            'success': True,
            'num_frames': len(frames),
            'num_paintings': len(paintings),
            'global_score': global_score,
            'warnings': all_warnings
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    
    except Exception as e:
        response = jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

# Vercel Python runtime automatically detects Flask apps
# The app object is exported and Vercel will use it
# When routing /api/check to this function, Flask receives the request at /

