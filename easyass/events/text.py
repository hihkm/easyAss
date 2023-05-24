import sys
import inspect
import re

from ass_types import AssColor


class TextBase:
    _prefix = ''
    _with_bracket = True
    _arg_mapper: dict[str, dict] = ...
    """
    _arg_mapper 字典定义函数参数
    key为参数名称，value为可迭代对象，其第一个元素表示 是否可选，第二个参数定义其 转换函数
    _arg_mapper = {
        'arg_name': (True, int),
        ...
    }
    """

    def __init__(self, *args, **kwargs):
        self._arg_values: dict = {arg_name: None for arg_name in self._arg_mapper} \
            if self._arg_mapper is not ... else {}  # 参数值存储

        if 'raw_str' in kwargs:  # 指定源字符串
            self.parse(kwargs.get('raw_str', ''))
        elif self._arg_mapper is not ...:  # 正常传参
            if len(args) > len(self._arg_mapper):
                raise TypeError('`{}()` takes at most {} arguments. '.
                                format(self.__class__.__name__, len(self._arg_mapper)))
            args = {name: value for name, value in zip(self._arg_mapper, args)}
            args.update(kwargs)
            self._handle_args(args)

    def _handle_args(self, args: dict[str, any]) -> None:
        for arg_name, arg_value in args.items():  # 填充已经填写的参数
            if arg_name not in self._arg_mapper:
                raise TypeError(arg_name)
            if arg_value is None:
                continue
            self._arg_values[arg_name] = \
                self._arg_mapper[arg_name][1](arg_value)

        if self._arg_mapper is ...:
            return
        for arg_name, arg_info in self._arg_mapper.items():  # 查找是否存在未赋值的必填参数
            if self._arg_values.get(arg_name, None) is None and not arg_info[0]:
                raise TypeError('In `{}()`, `{}` must be specified. '.
                                format(self.__class__.__name__, arg_name))

    def parse(self, ass_str: str):
        if self._arg_mapper is ...:
            return
        args_str = ass_str[len(self._prefix):].strip('() ')
        arg_values = args_str.split(',')
        args = {name: value for name, value in zip(self._arg_mapper, arg_values)}
        self._handle_args(args)

    def dump(self):
        arg_values = [str(value)
                      for value in self._arg_values.values()
                      if value is not None]
        args_str = ','.join(arg_values)
        if self._with_bracket:
            return '{}({})'.format(self._prefix, args_str)
        else:
            return '{}{}'.format(self._prefix, args_str)

    def __str__(self):
        return self.dump()

    def __getattr__(self, key):
        if key in self._arg_values:
            return self._arg_values[key]
        raise AttributeError(key)

    def __setattr__(self, key, value):
        if key in self.__dict__.get('_arg_values', {}):
            self.__dict__['_arg_values'][key] = value
            return
        super().__setattr__(key, value)

    def __add__(self, other):
        if not (isinstance(other, TextBase) or isinstance(other, str)):
            raise
        return Text(self, other)

    def __radd__(self, other):
        return TextBase.__add__(other, self)


class Text(TextBase, list):
    __match_code_part = re.compile(r'{[^}]*?}')

    def __init__(self, *args):
        super().__init__()
        for arg in args:
            if isinstance(arg, Text):
                self.extend(arg)
            elif isinstance(arg, TextBase):
                self.append(arg)
            elif isinstance(arg, str):
                self.parse(arg)
            else:
                raise TypeError(arg)

    def parse(self, ass_str: str):
        matches = self.__match_code_part.finditer(ass_str)
        curr_pos = 0
        # 匹配 { } 花括号区域
        for match in matches:
            if match.start() != curr_pos:
                self.append(Str(raw_str=match.string[curr_pos: match.start()]))
            codes = match.string[match.start()+1: match.end()-1].split('\\')  # 切割各组代码
            for code in codes:
                if len(code) == 0:
                    continue
                for code_name, proc_type in _codes_mapper.items():
                    if code.startswith(code_name):
                        tar_type = proc_type
                        break
                else:
                    raise TypeError('Unknown code `{}`'.format(code))
                self.append(tar_type(raw_str=code))
            curr_pos = match.end()
        # 末端字符串
        if curr_pos != len(ass_str):
            self.append(Str(raw_str=ass_str[curr_pos:]))

    def dump(self) -> str:
        ret: str = ''
        for index, item in enumerate(self):
            if isinstance(item, Str):
                if index != 0 and not isinstance(self[index - 1], Str):  # 闭大括号
                    ret += '}'
            else:
                if index == 0 or isinstance(self[index - 1], Str):  # 开大括号
                    ret += '{'
                ret += '\\'
            ret += item.dump()
        return ret

    def __str__(self) -> str:
        return self.dump()


class Str(TextBase, str):
    """
    文本部分

    与 str 类无异
    """
    __escape_mapper = {
        r'\n': r'\{}n',
        r'\h': r'\{}h',
        ' ': r'\h',
        '\n': r'\N',
    }

    def __new__(cls, *args, **kwargs):
        if 'raw_str' in kwargs:  # 对 ass原始字符串进行反转义
            arg = cls.__unescape(kwargs.get('raw_str', ''))
            return super().__new__(cls, arg)
        else:
            return super().__new__(cls, *args, **kwargs)

    @staticmethod
    def __escape(raw_str: str) -> str:
        for from_str, to_str in Str.__escape_mapper.items():
            raw_str = raw_str.replace(from_str, to_str)
        return raw_str

    @staticmethod
    def __unescape(raw_str: str) -> str:
        for to_str, from_str in Str.__escape_mapper.items():
            raw_str = raw_str.replace(from_str, to_str)
        return raw_str

    def dump(self):
        return self.__escape(str.__str__(self))

    def __str__(self):
        return str.__str__(self)


class Bold(TextBase):
    """
    文本加粗

    参数:
     - enable: 0取消加粗 / 1加粗 / 其他表示字重
    """
    _prefix = 'b'
    _with_bracket = False
    _arg_mapper = {
        'enable': (False, int),
    }


class Italic(TextBase):
    """
    文本斜体

    参数:
     - enable: 0取消斜体 / 1启用斜体 / 其他表示字重
    """
    _prefix = 'i'
    _with_bracket = False
    _arg_mapper = {
        'enable': (False, int),
    }


class Underline(TextBase):
    """
    文本斜体

    参数:
     - enable: 0取消斜体 / 1启用斜体
    """
    _prefix = 'u'
    _with_bracket = False
    _arg_mapper = {
        'enable': (False, int),
    }


class Delete(TextBase):
    """
    文本删除线

    参数:
     - enable: 0取消删除线 / 1启用删除线
    """
    _prefix = 's'
    _with_bracket = False
    _arg_mapper = {
        'enable': (False, int),
    }


class Border(TextBase):
    """
    文本外边框

    参数:
     - width: 边框宽度
    """
    _prefix = 'bord'
    _with_bracket = False
    _arg_mapper = {
        'width': (False, float),
    }


class BorderX(Border):
    """
    文本外边框，仅 X 轴

    参数:
     - width: 边框宽度
    """
    _prefix = 'xbord'


class BorderY(Border):
    """
    文本外边框，仅 Y 轴

    参数:
     - width: 边框宽度
    """
    _prefix = 'ybord'


class Shadow(TextBase):
    """
    文本阴影

    参数:
     - depth: 阴影深度
    """
    _prefix = 'shad'
    _with_bracket = False
    _arg_mapper = {
        'depth': (False, float),
    }


class ShadowX(Shadow):
    """
    文本阴影，仅 X 轴

    参数:
     - depth: 阴影深度
    """
    _prefix = 'xshad'


class ShadowY(Shadow):
    """
    文本阴影，仅 Y 轴

    参数:
     - depth: 阴影深度
    """
    _prefix = 'xshad'


class FontName(TextBase):
    """
    文本字体名

    参数:
     - name: 字体名
    """
    _prefix = 'fn'
    _with_bracket = False
    _arg_mapper = {
        'name': (False, str),
    }


class FontSize(TextBase):
    """
    文本大小

    参数:
     - size: 大小，文本行高，单位 px
    """
    _prefix = 'fs'
    _with_bracket = False
    _arg_mapper = {
        'size': (False, int),
    }


class FontSizeInc(FontSize):
    """
    文本大小增大

    参数:
     - size: 增大倍数，文本行高会变成原来的 (1+size/10)，如 size=5 表示文本行高变为原来的 1.5 倍
    """
    _prefix = 'fs+'


class FontSizeDec(FontSize):
    """
    文本大小减小

    参数:
     - size: 减小倍数，文本行高会变成原来的 (1-size/10)，如 size=5 表示文本行高变为原来的 0.5 倍
    """
    _prefix = 'fs-'


class ScaleX(TextBase):
    """
    文本缩放，仅 X 轴

    参数:
     - ratio: 缩放比例
    """
    _prefix = 'fscx'
    _with_bracket = False
    _arg_mapper = {
        'ratio': (False, float),
    }


class ScaleY(TextBase):
    """
    文本缩放，仅 Y 轴

    参数:
     - ratio: 缩放比例
    """
    _prefix = 'fscy'
    _with_bracket = False
    _arg_mapper = {
        'ratio': (False, float),
    }


class Space(TextBase):
    """
    文字间距离

    参数:
     - size: 距离，单位 px
    """
    _prefix = 'fsp'
    _with_bracket = False
    _arg_mapper = {
        'size': (False, int),
    }


class Rotate(TextBase):
    """
    文本旋转，沿 Z 轴

    参数:
     - angle: 旋转角度
    """
    _prefix = 'fr'
    _with_bracket = False
    _arg_mapper = {
        'angle': (False, float),
    }


class RotateZ(Rotate):
    """
    文本旋转，沿 Z 轴

    参数:
     - angle: 旋转角度
    """
    _prefix = 'frz'


class RotateX(Rotate):
    """
    文本旋转，沿 X 轴

    参数:
     - angle: 旋转角度
    """
    _prefix = 'frx'


class RotateY(Rotate):
    """
    文本旋转，沿 Y 轴

    参数:
     - angle: 旋转角度
    """
    _prefix = 'fry'


class AngleX(TextBase):
    """
    文本倾斜，沿 X 轴

    参数:
     - factor: 倾斜因数，-0.5为斜体
    """
    _prefix = 'fax'
    _with_bracket = False
    _arg_mapper = {
        'factor': (False, float),
    }


class AngleY(TextBase):
    """
    文本倾斜，沿 Y 轴

    参数:
     - factor: 倾斜因数
    """
    _prefix = 'fay'
    _with_bracket = False
    _arg_mapper = {
        'factor': (False, float),
    }


class Encoding(TextBase):
    """
    文本字符集

    参数:
     - encoding: 字符集，0 英文 / 1 ANSI / 134 简体中文 / 136 繁体中文
    """
    _prefix = 'fe'
    _with_bracket = False
    _arg_mapper = {
        'encoding': (False, int),
    }


class Color(TextBase):
    """
    文本颜色

    参数:
     - color: 文本颜色值，可选，不填默认使用style中颜色
    """
    _prefix = 'c'
    _with_bracket = False
    _arg_mapper = {
        'color': (True, AssColor),
    }


class PrimaryColor(Color):
    """
    文本颜色，主颜色

    参数:
     - color: 文本颜色值，可选，不填默认使用style中颜色
    """
    _prefix = '1c'


class SecondaryColor(Color):
    """
    文本颜色，次颜色

    参数:
     - color: 文本颜色值，可选，不填默认使用style中颜色
    """
    _prefix = '2c'


class OutlineColor(Color):
    """
    文本颜色，边线颜色

    参数:
     - color: 文本颜色值，可选，不填默认使用style中颜色
    """
    _prefix = '3c'


class BackColor(Color):
    """
    文本颜色，背景颜色

    参数:
     - color: 文本颜色值，可选，不填默认使用style中颜色
    """
    _prefix = '4c'


class Alpha(TextBase):
    """
    文本透明度值，主透明度

    参数:
     - alpha: 文本透明度值
    """
    _prefix = 'alpha'
    _with_bracket = False
    _arg_mapper = {
        'alpha': (True, str),
    }


class PrimaryAlpha(Alpha):
    """
    文本透明度值，主透明度

    参数:
     - alpha: 文本透明度值
    """
    _prefix = '1a'


class SecondaryAlpha(Alpha):
    """
    文本透明度值，次透明度

    参数:
     - alpha: 文本透明度值
    """
    _prefix = '2a'


class OutlineAlpha(Alpha):
    """
    文本透明度值，描边透明度

    参数:
     - alpha: 文本透明度值
    """
    _prefix = '3a'


class BackAlpha(Alpha):
    """
    文本透明度值，背景透明度

    参数:
     - alpha: 文本透明度值
    """
    _prefix = '4a'


class Align(TextBase):
    """
    文本对齐

    参数:
     - alpha: 文本透明度值

    备注:
    与小键盘的布局一致
    7 8 9
    4 5 6
    1 2 3
    """
    _prefix = 'an'
    _with_bracket = False
    _arg_mapper = {
        'side': (False, int),
    }


class AlignEx(Align):
    """
    文本对齐

    参数:
     - alpha: 文本透明度值

    备注:
    与小键盘的布局一致
    9 10 11
    5 6 7
    1 2 3
    """
    _prefix = 'a'


class Wrap(TextBase):
    """
    文本换行方式

    参数:
     - style: 文本换行方式 0 自动但顶部长 / 1 行尾 / 2 不换行 / 3 自动但底部长
    """
    _prefix = 'q'
    _with_bracket = False
    _arg_mapper = {
        'style': (True, int),
    }


class ChangeStyle(TextBase):
    """
    文本换行方式

    参数:
     - name: 要更改的样式名，此代码后面的文本都会换成此样式
    """
    _prefix = 'r'
    _with_bracket = False
    _arg_mapper = {
        'name': (True, str),
    }


class Move(TextBase):
    """
    直线移动

    参数:
     - x1: 开始位置x，单位 px
     - x2: 开始位置y，单位 px
     - y1: 结束位置x，单位 px
     - y2: 结束位置y，单位 px
     - t1: 开始运动时间，单位毫秒，可选
     - t2: 结束运动时间，单位毫秒，可选
    """
    _prefix = 'move'
    _with_bracket = True
    _arg_mapper = {
        'x1': (False, int),
        'x2': (False, int),
        'y1': (False, int),
        'y2': (False, int),
        't1': (True, int),
        't2': (True, int),
    }


class Pos(TextBase):
    """
    固定停留在指定位置

    参数:
     - x: 位置x，单位 px
     - y: 位置y，单位 px
    """
    _prefix = 'pos'
    _with_bracket = True
    _arg_mapper = {
        'x': (False, int),
        'y': (False, int),
    }


class Org(TextBase):
    """
    指定定位点位置

    物体的旋转、移动等位置都是以定位点作为基准

    参数:
     - x: 位置x，单位 px
     - y: 位置y，单位 px
    """
    _prefix = 'org'
    _with_bracket = True
    _arg_mapper = {
        'x': (False, int),
        'y': (False, int),
    }


class Fade(TextBase):
    """
    淡入和淡出

    参数:
     - t1: 淡入时间，单位毫秒
     - t2: 淡出时间，单位毫秒
    """
    _prefix = 'fad'
    _with_bracket = True
    _arg_mapper = {
        't1': (False, int),
        't2': (False, int),
    }


class FadeEx(TextBase):
    """
    更加复杂的淡入和淡出效果

    参数:
     - a1: 时间 t1 之前的透明度
     - a2: 时间 t1 到 t2 透明度由 a1 渐变为 a2
     - a3: 时间 t3 到 t4 透明度由 a2 渐变为 a3
     - t1: 时间节点1，单位毫秒
     - t2: 时间节点2，单位毫秒
     - t3: 时间节点3，单位毫秒
     - t4: 时间节点4，单位毫秒
    """
    _prefix = 'fade'
    _with_bracket = True
    _arg_mapper = {
        'a1': (False, str),
        'a2': (False, str),
        'a3': (False, str),
        't1': (False, int),
        't2': (False, int),
        't3': (False, int),
        't4': (False, int),
    }


class Clip(TextBase):
    """
    淡入和淡出

    参数:
     - t1: 淡入时间，单位毫秒
     - t2: 淡出时间，单位毫秒
    """
    _prefix = 'clip'
    _with_bracket = True
    _arg_mapper = {
        't1': (False, str),
    }


class Draw(TextBase):
    """
    开启绘图模式，并设置绘图等级

    坐标系比例会变为原来的 1/(2^(level-1))，如果level为0表示退出绘图模式

    参数:
     - level: 绘图等级
    """
    _prefix = 'p'
    _with_bracket = False
    _arg_mapper = {
        't1': (False, str),
    }


class DrawBegin(TextBase):
    """
    开启绘图模式，相当于 Draw(1)

    后面的文本都会被解释为绘图指令

    参数:
     - level: 绘图等级
    """
    _prefix = 'p1'
    _with_bracket = False


class DrawEnd(TextBase):
    """
    关闭绘图模式，相当于 Draw(0)

    后面的文本都会被解释为普通文本

    参数:
     - level: 绘图等级
    """
    _prefix = 'p1'
    _with_bracket = False


# 注册全部 code
_codes = []
for _, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
    if '_prefix' not in cls.__dict__ or not cls.__dict__.get('_prefix'):
        continue
    prefix = cls.__dict__.get('_prefix')
    _codes.append((prefix, cls))

# 将code按前缀长度排序
_codes.sort(key=lambda pair: len(pair[0]), reverse=True)
_codes_mapper: dict[str, type] = {_code[0]: _code[1] for _code in _codes}
del _codes
