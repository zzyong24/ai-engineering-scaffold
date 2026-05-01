# 代码风格

> 本文件定义 Python 代码风格约束。
> 自动生成于 2026-05-01

---

## 格式化

- 使用 `black` 自动格式化
- 行长度：88 字符（black 默认）
- 缩进：4 空格

## 命名

- 变量/函数：`snake_case`
- 类：`PascalCase`
- 常量：`SCREAMING_SNAKE_CASE`
- 私有：`_single_leading_underscore`

## 类型标注

- 必须为公共函数添加类型标注
- 使用 `typing` 模块（`List`, `Dict`, `Optional`）
- 复杂类型使用 `TypeAlias`

## 错误处理

- 异常继承 `Exception` 或 `BaseException`
- 捕获具体异常类型，不用 `except Exception`
- 使用 `logging` 记录错误，不用 `print`

## 导入

- 分组：标准库 → 第三方 → 本地
- 禁止使用 `from module import *`
- 使用 `isort` 自动排序

## 文档

- 公共类/函数使用 docstring
- 格式：三引号
