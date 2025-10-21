#!/usr/bin/env python3
"""YouTube 视频摘要工具 - 主程序入口"""

import sys
from src.cli import main

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误: {e}")
        sys.exit(1)
