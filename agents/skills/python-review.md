# python-review

## Purpose

Python 差分を型、テスト、lint、境界設計の観点で厳密に確認します。

## Use When

- `python/` 配下を触る
- pyright warning を扱う
- API や型境界を変える

## Required Checks

- `pyright`
- `pytest python/tests/`
- `ruff check python/ --select D,E,F,I,UP`

## Core References

- `documents/coding-conventions-python.md`
- `documents/conventions/python/07_type_checker.md`
- `documents/REVIEW_PROCESS.md`
