from easy_ass import *

with open(r'test.ass', 'r', encoding='utf8') as fp:
    ass_str = fp.read()


ass_obj = Ass()
err = ass_obj.parse(ass_str)
for e in err:
    print(e['level'], e['message'])

s, err = ass_obj.dump()
with open(r'D:\wc_op!.ass', 'w', encoding='utf-8') as fp:
    fp.write('\n'.join(s))
for e in err:
    print(e['level'], e['message'])
