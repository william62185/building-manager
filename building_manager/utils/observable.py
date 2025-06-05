from typing import Any, Callable, Dict, List
from dataclasses import dataclass, field

@dataclass
class Observable:
    """
    Clase base para implementar el patrón Observer y manejar el estado global.
    Permite a los componentes suscribirse a cambios en el estado.
    """
    _state: Dict[str, Any] = field(default_factory=dict)
    _observers: List[Callable] = field(default_factory=list)

    def add_observer(self, observer: Callable[[Dict[str, Any]], None]) -> None:
        """Agrega un observador que será notificado cuando el estado cambie."""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: Callable) -> None:
        """Elimina un observador de la lista."""
        if observer in self._observers:
            self._observers.remove(observer)

    def set_state(self, key: str, value: Any) -> None:
        """
        Actualiza el estado y notifica a todos los observadores.
        Args:
            key: La clave del estado a actualizar
            value: El nuevo valor
        """
        self._state[key] = value
        self.notify_observers()

    def get_state(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor del estado.
        Args:
            key: La clave del estado a obtener
            default: Valor por defecto si la clave no existe
        """
        return self._state.get(key, default)

    def notify_observers(self) -> None:
        """Notifica a todos los observadores del cambio en el estado."""
        for observer in self._observers:
            observer(self._state)

    def clear_state(self) -> None:
        """Limpia todo el estado."""
        self._state.clear()
        self.notify_observers() 