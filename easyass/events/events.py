from enum import Enum
from .text import Text

from easyass.ass_types import AssTime
from easyass.errors import Errors


class Events(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_format: EventFormat = ...

    def parse(self, ass_str: str) -> Errors:
        err = Errors()
        ass_line = ass_str.split(':', 1)
        if len(ass_line) != 2:
            return err.error(f'Fail to parse `{ass_str}` as Styles. ')
        title = ass_line[0].strip()
        if title == FORMAT_LINE_TITLE:
            self.event_format = EventFormat()
            err += self.event_format.parse(ass_str)
        elif title == str(EventTypes.dialogue.value):
            if self.event_format is ...:
                return err.error(f'`Format` line is missing. ')
            style_item = EventItem()
            err += style_item.parse(ass_str, self.event_format)
            self.append(style_item)
        return err

    def dump(self) -> (list[str], Errors):
        errors: Errors = Errors()
        dump_lines: list[str] = [
            '[{}]'.format(EVENTS_PART_TITLE)
        ]
        format_line, format_err = self.event_format.dump()  # format 行
        dump_lines += format_line
        errors += format_err

        for item in self:  # item 行
            item_line, item_error = item.dump(self.event_format)
            dump_lines += item_line
            errors += item_error
        return dump_lines, errors


class EventFormat:
    def __init__(self):
        self.event_attrs: list[str] = []

    def parse(self, ass_str: str) -> Errors:
        err = Errors()
        ass_line = ass_str.split(':', 1)
        if len(ass_line) != 2 or ass_line[0].strip() != FORMAT_LINE_TITLE:
            return err.error(f'Fail to parse `{ass_str}` as event format. ')
        style_attrs = ass_line[1].split(',')
        for event_attr in style_attrs:
            event_attr = event_attr.strip()
            if event_attr not in EVENT_ATTR_DEF:
                return err.error(f'Unknown event attribute `{event_attr}`. ')
            self.event_attrs.append(event_attr)
        return err

    def dump(self) -> (list[str], Errors):
        format_line = FORMAT_LINE_TITLE + ':' + ','.join(self.event_attrs)
        return [format_line], Errors()


class EventItem:
    def __init__(self, **kwargs):
        self.event_attrs = {attr_name: None for attr_name in EVENT_ATTR_DEF.keys()}
        self.event_type: EventTypes = ...
        for key, value in kwargs.items():  # 支持构造时传初始值
            if key in self.event_attrs:
                self.event_attrs[key] = value

    def parse(self, ass_str: str, event_format: EventFormat) -> Errors:
        err = Errors()
        ass_line = ass_str.split(':', 1)
        if len(ass_line) != 2:
            return err.error(f'Fail to parse `{ass_str}` as style values. ')
        # 解析类型
        event_type = ass_line[0].strip()
        if EventTypes(event_type) not in EventTypes:
            return err.error(f'Unknown event type `{event_type}`. ')
        self.event_type = EventTypes(event_type)

        # 解析属性
        event_values = ass_line[1].split(',', len(event_format.event_attrs) - 1)
        if len(event_values) < len(event_format.event_attrs):
            return err.error(f'`Styles` line does not match `Format` line! ')
        for index, style_attr in enumerate(event_format.event_attrs):
            try:
                self.event_attrs[style_attr] = \
                    EVENT_ATTR_DEF[style_attr](event_values[index])
            except Exception as exception:
                return err.error(f'Could not parse `{event_values[index]}` '
                                 f'as `{style_attr}`. Exception: {exception}. ')
        return err

    def dump(self, style_format: EventFormat) -> (list[str], Errors):
        err = Errors()
        style_values = []
        for style_attr in style_format.event_attrs:
            if self.event_attrs[style_attr] is None:
                err.error(f'Style `{style_attr}` not specified. ')
            else:
                style_values.append(str(self.event_attrs[style_attr]))

        events_line = self.event_type.value + ':' + ','.join(style_values)
        return [events_line], err

    def __getattr__(self, attribute):
        if attribute in self.event_attrs:
            return self.event_attrs[attribute]
        raise AttributeError(attribute)

    def __setattr__(self, key, value):
        if key in self.__dict__.get('event_attrs', {}):
            self.__dict__['event_attrs'][key] = EVENT_ATTR_DEF[key](value)
        else:
            super().__setattr__(key, value)


class EventTypes(Enum):
    dialogue = 'Dialogue'
    comment = 'Comment'
    picture = 'Picture'
    sound = 'Sound'
    movie = 'Movie'
    command = 'Command'


EVENTS_PART_TITLE = 'Events'
FORMAT_LINE_TITLE = 'Format'
EVENT_ATTR_DEF = {
    'Marked': int,  # 是否已标识
    'Layer': int,  # 图层 大的置于顶层
    'Start': AssTime,  # 开始时间
    'End': AssTime,  # 结束时间
    'Style': str,  # 使用的样式名称
    'Name': str,  # 角色名
    'MarginL': int,  # 左边距覆写值 px
    'MarginR': int,  # 右边距覆写值 px
    'MarginV': int,  # 垂直边距覆写值 px
    'Effect': str,  # 过渡效果 (暂不做特殊支持
    'Text': Text,  # 文本
}

__all__ = (
    'Events',
    'EventFormat',
    'EventItem',
    'EventTypes',
    'EVENTS_PART_TITLE',
    'FORMAT_LINE_TITLE',
    'EVENT_ATTR_DEF',
)
