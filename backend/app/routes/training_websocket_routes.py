"""
Training Websocket Routes
Handles websocket connections for real-time training progress updates
"""

from flask import request
from flask_socketio import emit, join_room, leave_room
from services.training_websocket_service import get_training_websocket_service

# SocketIO instance will be imported from the main app
socketio = None

def init_websocket_routes(socketio_instance):
    """Initialize websocket routes with the socketio instance"""
    global socketio
    socketio = socketio_instance
    
    @socketio.on('connect')
    def handle_connect():
        """Handle websocket connection"""
        print(f"🔌 Client connected: {request.sid}")

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle websocket disconnection"""
        print(f"🔌 Client disconnected: {request.sid}")

    @socketio.on('join_training_room')
    def handle_join_training_room(data):
        """Join a training job room for real-time updates"""
        job_id = data.get('job_id')
        if job_id:
            join_room(f'training_job_{job_id}')
            print(f"🔌 Client {request.sid} joined training room for job {job_id}")
            emit('joined_room', {'job_id': job_id, 'room': f'training_job_{job_id}'})

    @socketio.on('leave_training_room')
    def handle_leave_training_room(data):
        """Leave a training job room"""
        job_id = data.get('job_id')
        if job_id:
            leave_room(f'training_job_{job_id}')
            print(f"🔌 Client {request.sid} left training room for job {job_id}")
            emit('left_room', {'job_id': job_id})

    @socketio.on('get_training_status')
    def handle_get_training_status(data):
        """Get current training status for a job"""
        job_id = data.get('job_id')
        websocket_service = get_training_websocket_service()
        
        if websocket_service and job_id:
            active_jobs = websocket_service.get_active_jobs()
            if job_id in active_jobs:
                job_info = active_jobs[job_id]
                emit('training_status', {
                    'job_id': job_id,
                    'status': job_info['status'],
                    'current_step': job_info['current_step'],
                    'total_steps': job_info['total_steps'],
                    'progress_percent': (job_info['current_step'] / job_info['total_steps']) * 100
                })
            else:
                emit('training_status', {
                    'job_id': job_id,
                    'status': 'NOT_FOUND',
                    'message': 'Training session not found'
                })
        else:
            emit('training_status', {
                'job_id': job_id,
                'status': 'ERROR',
                'message': 'Websocket service not available'
            })
