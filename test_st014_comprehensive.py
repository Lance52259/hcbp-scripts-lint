#!/usr/bin/env python3
"""
全面测试ST.014规则 - 文件命名规范检查
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'rules'))

from st_rules.rule_014 import check_st014_file_naming

def mock_log_error(file_path, rule_id, message, line_num):
    """模拟错误日志函数"""
    print(f"[{rule_id}] {file_path}:{line_num} - {message}")

def test_st014_comprehensive():
    """全面测试ST.014规则"""
    print("全面测试ST.014规则 - 文件命名规范检查")
    print("="*60)
    
    # 测试有效文件
    print("\n1. 测试有效文件:")
    valid_file = 'test-files/valid-files/main.tf'
    with open(valid_file, 'w') as f:
        f.write('resource "huaweicloud_vpc" "test" {\n  name = "test"\n}')
    
    print(f"测试文件: {valid_file}")
    check_st014_file_naming(valid_file, "", mock_log_error)
    
    # 测试无效文件
    print("\n2. 测试无效文件:")
    invalid_files = [
        'test-files/invalid-files/_private.tf',
        'test-files/invalid-files/config-.tf', 
        'test-files/invalid-files/123_config.tf',
        'test-files/invalid-files/my-file.tf',
        'test-files/invalid-files/my__file.tf'
    ]
    
    for invalid_file in invalid_files:
        with open(invalid_file, 'w') as f:
            f.write('resource "huaweicloud_vpc" "test" {\n  name = "test"\n}')
        print(f"测试文件: {invalid_file}")
        check_st014_file_naming(invalid_file, "", mock_log_error)
    
    print("\n" + "="*60)
    print("测试完成!")

if __name__ == "__main__":
    test_st014_comprehensive()
