#!/usr/bin/env python3
"""
测试ST.014规则 - 文件命名规范检查
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'rules'))

from st_rules.rule_014 import check_st014_file_naming

def mock_log_error(file_path, rule_id, message, line_num):
    """模拟错误日志函数"""
    print(f"[{rule_id}] {file_path}:{line_num} - {message}")

def test_st014_rule():
    """测试ST.014规则"""
    print("测试ST.014规则 - 文件命名规范检查")
    print("="*60)
    
    # 创建一个测试文件
    test_file = 'test-files/valid-files/test.tf'
    with open(test_file, 'w') as f:
        f.write('resource "huaweicloud_vpc" "test" {\n  name = "test"\n}')
    
    print("测试文件内容:")
    with open(test_file, 'r') as f:
        print(f.read())
    
    print("\n运行ST.014规则检查:")
    print("-" * 40)
    
    # 运行规则检查
    check_st014_file_naming(test_file, "", mock_log_error)
    
    print("\n" + "="*60)
    print("测试完成!")

if __name__ == "__main__":
    test_st014_rule()
