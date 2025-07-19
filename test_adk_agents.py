#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试ADK agents的初始化和基本功能
"""

import sys
import os
import traceback

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_bi_agent():
    """测试BIAgent初始化"""
    print("🔍 测试BIAgent初始化...")
    
    try:
        from chat_bi.agents import BIAgent
        
        # 尝试初始化BIAgent
        bi_agent = BIAgent()
        print("✅ BIAgent 初始化成功")
        
        # 测试系统指令构建
        instruction = bi_agent._build_system_instruction()
        print(f"📝 系统指令长度: {len(instruction)} 字符")
        print(f"📖 前200字符预览: {instruction[:200]}...")
        
        # 检查是否包含知识库内容
        if "道路管理系统" in instruction:
            print("✅ 知识库内容已正确包含在系统指令中")
        else:
            print("⚠️ 系统指令中未找到知识库内容")
        
        return True
        
    except Exception as e:
        print(f"❌ BIAgent 初始化失败: {str(e)}")
        print(f"🔍 详细错误:\n{traceback.format_exc()}")
        return False

def test_sql_agent():
    """测试SQLAgent初始化"""
    print("\n🔍 测试SQLAgent初始化...")
    
    try:
        from chat_bi.agents import SQLAgent
        
        # 尝试初始化SQLAgent
        sql_agent = SQLAgent()
        print("✅ SQLAgent 初始化成功")
        
        # 测试SQL指令构建
        instruction = sql_agent._build_sql_instruction()
        print(f"📝 SQL指令长度: {len(instruction)} 字符")
        print(f"📖 前200字符预览: {instruction[:200]}...")
        
        # 检查是否包含知识库内容
        if "道路管理系统" in instruction:
            print("✅ 知识库内容已正确包含在SQL指令中")
        else:
            print("⚠️ SQL指令中未找到知识库内容")
        
        return True
        
    except Exception as e:
        print(f"❌ SQLAgent 初始化失败: {str(e)}")
        print(f"🔍 详细错误:\n{traceback.format_exc()}")
        return False

def test_analysis_agent():
    """测试AnalysisAgent初始化"""
    print("\n🔍 测试AnalysisAgent初始化...")
    
    try:
        from chat_bi.agents import AnalysisAgent
        
        # 尝试初始化AnalysisAgent
        analysis_agent = AnalysisAgent()
        print("✅ AnalysisAgent 初始化成功")
        
        # 测试分析指令构建
        instruction = analysis_agent._build_analysis_instruction()
        print(f"📝 分析指令长度: {len(instruction)} 字符")
        print(f"📖 前200字符预览: {instruction[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ AnalysisAgent 初始化失败: {str(e)}")
        print(f"🔍 详细错误:\n{traceback.format_exc()}")
        return False

def main():
    """主函数"""
    print("🚀 开始测试ADK agents...")
    print("=" * 60)
    
    # 测试各个代理
    bi_success = test_bi_agent()
    sql_success = test_sql_agent()
    analysis_success = test_analysis_agent()
    
    print("\n" + "=" * 60)
    print("🎯 测试结果:")
    print(f"  BIAgent: {'✅ 成功' if bi_success else '❌ 失败'}")
    print(f"  SQLAgent: {'✅ 成功' if sql_success else '❌ 失败'}")
    print(f"  AnalysisAgent: {'✅ 成功' if analysis_success else '❌ 失败'}")
    
    if all([bi_success, sql_success, analysis_success]):
        print("🎉 所有ADK agents测试通过！")
    else:
        print("⚠️ 部分ADK agents测试失败，请检查配置")

if __name__ == "__main__":
    main() 