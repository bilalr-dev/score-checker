"""
Vercel Serverless Function for Score Checker
Production-ready Flask app for Vercel deployment
"""

from flask import Flask, request, jsonify, Response
import json
from typing import List, Dict, Set, Tuple, Optional, Any

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# HTML content embedded directly
HTML_CONTENT = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Robot Satisfaction Score Checker</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); padding: 40px; }
        h1 { color: #333; text-align: center; margin-bottom: 10px; font-size: 2em; }
        .subtitle { text-align: center; color: #666; margin-bottom: 30px; }
        .file-input-group { margin-bottom: 25px; }
        label { display: block; margin-bottom: 8px; color: #333; font-weight: 600; }
        .file-input-wrapper { position: relative; display: inline-block; width: 100%; }
        input[type="file"] { width: 100%; padding: 12px; border: 2px dashed #667eea; border-radius: 8px; background: #f8f9ff; cursor: pointer; font-size: 14px; }
        input[type="file"]:hover { border-color: #764ba2; background: #f0f2ff; }
        .check-button { width: 100%; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; margin-top: 10px; }
        .check-button:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4); }
        .check-button:active { transform: translateY(0); }
        .check-button:disabled { background: #ccc; cursor: not-allowed; transform: none; }
        .results { margin-top: 30px; padding: 20px; border-radius: 8px; display: none; }
        .results.success { background: #d4edda; border: 2px solid #28a745; display: block; }
        .results.error { background: #f8d7da; border: 2px solid #dc3545; display: block; }
        .results h2 { margin-bottom: 15px; color: #333; }
        .score-display { font-size: 2.5em; font-weight: bold; color: #28a745; text-align: center; margin: 20px 0; }
        .info-item { margin: 10px 0; padding: 10px; background: white; border-radius: 5px; }
        .warnings { margin-top: 15px; padding: 15px; background: #fff3cd; border-left: 4px solid #ffc107; border-radius: 4px; }
        .warnings h3 { margin-bottom: 10px; color: #856404; }
        .warnings ul { list-style: none; padding-left: 0; }
        .warnings li { padding: 5px 0; color: #856404; }
        .loading { text-align: center; padding: 20px; display: none; }
        .loading.active { display: block; }
        .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #667eea; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Robot Satisfaction Score Checker</h1>
        <p class="subtitle">Upload your input and output files to validate and compute scores</p>
        <form id="checkForm">
            <div class="file-input-group">
                <label for="input_file">Input File (.txt)</label>
                <div class="file-input-wrapper">
                    <input type="file" id="input_file" name="input_file" accept=".txt" required>
                </div>
            </div>
            <div class="file-input-group">
                <label for="output_file">Output File (.txt)</label>
                <div class="file-input-wrapper">
                    <input type="file" id="output_file" name="output_file" accept=".txt" required>
                </div>
            </div>
            <button type="submit" class="check-button" id="checkButton">Check & Score</button>
        </form>
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p style="margin-top: 10px;">Processing files...</p>
        </div>
        <div class="results" id="results"></div>
    </div>
    <script>
        const API_URL = '/api/check';
        document.getElementById('checkForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData();
            const inputFile = document.getElementById('input_file').files[0];
            const outputFile = document.getElementById('output_file').files[0];
            if (!inputFile || !outputFile) { showError('Please select both input and output files.'); return; }
            formData.append('input_file', inputFile);
            formData.append('output_file', outputFile);
            const checkButton = document.getElementById('checkButton');
            const loading = document.getElementById('loading');
            const results = document.getElementById('results');
            checkButton.disabled = true;
            loading.classList.add('active');
            results.style.display = 'none';
            try {
                const response = await fetch(API_URL, { method: 'POST', body: formData });
                const data = await response.json();
                if (data.success) { showSuccess(data); } else { showError(data.error || 'An error occurred.', data.warnings); }
            } catch (error) { showError('Network error: ' + error.message); } finally {
                checkButton.disabled = false;
                loading.classList.remove('active');
            }
        });
        function showSuccess(data) {
            const results = document.getElementById('results');
            results.className = 'results success';
            results.innerHTML = `<h2>✅ Success!</h2><div class="score-display">${data.global_score}</div><p style="text-align: center; color: #666; margin-bottom: 20px;">Global Robotic Satisfaction Score</p><div class="info-item"><strong>Number of frameglasses:</strong> ${data.num_frames}</div><div class="info-item"><strong>Number of paintings:</strong> ${data.num_paintings}</div>${data.warnings && data.warnings.length > 0 ? `<div class="warnings"><h3>⚠️ Warnings</h3><ul>${data.warnings.map(w => '<li>' + w + '</li>').join('')}</ul></div>` : ''}`;
            results.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
        function showError(error, warnings = []) {
            const results = document.getElementById('results');
            results.className = 'results error';
            results.innerHTML = `<h2>❌ Error</h2><p style="margin: 15px 0; color: #721c24;">${error}</p>${warnings && warnings.length > 0 ? `<div class="warnings"><h3>Details</h3><ul>${warnings.map(w => '<li>' + w + '</li>').join('')}</ul></div>` : ''}`;
            results.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    </script>
</body>
</html>'''

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
@app.route('/api/check', methods=['POST', 'OPTIONS'])
def handler():
    try:
        if request.method == 'GET':
            # Serve the embedded HTML for GET requests
            return Response(HTML_CONTENT, mimetype='text/html', status=200)
        
        # Handle POST requests for API
        return check_files()
    except Exception as e:
        # Return error response instead of crashing
        return jsonify({'error': str(e)}), 500

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
# The app object is the default export
# Make sure app is accessible at module level
if __name__ == '__main__':
    app.run(debug=True)

