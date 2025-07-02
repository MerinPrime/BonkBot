from typing import Any, Callable, Iterable, Optional, Tuple

import attrs


def convert_to_float_vector(value: Tuple[Any, Any]) -> Tuple[float, float]:
    if not isinstance(value, (tuple, list)) or len(value) != 2:
        raise TypeError(f'Position must be a tuple or list of two elements, but got {type(value)}')
    
    try:
        return float(value[0]), float(value[1])
    except (ValueError, TypeError) as e:
        raise TypeError(f'Could not convert position elements to float: {value}.\nErr: {e}') from e


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

def validate_int(min_value: Optional[int] = None,
                 max_value: Optional[int] = None) -> Callable[[Any, attrs.Attribute, Any], None]:
    validators = []
    if min_value is not None:
        validators.append(attrs.validators.ge(min_value))
    if max_value is not None:
        validators.append(attrs.validators.le(max_value))
    return attrs.validators.and_(attrs.validators.instance_of(int), *validators)

def validate_float(min_value: Optional[float] = None,
                   max_value: Optional[float] = None) -> Callable[[Any, attrs.Attribute, Any], None]:
    validators = []
    if min_value is not None:
        validators.append(attrs.validators.ge(min_value))
    if max_value is not None:
        validators.append(attrs.validators.le(max_value))
    return attrs.validators.and_(
        attrs.validators.or_(
            attrs.validators.instance_of(int),
            attrs.validators.instance_of(float),
        ),
        *validators,
    )

def validate_bool() -> Callable[[Any, attrs.Attribute, Any], None]:
    return attrs.validators.instance_of(bool)

def validate_str(max_len: Optional[int] = None, min_len: Optional[int] = None) -> Callable[[Any, attrs.Attribute, Any], None]:
    validators = []
    if max_len is not None:
        validators.append(attrs.validators.max_len(max_len))
    if min_len is not None:
        validators.append(attrs.validators.min_len(min_len))
    return attrs.validators.and_(
        attrs.validators.instance_of(str),
        *validators,
    )

def validate_opt_str(max_len: Optional[int] = None) -> Callable[[Any, attrs.Attribute, Any], None]:
    validators = []
    if max_len is not None:
        validators.append(attrs.validators.max_len(max_len))
    return attrs.validators.optional(attrs.validators.and_(
        attrs.validators.instance_of(str),
        *validators,
    ))

def validate_opt_bool() -> Callable[[Any, attrs.Attribute, Any], None]:
    return attrs.validators.optional(attrs.validators.instance_of(bool))

def validate_opt_float(min_value: Optional[float] = None,
                       max_value: Optional[float] = None) -> Callable[[Any, attrs.Attribute, Any], None]:
    validators = [
        attrs.validators.instance_of(float),
    ]
    if min_value is not None:
        validators.append(attrs.validators.ge(min_value))
    if max_value is not None:
        validators.append(attrs.validators.le(max_value))
    return attrs.validators.optional(attrs.validators.and_(*validators))

def validate_opt_int(min_value: Optional[int] = None,
                     max_value: Optional[int] = None) -> Callable[[Any, attrs.Attribute, Any], None]:
    validators = [
        attrs.validators.instance_of(int),
    ]
    if min_value is not None:
        validators.append(attrs.validators.ge(min_value))
    if max_value is not None:
        validators.append(attrs.validators.le(max_value))
    return attrs.validators.optional(attrs.validators.and_(*validators))

def validate_int_opts(options: Iterable[int]) -> Callable[[Any, attrs.Attribute, Any], None]:
    return attrs.validators.and_(
        attrs.validators.instance_of(int),
        attrs.validators.in_(options),
    )

def validate_type_list(cls_type: type, max_len: Optional[int] = None) -> Callable[[Any, attrs.Attribute, Any], None]:
    validators = []
    if max_len is not None:
        validators.append(attrs.validators.max_len(max_len))
    return attrs.validators.deep_iterable(
        attrs.validators.instance_of(cls_type),
        attrs.validators.and_(
            attrs.validators.instance_of(list),
            *validators,
        ),
    )

def validate_contributors() -> Callable[[Any, attrs.Attribute, Any], None]:
    return attrs.validators.deep_iterable(
        validate_str(15),
        attrs.validators.instance_of(list),
    )

def validate_type(cls_type: type) -> Callable[[Any, attrs.Attribute, Any], None]:
    return attrs.validators.instance_of(cls_type)
