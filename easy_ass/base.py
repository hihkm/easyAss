class AssAttr:
    _range: tuple = ...
    _attr_type: type = ...
    _default = None

    def __new__(cls, value):
        if cls._attr_type is not ...:
            value = cls._attr_type(value)
        if cls._attr_type == str:
            value = value.lower()
            for cmp_value in vars(cls).values():  # 忽略大小写比较字符串
                if isinstance(cmp_value, str) and cmp_value.lower() == value:
                    return cmp_value

        if value in vars(cls).values():
            return value
        if cls._range is not ... and \
                (cls._range[0] is ... or cls._range[0] <= value) and \
                (cls._range[1] is ... or cls._range[1] >= value):

            return value

        if cls._default is not None:
            return cls._default
        raise KeyError('Could not parse `{}` as {}'.format(value, cls.__name__))
