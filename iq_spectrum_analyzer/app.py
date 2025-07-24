#!/usr/bin/env python3
"""
IQ Spectrum Analyzer - Web Application
A comprehensive web-based IQ signal analyzer with real-time spectrum and waterfall displays.
"""

import os
import json
import uuid
from datetime import datetime
from pathlib import Path
import numpy as np
import io
import base64

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from werkzeug.utils import secure_filename
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from backend.signal_processor import SignalProcessor
from backend.database_manager import DatabaseManager
from backend.file_handler import FileHandler
from config.settings import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Initialize extensions
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Initialize components
db_manager = DatabaseManager()
signal_processor = SignalProcessor()
file_handler = FileHandler()

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    """Main application page."""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle IQ file upload."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get form data
        sample_rate = float(request.form.get('sample_rate', 2048000))
        data_type = request.form.get('data_type', 'auto')
        center_freq = float(request.form.get('center_freq', 0))
        
        # Secure filename and save
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        file.save(filepath)
        
        # Get file info
        file_info = file_handler.get_file_info(filepath, data_type)
        
        # Create session record in database
        session_data = {
            'session_id': str(uuid.uuid4()),
            'filename': filename,
            'filepath': unique_filename,
            'upload_time': datetime.utcnow(),
            'sample_rate': sample_rate,
            'data_type': data_type,
            'center_freq': center_freq,
            'file_info': file_info,
            'status': 'uploaded'
        }
        
        session_id = db_manager.create_session(session_data)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'file_info': file_info,
            'message': 'File uploaded successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze/<session_id>')
def analyze_signal(session_id):
    """Analyze uploaded IQ signal."""
    try:
        # Get session from database
        session = db_manager.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Load IQ data
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], session['filepath'])
        iq_data = file_handler.load_iq_data(
            filepath, 
            session['data_type'], 
            session['sample_rate']
        )
        
        # Analyze signal
        analysis_results = signal_processor.analyze_signal(
            iq_data, 
            session['sample_rate']
        )
        
        # Generate spectrum plot
        spectrum_data = signal_processor.generate_spectrum_data(
            iq_data, 
            session['sample_rate']
        )
        
        # Update session with analysis results
        db_manager.update_session(session_id, {
            'analysis_results': analysis_results,
            'spectrum_data': spectrum_data,
            'status': 'analyzed'
        })
        
        return jsonify({
            'success': True,
            'analysis': analysis_results,
            'spectrum': spectrum_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/demodulate/<session_id>')
def demodulate_signal(session_id):
    """Demodulate signal with specified parameters."""
    try:
        # Get parameters
        demod_type = request.args.get('type', 'fm')
        center_freq_offset = float(request.args.get('center_freq', 0))
        bandwidth = request.args.get('bandwidth')
        
        # Get session
        session = db_manager.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Load IQ data
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], session['filepath'])
        iq_data = file_handler.load_iq_data(
            filepath, 
            session['data_type'], 
            session['sample_rate']
        )
        
        # Demodulate
        audio_data = signal_processor.demodulate(
            iq_data,
            demod_type=demod_type,
            sample_rate=session['sample_rate'],
            center_freq=center_freq_offset,
            bandwidth=float(bandwidth) if bandwidth else None
        )
        
        # Save audio file
        audio_filename = f"audio_{session_id}_{demod_type}.wav"
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
        file_handler.save_audio(audio_data, audio_path)
        
        # Update session
        db_manager.update_session(session_id, {
            'demodulation_results': {
                'type': demod_type,
                'audio_file': audio_filename,
                'center_freq': center_freq_offset,
                'bandwidth': bandwidth
            },
            'status': 'demodulated'
        })
        
        return jsonify({
            'success': True,
            'audio_file': audio_filename,
            'download_url': f'/api/download/{session_id}/audio'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<session_id>/<file_type>')
def download_file(session_id, file_type):
    """Download processed files."""
    try:
        session = db_manager.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        if file_type == 'audio' and 'demodulation_results' in session:
            filename = session['demodulation_results']['audio_file']
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            return send_file(filepath, as_attachment=True)
        
        return jsonify({'error': 'File not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/waterfall/<session_id>')
def get_waterfall_data(session_id):
    """Get waterfall plot data."""
    try:
        session = db_manager.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Load IQ data
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], session['filepath'])
        iq_data = file_handler.load_iq_data(
            filepath, 
            session['data_type'], 
            session['sample_rate']
        )
        
        # Generate waterfall data
        waterfall_data = signal_processor.generate_waterfall_data(
            iq_data, 
            session['sample_rate']
        )
        
        return jsonify({
            'success': True,
            'waterfall': waterfall_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions')
def get_sessions():
    """Get all analysis sessions."""
    try:
        sessions = db_manager.get_all_sessions()
        return jsonify({
            'success': True,
            'sessions': sessions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/<session_id>')
def get_session(session_id):
    """Get specific session details."""
    try:
        session = db_manager.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        return jsonify({
            'success': True,
            'session': session
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print(f'Client connected: {request.sid}')
    emit('status', {'msg': 'Connected to IQ Spectrum Analyzer'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print(f'Client disconnected: {request.sid}')

@socketio.on('join_analysis')
def handle_join_analysis(data):
    """Join analysis room for real-time updates."""
    session_id = data['session_id']
    join_room(session_id)
    emit('status', {'msg': f'Joined analysis session {session_id}'})

@socketio.on('leave_analysis')
def handle_leave_analysis(data):
    """Leave analysis room."""
    session_id = data['session_id']
    leave_room(session_id)
    emit('status', {'msg': f'Left analysis session {session_id}'})

@socketio.on('request_realtime_spectrum')
def handle_realtime_spectrum(data):
    """Handle real-time spectrum requests."""
    try:
        session_id = data['session_id']
        fft_size = data.get('fft_size', 1024)
        overlap = data.get('overlap', 0.5)
        
        # Get session
        session = db_manager.get_session(session_id)
        if not session:
            emit('error', {'msg': 'Session not found'})
            return
        
        # Generate real-time spectrum data
        # This would be implemented to stream data in chunks
        emit('spectrum_update', {
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat(),
            'spectrum': []  # Real spectrum data would go here
        })
        
    except Exception as e:
        emit('error', {'msg': str(e)})

if __name__ == '__main__':
    # Initialize database
    db_manager.initialize_database()
    
    # Run the application
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=5000, 
        debug=True,
        allow_unsafe_werkzeug=True
    )