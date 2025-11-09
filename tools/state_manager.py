"""
PLHub State Management System
Provides reactive state management with computed values, watchers, and persistence

Features:
- Reactive state with automatic UI updates
- Computed values (derived state)
- Watchers (side effects)
- Global store (Redux-like)
- Local component state
- State persistence (localStorage, sessionStorage, file)
- Time-travel debugging
- State snapshots and restoration
- Middleware support
- Action history
"""

import json
import pickle
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import threading
import copy


class StateChangeType(Enum):
    """Types of state changes"""
    SET = "set"
    UPDATE = "update"
    DELETE = "delete"
    RESET = "reset"


@dataclass
class StateChange:
    """Represents a state change event"""
    path: str
    change_type: StateChangeType
    old_value: Any
    new_value: Any
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    
    def to_dict(self) -> Dict:
        return {
            'path': self.path,
            'type': self.change_type.value,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'timestamp': self.timestamp
        }


class StateListener:
    """Listener for state changes"""
    
    def __init__(self, callback: Callable, path: Optional[str] = None, 
                 immediate: bool = False):
        self.callback = callback
        self.path = path  # None means listen to all changes
        self.immediate = immediate
        self.active = True
    
    def matches(self, change_path: str) -> bool:
        """Check if this listener should be notified for the given path"""
        if not self.active:
            return False
        if self.path is None:
            return True
        return change_path.startswith(self.path)
    
    def notify(self, change: StateChange):
        """Notify listener of state change"""
        if self.active:
            try:
                self.callback(change)
            except Exception as e:
                print(f"State listener error: {e}")


class ComputedValue:
    """Computed/derived state value"""
    
    def __init__(self, compute_fn: Callable, dependencies: List[str]):
        self.compute_fn = compute_fn
        self.dependencies = dependencies
        self._cached_value = None
        self._is_dirty = True
    
    def get_value(self, state_getter: Callable) -> Any:
        """Get computed value, using cache if not dirty"""
        if self._is_dirty:
            self._cached_value = self.compute_fn(state_getter)
            self._is_dirty = False
        return self._cached_value
    
    def invalidate(self):
        """Mark as dirty, requiring recomputation"""
        self._is_dirty = True
    
    def depends_on(self, path: str) -> bool:
        """Check if this computed value depends on the given path"""
        return any(path.startswith(dep) for dep in self.dependencies)


class StateStore:
    """Core state store with reactivity"""
    
    def __init__(self, initial_state: Optional[Dict] = None):
        self._state: Dict = initial_state or {}
        self._listeners: List[StateListener] = []
        self._computed: Dict[str, ComputedValue] = {}
        self._history: List[StateChange] = []
        self._max_history = 100
        self._lock = threading.RLock()
        self._middleware: List[Callable] = []
    
    def get(self, path: str, default: Any = None) -> Any:
        """Get value from state by path (e.g., 'user.profile.name')"""
        with self._lock:
            # Check if it's a computed value
            if path in self._computed:
                return self._computed[path].get_value(lambda p: self.get(p))
            
            # Navigate path
            keys = path.split('.')
            value = self._state
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            
            return value
    
    def set(self, path: str, value: Any, notify: bool = True):
        """Set value in state by path"""
        with self._lock:
            old_value = self.get(path)
            
            # Apply middleware
            for middleware in self._middleware:
                value = middleware(path, old_value, value)
            
            # Update state
            keys = path.split('.')
            state = self._state
            
            for key in keys[:-1]:
                if key not in state:
                    state[key] = {}
                state = state[key]
            
            state[keys[-1]] = value
            
            # Record change
            change = StateChange(
                path=path,
                change_type=StateChangeType.SET,
                old_value=old_value,
                new_value=value
            )
            
            self._add_to_history(change)
            
            # Invalidate computed values that depend on this path
            for computed in self._computed.values():
                if computed.depends_on(path):
                    computed.invalidate()
            
            # Notify listeners
            if notify:
                self._notify_listeners(change)
    
    def update(self, path: str, updater: Callable[[Any], Any]):
        """Update value using an updater function"""
        current = self.get(path)
        new_value = updater(current)
        self.set(path, new_value)
    
    def delete(self, path: str):
        """Delete value from state"""
        with self._lock:
            old_value = self.get(path)
            
            keys = path.split('.')
            state = self._state
            
            for key in keys[:-1]:
                if key in state:
                    state = state[key]
                else:
                    return
            
            if keys[-1] in state:
                del state[keys[-1]]
            
            change = StateChange(
                path=path,
                change_type=StateChangeType.DELETE,
                old_value=old_value,
                new_value=None
            )
            
            self._add_to_history(change)
            self._notify_listeners(change)
    
    def reset(self, initial_state: Optional[Dict] = None):
        """Reset state to initial or empty"""
        with self._lock:
            old_state = copy.deepcopy(self._state)
            self._state = initial_state or {}
            
            change = StateChange(
                path="",
                change_type=StateChangeType.RESET,
                old_value=old_state,
                new_value=self._state
            )
            
            self._add_to_history(change)
            
            # Invalidate all computed values
            for computed in self._computed.values():
                computed.invalidate()
            
            self._notify_listeners(change)
    
    def get_all(self) -> Dict:
        """Get entire state"""
        with self._lock:
            return copy.deepcopy(self._state)
    
    def watch(self, path: Optional[str], callback: Callable, 
             immediate: bool = False) -> StateListener:
        """Watch for changes to a specific path or all state"""
        listener = StateListener(callback, path, immediate)
        self._listeners.append(listener)
        
        # Call immediately if requested
        if immediate:
            change = StateChange(
                path=path or "",
                change_type=StateChangeType.SET,
                old_value=None,
                new_value=self.get(path) if path else self._state
            )
            listener.notify(change)
        
        return listener
    
    def unwatch(self, listener: StateListener):
        """Remove a listener"""
        listener.active = False
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def computed(self, path: str, compute_fn: Callable, 
                dependencies: List[str]) -> ComputedValue:
        """Register a computed value"""
        computed = ComputedValue(compute_fn, dependencies)
        self._computed[path] = computed
        return computed
    
    def use_middleware(self, middleware: Callable):
        """Add middleware to intercept state changes"""
        self._middleware.append(middleware)
    
    def _notify_listeners(self, change: StateChange):
        """Notify all matching listeners"""
        for listener in self._listeners[:]:  # Copy to avoid modification during iteration
            if listener.matches(change.path):
                listener.notify(change)
    
    def _add_to_history(self, change: StateChange):
        """Add change to history"""
        self._history.append(change)
        if len(self._history) > self._max_history:
            self._history.pop(0)
    
    def get_history(self, limit: Optional[int] = None) -> List[StateChange]:
        """Get state change history"""
        with self._lock:
            if limit:
                return self._history[-limit:]
            return self._history.copy()
    
    def clear_history(self):
        """Clear state change history"""
        with self._lock:
            self._history.clear()
    
    def snapshot(self) -> Dict:
        """Create a snapshot of current state"""
        with self._lock:
            return {
                'state': copy.deepcopy(self._state),
                'timestamp': datetime.now().isoformat(),
                'history_length': len(self._history)
            }
    
    def restore(self, snapshot: Dict):
        """Restore state from snapshot"""
        with self._lock:
            self._state = copy.deepcopy(snapshot['state'])
            
            # Invalidate all computed values
            for computed in self._computed.values():
                computed.invalidate()
            
            # Notify listeners of full state change
            change = StateChange(
                path="",
                change_type=StateChangeType.RESET,
                old_value=None,
                new_value=self._state
            )
            self._notify_listeners(change)


class PersistenceAdapter:
    """Base class for state persistence"""
    
    def save(self, state: Dict) -> bool:
        raise NotImplementedError
    
    def load(self) -> Optional[Dict]:
        raise NotImplementedError
    
    def clear(self) -> bool:
        raise NotImplementedError


class FilePersistence(PersistenceAdapter):
    """File-based persistence"""
    
    def __init__(self, file_path: Path, format: str = "json"):
        self.file_path = file_path
        self.format = format
    
    def save(self, state: Dict) -> bool:
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            
            if self.format == "json":
                self.file_path.write_text(json.dumps(state, indent=2))
            elif self.format == "pickle":
                with open(self.file_path, 'wb') as f:
                    pickle.dump(state, f)
            else:
                raise ValueError(f"Unknown format: {self.format}")
            
            return True
        except Exception as e:
            print(f"Failed to save state: {e}")
            return False
    
    def load(self) -> Optional[Dict]:
        try:
            if not self.file_path.exists():
                return None
            
            if self.format == "json":
                return json.loads(self.file_path.read_text())
            elif self.format == "pickle":
                with open(self.file_path, 'rb') as f:
                    return pickle.load(f)
            else:
                raise ValueError(f"Unknown format: {self.format}")
        except Exception as e:
            print(f"Failed to load state: {e}")
            return None
    
    def clear(self) -> bool:
        try:
            if self.file_path.exists():
                self.file_path.unlink()
            return True
        except Exception as e:
            print(f"Failed to clear state: {e}")
            return False


class MemoryPersistence(PersistenceAdapter):
    """In-memory persistence (for testing)"""
    
    def __init__(self):
        self._storage: Optional[Dict] = None
    
    def save(self, state: Dict) -> bool:
        self._storage = copy.deepcopy(state)
        return True
    
    def load(self) -> Optional[Dict]:
        if self._storage:
            return copy.deepcopy(self._storage)
        return None
    
    def clear(self) -> bool:
        self._storage = None
        return True


class PersistedStore(StateStore):
    """State store with automatic persistence"""
    
    def __init__(self, persistence: PersistenceAdapter, 
                 initial_state: Optional[Dict] = None,
                 auto_save: bool = True,
                 save_debounce_ms: int = 1000):
        # Load persisted state
        persisted = persistence.load()
        if persisted and not initial_state:
            initial_state = persisted
        
        super().__init__(initial_state)
        
        self.persistence = persistence
        self.auto_save = auto_save
        self.save_debounce_ms = save_debounce_ms
        self._save_timer: Optional[threading.Timer] = None
        
        # Watch for changes and auto-save
        if auto_save:
            self.watch(None, lambda change: self._schedule_save())
    
    def _schedule_save(self):
        """Schedule a save with debouncing"""
        if self._save_timer:
            self._save_timer.cancel()
        
        self._save_timer = threading.Timer(
            self.save_debounce_ms / 1000.0,
            self._do_save
        )
        self._save_timer.start()
    
    def _do_save(self):
        """Actually save to persistence"""
        self.persistence.save(self._state)
    
    def save_now(self):
        """Force immediate save"""
        if self._save_timer:
            self._save_timer.cancel()
        self._do_save()
    
    def clear_persisted(self):
        """Clear persisted data"""
        self.persistence.clear()


class GlobalStore:
    """Singleton global state store"""
    
    _instance: Optional[StateStore] = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls, initial_state: Optional[Dict] = None) -> StateStore:
        """Get or create global store instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = StateStore(initial_state)
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """Reset global store (mainly for testing)"""
        with cls._lock:
            cls._instance = None


class StateManager:
    """High-level state management API"""
    
    def __init__(self, app_name: str, data_dir: Optional[Path] = None):
        self.app_name = app_name
        self.data_dir = data_dir or Path.home() / ".plhub" / "state"
        self.stores: Dict[str, StateStore] = {}
        
        # Create global store
        self.global_store = GlobalStore.get_instance()
    
    def create_store(self, name: str, initial_state: Optional[Dict] = None,
                    persist: bool = False, persist_format: str = "json") -> StateStore:
        """Create a named state store"""
        if persist:
            file_path = self.data_dir / self.app_name / f"{name}.{persist_format}"
            persistence = FilePersistence(file_path, persist_format)
            store = PersistedStore(persistence, initial_state)
        else:
            store = StateStore(initial_state)
        
        self.stores[name] = store
        return store
    
    def get_store(self, name: str) -> Optional[StateStore]:
        """Get a named store"""
        return self.stores.get(name)
    
    def get_global(self) -> StateStore:
        """Get global store"""
        return self.global_store
    
    def create_computed(self, store: StateStore, path: str, 
                       compute_fn: Callable, dependencies: List[str]):
        """Create a computed value in a store"""
        return store.computed(path, compute_fn, dependencies)
    
    def create_watcher(self, store: StateStore, path: str, 
                      callback: Callable, immediate: bool = False) -> StateListener:
        """Create a watcher for a store"""
        return store.watch(path, callback, immediate)
    
    def export_state(self, store_name: Optional[str] = None) -> Dict:
        """Export state from store(s)"""
        if store_name:
            store = self.stores.get(store_name)
            if store:
                return {store_name: store.get_all()}
        
        # Export all stores
        return {
            name: store.get_all()
            for name, store in self.stores.items()
        }
    
    def import_state(self, state_data: Dict):
        """Import state into stores"""
        for name, data in state_data.items():
            if name in self.stores:
                self.stores[name].reset(data)


# Middleware examples

def logging_middleware(path: str, old_value: Any, new_value: Any) -> Any:
    """Log all state changes"""
    print(f"State change: {path}")
    print(f"  Old: {old_value}")
    print(f"  New: {new_value}")
    return new_value


def validation_middleware(validators: Dict[str, Callable]) -> Callable:
    """Create validation middleware"""
    def middleware(path: str, old_value: Any, new_value: Any) -> Any:
        if path in validators:
            validator = validators[path]
            if not validator(new_value):
                raise ValueError(f"Validation failed for {path}: {new_value}")
        return new_value
    return middleware


def immutability_middleware(path: str, old_value: Any, new_value: Any) -> Any:
    """Ensure immutability by deep copying values"""
    if isinstance(new_value, (dict, list)):
        return copy.deepcopy(new_value)
    return new_value


# Helper functions

def create_action(store: StateStore, name: str, handler: Callable):
    """Create a named action that modifies state"""
    def action(*args, **kwargs):
        with store._lock:
            handler(store, *args, **kwargs)
    action.__name__ = name
    return action


def bind_to_ui(store: StateStore, path: str, ui_updater: Callable):
    """Bind state path to UI updater"""
    def on_change(change: StateChange):
        if change.path == path:
            ui_updater(change.new_value)
    
    return store.watch(path, on_change, immediate=True)


# Example usage patterns

def example_basic_usage():
    """Example: Basic state management"""
    store = StateStore({'count': 0, 'user': {'name': 'Alice'}})
    
    # Get values
    count = store.get('count')  # 0
    name = store.get('user.name')  # 'Alice'
    
    # Set values
    store.set('count', 1)
    store.set('user.name', 'Bob')
    
    # Update with function
    store.update('count', lambda x: x + 1)
    
    # Watch for changes
    def on_count_change(change: StateChange):
        print(f"Count changed to: {change.new_value}")
    
    listener = store.watch('count', on_count_change)


def example_computed_values():
    """Example: Computed values"""
    store = StateStore({'firstName': 'John', 'lastName': 'Doe'})
    
    # Create computed value
    def compute_full_name(getter):
        first = getter('firstName')
        last = getter('lastName')
        return f"{first} {last}"
    
    store.computed('fullName', compute_full_name, ['firstName', 'lastName'])
    
    # Access computed value
    full_name = store.get('fullName')  # 'John Doe'
    
    # Changes to dependencies auto-update computed
    store.set('firstName', 'Jane')
    full_name = store.get('fullName')  # 'Jane Doe'


def example_persistence():
    """Example: Persisted state"""
    persistence = FilePersistence(Path('app_state.json'))
    store = PersistedStore(persistence, {'theme': 'dark'})
    
    # Changes automatically saved
    store.set('theme', 'light')
    
    # Force immediate save
    store.save_now()
    
    # Clear persisted data
    store.clear_persisted()


def example_time_travel():
    """Example: Time-travel debugging"""
    store = StateStore({'value': 0})
    
    store.set('value', 1)
    store.set('value', 2)
    store.set('value', 3)
    
    # View history
    history = store.get_history()
    for change in history:
        print(f"{change.path}: {change.old_value} -> {change.new_value}")
    
    # Create snapshot
    snapshot = store.snapshot()
    
    # Make more changes
    store.set('value', 4)
    store.set('value', 5)
    
    # Restore to snapshot
    store.restore(snapshot)
    print(store.get('value'))  # 3
