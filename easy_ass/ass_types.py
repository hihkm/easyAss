import re


class AssColor:
    def __init__(self, value: int | str):
        """
        ASS 颜色类型

        参数：
            value: 颜色值
                - 当传入整数时，直接存储作为颜色值
                - 当传入字符串时，按照 AGBR 的顺序进行解析
        用法：
            dm_color = AssColor("&H66CCFF")  # 定义一个颜色，并将 66CCFF 作为值
            print(int(dm_color))  # 打印其整数值
            print(dm_color)  # 打印其十六进制值
            print(AssColor(17900) == AssColor("&H66CCFF"))  # 比较两个颜色值是否相同
        """
        if isinstance(value, int):
            self.__color_value = value
        elif isinstance(value, str):
            self.parse(value)
        else:
            raise Exception('Unsupported AssColor value type `{}`. '.format(type(value)))

    def parse(self, raw_str: str) -> None:
        """
        通过字符串改变当前颜色对象的颜色值

        参数：
            raw_str: 字符颜色值
        """
        try:
            raw_str = raw_str.strip('&Hh')
            self.__color_value = int(raw_str, base=16)
        except Exception as e:
            raise TypeError('Could not parse `{}` as ass color. {}'.
                            format(raw_str, e))

    def dump(self) -> str:
        """
        将颜色转为十六进制字符串

        返回值：
            字符串颜色值
        """
        alpha: int = (self.__color_value & 0xFF000000) >> 24
        color: int = (self.__color_value & 0x00FFFFFF)

        ret_str: str = '&H'
        if alpha != 0:  # 若透明度为 0 则不显示透明度的 0
            ret_str += '{:0>2X}'.format(alpha)
        ret_str += '{:0>6X}'.format(color)
        return ret_str

    def __eq__(self, other) -> bool:
        """
        判断两个颜色对象值是否相等

        返回值：
            颜色是否相同
        """
        if not isinstance(other, AssColor):
            raise Exception('Could not compare with `AssColor` and `{}`'.format(type(other)))
        return other.__color_value == self.__color_value

    def __str__(self) -> str:
        """
        将颜色转为十六进制字符串
        返回值：
            字符串颜色值
        """
        return self.dump()

    def __int__(self) -> int:
        """
        将颜色转为整形

        返回值：
            整数颜色值
        """
        return self.__color_value


class AssTime:
    _match_time = re.compile(r'(?P<h>\d+):(?P<m>\d+):(?P<s>\d+).(?P<ms>\d+)')

    def __init__(self, value: int | float | str):
        self.__time_value = 0
        if isinstance(value, str):
            self.parse(value)
        else:
            self.__time_value = value

    def parse(self, value: str):
        match = self._match_time.match(value)
        if match is None:
            raise Exception(f'Could not parse `{value}` as ass time. ')
        time_path = match.groupdict()
        self.__time_value =                 \
            int(time_path['h']) * 3600 +    \
            int(time_path['m']) * 60 +      \
            int(time_path['s']) +           \
            int(time_path['ms']) / 1000

    def dump(self):
        hour = int(self.__time_value // 3600)
        minute = int(self.__time_value // 60 % 60)
        second = int(self.__time_value % 60)
        milli_second = int(self.__time_value * 1000 % 1000)

        return f'{hour:0>2d}:{minute:0>2d}:{second:0>2d}.{milli_second:0>2d}'

    def __str__(self):
        return self.dump()

    def __float__(self):
        return self.__time_value
