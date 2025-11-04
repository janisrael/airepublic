"""
Training Websocket Service
Handles real-time progress updates during training jobs
Websockets are only active during training, automatically turn off when completed/error
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
import threading
import time
import queue
from typing import Dict, Any, Optional

class TrainingWebsocketService:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.active_training_jobs: Dict[int, Dict[str, Any]] = {}
        self.lock = threading.Lock()
        self.message_queue = queue.Queue()
        self.worker_thread = None
        self.shutdown_flag = threading.Event()
        self.websockets_enabled = False  # Disable by default
        self._start_worker()
    
    def _start_worker(self):
        """Start the background worker thread for processing websocket messages"""
        if self.worker_thread is None or not self.worker_thread.is_alive():
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            print("🔧 Websocket worker thread started")
    
    def _worker_loop(self):
        """Background worker that processes websocket messages from the queue"""
        while not self.shutdown_flag.is_set():
            try:
                # Get message from queue with timeout
                message = self.message_queue.get(timeout=1.0)
                
                if message['type'] == 'progress':
                    self._emit_progress_safe(message['data'])
                elif message['type'] == 'completion':
                    self._emit_completion_safe(message['data'])
                
                self.message_queue.task_done()
                
            except queue.Empty:
                continue  # Timeout, check shutdown flag
            except Exception as e:
                print(f"⚠️ Worker thread error: {e}")
    
    def _emit_progress_safe(self, data):
        """Safely emit progress update - only if websockets are enabled"""
        if not self.websockets_enabled:
            print(f"📡 Websockets disabled - skipping progress emit for job {data['job_id']}")
            return
        try:
            self.socketio.emit('training_progress', data, room=f'training_job_{data["job_id"]}')
        except Exception as e:
            print(f"⚠️ Progress emit failed: {e}")
    
    def _emit_completion_safe(self, data):
        """Safely emit completion update - only if websockets are enabled"""
        if not self.websockets_enabled:
            print(f"📡 Websockets disabled - skipping completion emit for job {data['job_id']}")
            return
        try:
            self.socketio.emit('training_completed', data, room=f'training_job_{data["job_id"]}')
        except Exception as e:
            print(f"⚠️ Completion emit failed: {e}")
    
    def start_training_session(self, job_id: int, user_id: int, minion_id: int) -> None:
        """Start websocket session for a training job"""
        try:
            with self.lock:
                self.active_training_jobs[job_id] = {
                    'user_id': user_id,
                    'minion_id': minion_id,
                    'started_at': time.time(),
                    'current_step': 0,
                    'total_steps': 9,
                    'status': 'RUNNING'
                }
            
            print(f"🔌 Websocket session started for job {job_id}")
        except Exception as e:
            print(f"⚠️ Failed to start websocket session: {e}")
    
    def update_training_progress(self, job_id: int, step: int, step_name: str, 
                               progress_percent: float, message: str = "") -> None:
        """Queue progress update for background processing"""
        if job_id not in self.active_training_jobs:
            return
        
        try:
            with self.lock:
                self.active_training_jobs[job_id]['current_step'] = step
                self.active_training_jobs[job_id]['status'] = 'RUNNING'
            
            # Queue message for background processing
            self.message_queue.put({
                'type': 'progress',
                'data': {
                    'job_id': job_id,
                    'step': step,
                    'step_name': step_name,
                    'progress_percent': progress_percent,
                    'message': message,
                    'status': 'RUNNING'
                }
            })
        except Exception as e:
            print(f"⚠️ Failed to queue progress update: {e}")
        
        print(f"📡 Progress update queued: Job {job_id}, Step {step} ({step_name}), Progress: {progress_percent}%")
    
    def complete_training(self, job_id: int, success: bool, xp_gained: int = 0, 
                         error_message: str = "") -> None:
        """Queue completion update for background processing"""
        if job_id not in self.active_training_jobs:
            return
        
        try:
            with self.lock:
                self.active_training_jobs[job_id]['status'] = 'COMPLETED' if success else 'FAILED'
            
            # Queue completion message for background processing
            self.message_queue.put({
                'type': 'completion',
                'data': {
                    'job_id': job_id,
                    'success': success,
                    'xp_gained': xp_gained,
                    'error_message': error_message,
                    'status': 'COMPLETED' if success else 'FAILED',
                    'progress_percent': 100.0 if success else 0.0
                }
            })
            
            # Schedule cleanup after delay
            threading.Timer(5.0, self._cleanup_session, args=[job_id]).start()
            
        except Exception as e:
            print(f"⚠️ Failed to queue completion update: {e}")
        
        print(f"✅ Training completion queued: Job {job_id}, Success: {success}, XP: {xp_gained}")
    
    def _cleanup_session(self, job_id: int) -> None:
        """Clean up websocket session after training completes"""
        with self.lock:
            if job_id in self.active_training_jobs:
                del self.active_training_jobs[job_id]
        
        print(f"🧹 Websocket session cleaned up for job {job_id}")
    
    def is_training_active(self, job_id: int) -> bool:
        """Check if training session is active"""
        with self.lock:
            return job_id in self.active_training_jobs
    
    def get_active_jobs(self) -> Dict[int, Dict[str, Any]]:
        """Get all active training jobs"""
        with self.lock:
            return self.active_training_jobs.copy()
    
    def shutdown(self):
        """Shutdown the websocket service and worker thread"""
        self.shutdown_flag.set()
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2.0)
        print("🔧 Websocket service shutdown complete")
    
    def enable_websockets(self):
        """Enable websocket functionality"""
        self.websockets_enabled = True
        print("🔌 Websockets enabled")
    
    def disable_websockets(self):
        """Disable websocket functionality"""
        self.websockets_enabled = False
        print("🔌 Websockets disabled")

# Global instance (will be initialized in app)
training_websocket_service: Optional[TrainingWebsocketService] = None

def init_training_websocket_service(socketio: SocketIO) -> TrainingWebsocketService:
    """Initialize the global training websocket service"""
    global training_websocket_service
    training_websocket_service = TrainingWebsocketService(socketio)
    return training_websocket_service

def get_training_websocket_service() -> Optional[TrainingWebsocketService]:
    """Get the global training websocket service"""
    return training_websocket_service
