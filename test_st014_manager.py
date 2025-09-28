#!/usr/bin/env python3
"""
测试ST.014规则在规则管理器中的集成
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'rules'))

from st_rules.reference import STRules

def test_st014_in_manager():
    """测试ST.014规则在规则管理器中的集成"""
    print("测试ST.014规则在规则管理器中的集成")
    print("="*60)
    
    # 创建ST规则管理器
    st_rules = STRules()
    
    # 检查规则是否已注册
    available_rules = st_rules.get_available_rules()
    print(f"可用规则数量: {len(available_rules)}")
    print(f"ST.014规则是否已注册: {'ST.014' in available_rules}")
    
    # 获取ST.014规则信息
    rule_info = st_rules.get_rule_info("ST.014")
    if rule_info:
        print(f"\nST.014规则信息:")
        print(f"  规则ID: {rule_info.get('rule_id')}")
        print(f"  标题: {rule_info.get('title')}")
        print(f"  类别: {rule_info.get('category')}")
        print(f"  严重级别: {rule_info.get('severity')}")
        print(f"  描述: {rule_info.get('description')}")
        print(f"  实现状态: {rule_info.get('implementation')}")
        print(f"  版本: {rule_info.get('version')}")
        
        # 显示命名模式
        naming_pattern = rule_info.get('naming_pattern', {})
        print(f"\n命名模式:")
        for key, value in naming_pattern.items():
            print(f"  {key}: {value}")
        
        # 显示有效示例
        examples = rule_info.get('examples', {})
        if 'valid' in examples:
            print(f"\n有效示例:")
            for example in examples['valid'][:5]:  # 只显示前5个
                print(f"  - {example}")
        
        if 'invalid' in examples:
            print(f"\n无效示例:")
            for example in examples['invalid'][:5]:  # 只显示前5个
                print(f"  - {example}")
    
    print("\n" + "="*60)
    print("测试完成!")

if __name__ == "__main__":
    test_st014_in_manager()
