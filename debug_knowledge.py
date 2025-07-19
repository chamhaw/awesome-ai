#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试知识库和模板格式化问题的脚本
"""

import sys
import os
import traceback

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_knowledge_module():
    """测试knowledge模块"""
    print("🔍 测试knowledge模块...")
    
    try:
        from chat_bi.knowledge import get_knowledge, retrieve_knowledge_from_local
        
        # 测试本地知识库检索
        knowledge_dir = "knowledge"
        print(f"📂 检查知识库目录: {knowledge_dir}")
        
        if not os.path.exists(knowledge_dir):
            print(f"❌ 知识库目录不存在: {knowledge_dir}")
            return False
        
        local_knowledge = retrieve_knowledge_from_local(knowledge_dir)
        print(f"📚 本地知识库内容长度: {len(local_knowledge)} 字符")
        
        if local_knowledge:
            print(f"✅ 本地知识库读取成功")
            print(f"📖 前100字符预览: {local_knowledge[:100]}...")
        else:
            print(f"⚠️ 本地知识库为空")
            
        # 测试get_knowledge函数
        user_prompt = "测试查询"
        knowledge = get_knowledge(user_prompt)
        print(f"🔍 get_knowledge 返回长度: {len(knowledge)} 字符")
        
        return True
        
    except Exception as e:
        print(f"❌ knowledge模块测试失败: {str(e)}")
        print(f"🔍 详细错误:\n{traceback.format_exc()}")
        return False

def test_template_formatting():
    """测试模板格式化"""
    print("\n🔍 测试模板格式化...")
    
    try:
        from chat_bi.knowledge import get_knowledge
        from chat_bi.prompt import system_prompts
        
        # 获取知识库内容
        user_prompt = "测试查询"
        knowledge = get_knowledge(user_prompt)
        
        print(f"📚 知识库内容长度: {len(knowledge)} 字符")
        print(f"📋 测试模板: system_prompts.gen_sql")
        
        # 测试模板格式化
        try:
            formatted_prompt = system_prompts.gen_sql.format(knowledge=knowledge)
            print(f"✅ 模板格式化成功")
            print(f"📝 格式化后长度: {len(formatted_prompt)} 字符")
            print(f"📖 前200字符预览: {formatted_prompt[:200]}...")
        except KeyError as e:
            print(f"❌ 模板格式化失败 - 缺少变量: {str(e)}")
            print(f"🔍 模板内容预览: {system_prompts.gen_sql[:200]}...")
        except Exception as e:
            print(f"❌ 模板格式化异常: {str(e)}")
            print(f"🔍 详细错误:\n{traceback.format_exc()}")
            
        return True
        
    except Exception as e:
        print(f"❌ 模板格式化测试失败: {str(e)}")
        print(f"🔍 详细错误:\n{traceback.format_exc()}")
        return False

def test_store_module():
    """测试store模块的prompt_prepare函数"""
    print("\n🔍 测试store模块...")
    
    try:
        from chat_bi import store
        from chat_bi.prompt import system_prompts
        
        # 测试prompt_prepare函数
        user_prompt = "测试查询"
        system_prompt = system_prompts.gen_sql
        session_id = "test_session"
        history = []
        
        prepared_prompt, updated_history = store.prompt_prepare(
            user_prompt, system_prompt, session_id, history
        )
        
        print(f"✅ prompt_prepare 执行成功")
        print(f"📝 准备好的提示词长度: {len(prepared_prompt)} 字符")
        print(f"📖 前200字符预览: {prepared_prompt[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ store模块测试失败: {str(e)}")
        print(f"🔍 详细错误:\n{traceback.format_exc()}")
        return False

def main():
    """主函数"""
    print("🚀 开始调试知识库和模板问题...")
    print("=" * 60)
    
    # 测试各个模块
    test_knowledge_module()
    test_template_formatting()
    test_store_module()
    
    print("\n" + "=" * 60)
    print("🎯 调试完成")

if __name__ == "__main__":
    main() 