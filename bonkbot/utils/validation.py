from typing import Any, Tuple

import attrs


def convert_to_float_vector(value: Tuple[Any, Any]) -> Tuple[float, float]:
    if not isinstance(value, (tuple, list)) or len(value) != 2:
        raise TypeError(f"Position must be a tuple or list of two elements, but got {type(value)}")
    
    try:
        return float(value[0]), float(value[1])
    except (ValueError, TypeError) as e:
        raise TypeError(f"Could not convert position elements to float: {value}.\n{e}")


def validate_vector_range(min_value: float, max_value: float) -> None:
    def validate_vector_range(instance: Any, attribute: attrs.Attribute, value: Tuple[float, float]) -> None:
        if len(value) != 2:
            raise ValueError(f"'{attribute.name}' must be a tuple of length 2, but got {value}")
        
        x, y = value
        if not min_value <= x <= max_value:
            raise ValueError(f"'{attribute.name}' x-coordinate ({x}) is out of the valid range [{min_value}, {max_value}]")
    
        if not min_value <= y <= max_value:
            raise ValueError(f"'{attribute.name}' y-coordinate ({y}) is out of the valid range [{min_value}, {max_value}]")
    
    return validate_vector_range
