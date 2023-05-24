from errors import Errors
from base import AssAttr
from ass_types import AssColor


class Styles(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style_format: StyleFormat = StyleFormat()

    def parse(self, ass_str: str) -> Errors:
        err = Errors()
        ass_line = ass_str.split(':', 1)
        if len(ass_line) != 2:
            return err.error(f'Fail to parse `{ass_str}` as Styles. ')
        title = ass_line[0].strip()
        if title == FORMAT_LINE_TITLE:
            self.style_format = StyleFormat()
            err += self.style_format.parse(ass_str)
        elif title == STYLE_LINE_TITLE:
            if self.style_format is ...:
                return err.error(f'`Format` line is missing. ')
            style_item = StyleItem()
            style_item.parse(ass_str, self.style_format)
            self.append(style_item)
        return err

    def dump(self) -> (list[str], Errors):
        errors = Errors()
        dump_lines: list[str] = ['[{}]'.format(STYLES_PART_TITLE)]

        format_lines, format_errors = self.style_format.dump()
        dump_lines += format_lines
        errors += format_errors
        for item in self:
            item_line, item_error = item.dump(self.style_format)
            dump_lines += item_line
            errors += item_error
        return dump_lines, errors


class StyleFormat:
    def __init__(self):
        self.style_attrs: list[str] = []

    def parse(self, ass_str: str) -> Errors:
        err = Errors()
        ass_line = ass_str.split(':', 1)
        if len(ass_line) != 2 or ass_line[0].strip() != FORMAT_LINE_TITLE:
            return err.error(f'Fail to parse `{ass_str}` as style format. ')
        style_attrs = ass_line[1].split(',')
        for style_attr in style_attrs:
            style_attr = style_attr.strip()
            if style_attr not in STYLE_ATTR_DEF:
                return err.error(f'Unknown style attribute `{style_attr}`. ')
            self.style_attrs.append(style_attr)
        return err

    def dump(self) -> (list[str], Errors):
        format_line = FORMAT_LINE_TITLE + ':' + ','.join(self.style_attrs)
        return [format_line], Errors()


class StyleItem:
    def __init__(self, **kwargs):
        self.style_attrs = {attr_name: None for attr_name in STYLE_ATTR_DEF.keys()}
        for key, value in kwargs.items():  # 支持构造时传初始值
            if key in self.style_attrs:
                self.style_attrs[key] = value

    def parse(self, ass_str: str, style_format: StyleFormat) -> Errors:
        err = Errors()
        ass_line = ass_str.split(':', 1)
        if len(ass_line) != 2 or ass_line[0].strip() != STYLE_LINE_TITLE:
            return err.error(f'Fail to parse `{ass_str}` as style values. ')
        style_values = ass_line[1].split(',')
        if len(style_values) != len(style_format.style_attrs):
            return err.error(f'`Styles` line does not match `Format` line! ')
        for index, style_attr in enumerate(style_format.style_attrs):
            try:
                self.style_attrs[style_attr] = \
                    STYLE_ATTR_DEF[style_attr](style_values[index])
            except Exception as exception:
                err.error(f'Could not parse `{style_values[index]}` '
                          f'as `{style_attr}`. Exception: {exception}. ')
        return err

    def dump(self, style_format: StyleFormat) -> (list[str], Errors):
        err = Errors()
        style_values = []
        for style_attr in style_format.style_attrs:
            if self.style_attrs[style_attr] is None:
                err.error(f'Style `{style_attr}` not specified. ')
            style_values.append(str(self.style_attrs[style_attr]))

        styles_line = STYLE_LINE_TITLE + ':' + ','.join(style_values)
        return [styles_line], err

    def __getattr__(self, attribute):
        if attribute in self.style_attrs:
            return self.style_attrs[attribute]
        raise AttributeError(attribute)

    def __setattr__(self, key, value):
        style_attrs = self.__dict__.get('style_attrs', {})
        if key in style_attrs:
            style_attrs[key] = STYLE_ATTR_DEF[key](value)
        else:
            super().__setattr__(key, value)


class Bold(AssAttr):
    _attr_type = int
    enable = -1
    disable = 0
    _default = -1


class Italic(AssAttr):
    _attr_type = int
    enable = -1
    disable = 0
    _default = -1


class Underline(AssAttr):
    _attr_type = int
    enable = -1
    disable = 0
    _default = -1


class StrikeOut(AssAttr):
    _attr_type = int
    enable = -1
    disable = 0
    _default = -1


class BorderStyle(AssAttr):
    _attr_type = int
    outlineAndShadow = 1
    opaque = 3
    _default = 1


class Alignment(AssAttr):
    _attr_type = int
    NW = 7
    N = 8
    NE = 9
    W = 4
    CENTER = 5
    E = 6
    SW = 1
    S = 2
    SE = 3
    _default = 5


STYLES_PART_TITLE = 'v4+ Styles'
FORMAT_LINE_TITLE = 'Format'
STYLE_LINE_TITLE = 'Style'
STYLE_ATTR_DEF = {
    'Name': str,  # 样式名称
    'Fontname': str,  # 字体名称
    'Fontsize': int,  # 文字大小
    'PrimaryColour': AssColor,  # 主颜色
    'SecondaryColour': AssColor,  # 次颜色
    'OutlineColour': AssColor,  # 边框颜色
    'BackColour': AssColor,  # 边框颜色
    'Bold': Bold,  # 粗体
    'Italic': Italic,  # 斜体
    'Underline': Underline,  # 下划线
    'StrikeOut': StrikeOut,  # 删除线
    'ScaleX': float,  # 文本宽度
    'ScaleY': float,  # 文本高度
    'Spacing': float,  # 字符之间的间隙
    'Angle': float,  # 文本旋转角度
    'BorderStyle': BorderStyle,  # 边框样式
    'Outline': float,  # 边框宽度
    'Shadow': int,  # 阴影宽度
    'Alignment': Alignment,  # 对齐方式 与小键盘一致
    'MarginL': int,  # 左边距
    'MarginR': int,  # 右边距
    'MarginV': int,  # 垂直边距
    'Encoding': int,  # 编码方式
}

__all__ = (
    'Styles',
    'StyleFormat',
    'StyleItem',
    'Bold',
    'Italic',
    'Underline',
    'StrikeOut',
    'BorderStyle',
    'Alignment',
    'STYLES_PART_TITLE',
    'FORMAT_LINE_TITLE',
    'STYLE_LINE_TITLE',
    'STYLE_ATTR_DEF'
)
