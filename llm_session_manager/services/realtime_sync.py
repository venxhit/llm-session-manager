"""Real-time sync service - Keep web sessions updated with CLI data."""

import threading
import time
from typing import Dict, Optional, Callable
import structlog

from .session_exporter import SessionExporter

logger = structlog.get_logger()


class RealtimeSync:
    """Sync CLI session data to web in real-time."""

    def __init__(self, sync_interval: int = 5):
        """
        Initialize real-time sync.

        Args:
            sync_interval: Seconds between syncs (default: 5)
        """
        self.sync_interval = sync_interval
        self.active_syncs: Dict[str, threading.Thread] = {}
        self.stop_events: Dict[str, threading.Event] = {}
        self.exporter = SessionExporter()

    def start_sync(
        self,
        session_id: str,
        get_session_func: Callable,
        on_update: Optional[Callable] = None
    ):
        """
        Start background sync for a session.

        Args:
            session_id: Session ID to sync
            get_session_func: Function that returns current session data
            on_update: Optional callback when session is updated
        """
        if session_id in self.active_syncs:
            logger.warning("sync_already_active", session_id=session_id)
            return

        # Create stop event
        stop_event = threading.Event()
        self.stop_events[session_id] = stop_event

        # Create and start sync thread
        sync_thread = threading.Thread(
            target=self._sync_loop,
            args=(session_id, get_session_func, stop_event, on_update),
            daemon=True,
            name=f"sync-{session_id}"
        )
        sync_thread.start()
        self.active_syncs[session_id] = sync_thread

        logger.info("sync_started",
                   session_id=session_id,
                   interval=self.sync_interval)

    def _sync_loop(
        self,
        session_id: str,
        get_session_func: Callable,
        stop_event: threading.Event,
        on_update: Optional[Callable]
    ):
        """
        Background sync loop.

        Args:
            session_id: Session ID
            get_session_func: Function to get current session
            stop_event: Event to stop syncing
            on_update: Callback for updates
        """
        logger.info("sync_loop_started", session_id=session_id)

        while not stop_event.is_set():
            try:
                # Get current session data
                session = get_session_func()

                if session:
                    # Sync to web database
                    success = self.exporter.sync_session_update(session)

                    if success:
                        logger.debug("sync_update",
                                    session_id=session_id,
                                    tokens=session.token_count,
                                    health=session.health_score)

                        # Call update callback if provided
                        if on_update:
                            on_update(session)
                    else:
                        logger.warning("sync_update_failed",
                                      session_id=session_id)
                else:
                    logger.warning("session_not_found",
                                  session_id=session_id)
                    # Stop syncing if session no longer exists
                    break

            except Exception as e:
                logger.error("sync_error",
                            session_id=session_id,
                            error=str(e))

            # Wait for next interval or stop event
            stop_event.wait(self.sync_interval)

        logger.info("sync_loop_stopped", session_id=session_id)

    def stop_sync(self, session_id: str):
        """
        Stop syncing a session.

        Args:
            session_id: Session ID to stop
        """
        if session_id not in self.active_syncs:
            logger.warning("sync_not_active", session_id=session_id)
            return

        # Signal stop
        stop_event = self.stop_events.get(session_id)
        if stop_event:
            stop_event.set()

        # Wait for thread to finish (with timeout)
        sync_thread = self.active_syncs.get(session_id)
        if sync_thread:
            sync_thread.join(timeout=2.0)

        # Cleanup
        self.active_syncs.pop(session_id, None)
        self.stop_events.pop(session_id, None)

        logger.info("sync_stopped", session_id=session_id)

    def stop_all(self):
        """Stop all active syncs."""
        logger.info("stopping_all_syncs", count=len(self.active_syncs))

        session_ids = list(self.active_syncs.keys())
        for session_id in session_ids:
            self.stop_sync(session_id)

        logger.info("all_syncs_stopped")

    def is_syncing(self, session_id: str) -> bool:
        """
        Check if a session is currently syncing.

        Args:
            session_id: Session ID

        Returns:
            True if syncing
        """
        return session_id in self.active_syncs

    def get_active_syncs(self):
        """
        Get list of currently syncing session IDs.

        Returns:
            List of session IDs
        """
        return list(self.active_syncs.keys())

    def close(self):
        """Close sync service and cleanup."""
        self.stop_all()
        self.exporter.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
