# easy ass

一个用于解析和操作ass字幕的python包

⚠️当前处于开发阶段，未经过严格测试

### 功能
✅ ScriptInfo、Styles、Events解析

✅ 大部分的覆写控制代码支持

✅ 字段类型，合法性检查

⬜ 绘图指令、方便的绘图支持（开发中）

~~⬜ C++内核实现 （计划）~~

### 安装
从 pip 中获取

``` shell
pip install easyass
```

支持 python 3.7 及以上版本，没有额外的库依赖。

### 例子

```python
from easyass import *  # 引入 easyass 包

# 库不提供直接读取文件的api，需要自行读写
with open(r'test.ass', 'r', encoding='utf8') as fp:  # 读一个 ass 文件
    ass_str = fp.read()
    
ass_obj = Ass()  # 创建一个 ass 实例
errs = ass_obj.parse(ass_str)  # 解析 ass 文本
print(ass.script_info.Title)  # 输出 title
ass_obj.script_info.Title = 'aabbcc'  # 修改 title

print(ass_obj.styles[0].Name)  # 获取第一条 styles 的名字
ass_obj.styles.append(StyleItem(  # 添加一个 style 并指定其部分字段
    Name='r2l',
    Fontname='Microsoft YaHei',
    Fontsize=30,
))

print(ass_obj.events[0].Start)  # 获取第一条事件的开始时间
ass_obj.events[0].Text = 'good'  # 修改第一条事件的文本
# 修改第一条事件的文本，并使用覆写代码
ass_obj.events[0].Text = Pos(1, 10) + 'good' + FontSize(size=30) 
ass_obj.events[0].Text[0].x = 60  # 修改刚才添加的覆写代码中 Pos 的属性 x, 具体属性见 docstring
print(ass_obj.events[0].dump())  # 获取第一条事件的 ass 代码

lines, errs = ass_obj.dump()
with open(r'op.ass', 'w', encoding='utf8') as fp:  # 修改后的ass写到文件
    fp.write('\n'.join(lines))  # lines是一个字符串数组，包含每一行的内容
```

