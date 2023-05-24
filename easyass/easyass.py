from scriptinfo import *
from events import *
from styles import *
from errors import Errors


class Ass:
    def __init__(self):
        self.script_info: ScriptInfo = ScriptInfo()
        self.styles: Styles = Styles()
        self.events: Events = Events()

        self._parser_status: ScriptInfo | Styles | Events = self.script_info

    def parse(self, ass_str: str) -> Errors:
        err: Errors = Errors()
        ass_str_lines = ass_str.split('\n')
        for ass_str_line in ass_str_lines:
            err += self.parse_line(ass_str_line)
        return err

    def parse_line(self, ass_str: str) -> Errors:
        err: Errors = Errors()
        ass_str = ass_str.lstrip()
        if len(ass_str) == 0:  # 空行
            return err
        if ass_str.startswith('['):
            ass_str_lower = ass_str.lower()
            if ass_str_lower.startswith(EVENTS_PART_TITLE.lower(), 1):
                self._parser_status = self.events
            elif ass_str_lower.startswith(STYLES_PART_TITLE.lower(), 1):
                self._parser_status = self.styles
            elif ass_str_lower.startswith(SCRIPT_INFO_PART_TITLE.lower(), 1):
                self._parser_status = self.script_info
        else:
            err += self._parser_status.parse(ass_str)
        return err

    def dump(self):
        script_info_lines, script_info_errs = self.script_info.dump()
        styles_lines, styles_errs = self.styles.dump()
        events_lines, events_errs = self.events.dump()
        lines = script_info_lines + [''] + styles_lines + [''] + events_lines
        errors = script_info_errs + styles_errs + events_errs
        return lines, errors
