from easy_ass.errors import Errors
from easy_ass.base import AssAttr


class ScriptInfo:
    def __init__(self):
        self.script_info_attrs = {attr_name: None
                                  for attr_name in SCRIPT_INFO_ATTR_DEF.keys()}
        self.script_info_attrs.update({
            'ScriptType': 'V4.00+',
            'Title': '<untitled>'
        })

    def parse(self, ass_str: str) -> Errors:
        err = Errors()
        str_part = ass_str.split(':')
        if len(str_part) != 2:
            return err.error(f'Fail to parse `{ass_str}` as script info. ')
        attribute = str_part[0].strip()
        value = str_part[1].strip()
        if attribute not in self.script_info_attrs:
            return err.error(f'Unknown script info attribute `{attribute}`. ')
        try:
            attribute_type = SCRIPT_INFO_ATTR_DEF[attribute]
            self.script_info_attrs[attribute] = attribute_type(value)
        except Exception as exception:
            return err.error(f'Could not parse `{value}` as `{attribute}`. '
                             f'Exception: {exception}. ')
        return err

    def dump(self) -> (list[str], Errors):
        errors: Errors = Errors()
        dump_lines: list[str] = [
            '[{}]'.format(SCRIPT_INFO_PART_TITLE)
        ]
        for key, value in self.script_info_attrs.items():
            if value is not None:
                dump_lines.append('{}: {}'.format(key, value))
        return dump_lines, errors

    def __str__(self):
        return '\n'.join(self.dump()[0])

    def __getattr__(self, key):
        if key in self.script_info_attrs:
            return self.script_info_attrs[key]
        raise AttributeError(key)

    def __setattr__(self, key, value):
        script_info_attrs = self.__dict__.get('script_info_attrs', {})
        if key in script_info_attrs:
            script_info_attrs[key] = SCRIPT_INFO_ATTR_DEF[key](value)
        else:
            super().__setattr__(key, value)


class Collisions(AssAttr):
    _attr_type = str
    normal: str = 'Normal'
    reverse: str = 'Reverse'


class WrapStyle(AssAttr):
    _attr_type = int
    auto_but_top_line_longer: int = 0
    last_word_of_line: int = 1
    never_swap: int = 2
    auto_but_bottom_line_longer: int = 3


class ScaledBorderAndShadow(AssAttr):
    _attr_type = str
    yes: str = 'Yes'
    no: str = 'No'


SCRIPT_INFO_PART_TITLE = 'Script Info'
SCRIPT_INFO_ATTR_DEF = {
    'ScriptType': str,  # 脚本版本
    'Title': str,  # 标题
    'PlayResX': float,  # 分辨率 X
    'PlayResY': float,  # 分辨率 Y
    'Collisions': Collisions,  # 重叠处理
    'PlayDepth': int,  # 颜色深度
    'Timer': float,  # 计时器速度
    'WrapStyle': WrapStyle,  # 换行方式
    'ScaledBorderAndShadow': ScaledBorderAndShadow,  # 边框与阴影是否随分辨率缩放
    'OriginalScript': str,  # 原始作者
    'OriginalTranslation': str,  # 原始翻译者 可选
    'OriginalEditing': str,  # 原始编辑者 可选
    'OriginalTiming': str,  # 原始打轴者 可选
    'SynchPoint': float,   # 开始播放时间 可选
    'ScriptUpdatedBy': str,  # 脚本更新者 可选
    'UpdateDetails': str,  # 更新细节 可选
}


__all__ = (
    'ScriptInfo',
    'Collisions',
    'WrapStyle',
    'ScaledBorderAndShadow',
    'SCRIPT_INFO_PART_TITLE',
)
