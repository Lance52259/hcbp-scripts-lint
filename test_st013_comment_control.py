#!/usr/bin/env python3
"""
测试ST.013规则的注释控制功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'rules'))

from st_rules.rule_013 import check_st013_directory_naming
from comment_control import CommentController

def mock_log_error(file_path, rule_id, message, line_num):
    """模拟错误日志函数"""
    print(f"[{rule_id}] {file_path}:{line_num} - {message}")

def test_st013_comment_control():
    """测试ST.013规则的注释控制功能"""
    print("测试ST.013规则的注释控制功能")
    print("="*60)
    
    # 创建注释控制器
    comment_controller = CommentController()
    
    # 创建测试文件内容（包含注释控制）
    test_content = '''# ST.013 Disable
resource "huaweicloud_vpc" "test" {
  name = "test"
}
# ST.013 Enable'''
    
    # 创建测试文件
    test_file = 'test-dirs/test_with_comments.tf'
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    print("测试文件内容:")
    print(test_content)
    print("\n" + "="*60)
    
    # 解析注释控制
    control_states = comment_controller.parse_control_comments(test_content)
    print("\n解析的注释控制状态:")
    for line_num, state in control_states.items():
        print(f"  行 {line_num}: {state.rule_id} {state.control_type}")
    
    # 创建受控制的日志函数
    def controlled_log_func(path: str, rule: str, message: str, line_number: int = None):
        # 检查规则是否在该行被禁用
        if line_number is not None and control_states:
            if not comment_controller.get_rule_state_at_line(rule, line_number, control_states):
                print(f"  [跳过] {rule} 在第 {line_number} 行被禁用")
                return  # 跳过日志记录
        # 调用原始日志函数
        mock_log_error(path, rule, message, line_number)
    
    print("\n运行ST.013规则检查（带注释控制）:")
    print("-" * 40)
    check_st013_directory_naming(test_file, test_content, controlled_log_func)
    
    print("\n" + "="*60)
    print("测试完成!")

if __name__ == "__main__":
    test_st013_comment_control()
