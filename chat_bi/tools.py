"""
ADK Tools 模块
基于Google ADK实现的各种工具
"""

import os
import time
import re
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

# 导入原有模块以保持兼容性
from app.tool.sql import execute_sql_to_csv
from app.tool import extractor
from chat_bi import store
from .config import app_config


@dataclass
class ToolResult:
    """工具执行结果"""
    success: bool
    content: str
    metadata: Dict[str, Any]
    error: Optional[str] = None


class SQLExecutor:
    """SQL执行工具 - 基于ADK的实现"""
    
    def __init__(self, db_config: Optional[Dict[str, str]] = None):
        """初始化SQL执行器
        
        Args:
            db_config: 数据库配置，如果为None则使用全局配置
        """
        self.db_config = db_config or app_config.database.to_dict()
        self.description = "执行SQL查询并返回结果数据，支持MySQL 8.0语法"
        # 为ADK框架添加__name__属性
        self.__name__ = "sql_executor"
        
    @property
    def name(self) -> str:
        """工具名称"""
        return self.__name__
    
    def __call__(self, sql: str, session_id: str = "") -> Dict[str, Any]:
        """执行SQL查询
        
        Args:
            sql: SQL查询语句
            session_id: 会话ID
            
        Returns:
            包含执行结果的字典
        """
        try:
            if not session_id:
                session_id = time.strftime("%Y%m%d%H%M%S", time.localtime())
            
            # 验证SQL安全性
            if not self._validate_sql(sql):
                return {
                    "success": False,
                    "content": "SQL语句包含不安全的操作，仅支持SELECT查询",
                    "sql": sql,
                    "error": "Unsafe SQL operation"
                }
            
            csv_path = store.get_csv_path(session_id)
            # 确保db_config中的值不为None
            safe_db_config = {k: v for k, v in self.db_config.items() if v is not None}
            results = execute_sql_to_csv(sql, csv_path, safe_db_config)
            
            if results:
                return {
                    "success": True,
                    "content": results,
                    "csv_path": csv_path,
                    "sql": sql,
                    "row_count": len(results.split('\n')) - 1 if results else 0
                }
            else:
                return {
                    "success": False,
                    "content": "未查到任何统计数据，请重新调整查询条件",
                    "sql": sql
                }
                
        except Exception as e:
            return {
                "success": False,
                "content": f"SQL执行错误: {str(e)}",
                "sql": sql,
                "error": str(e)
            }
    
    def _validate_sql(self, sql: str) -> bool:
        """验证SQL语句的安全性"""
        try:
            sql_lower = sql.lower().strip()
            
            # 检查是否是查询语句
            if not sql_lower.startswith('select'):
                return False
                
            # 检查是否包含危险操作
            dangerous_keywords = ['drop', 'delete', 'update', 'insert', 'create', 'alter', 'exec', 'execute']
            if any(keyword in sql_lower for keyword in dangerous_keywords):
                return False
                
            return True
            
        except Exception:
            return False


class ChartRecommender:
    """图表推荐工具"""
    
    def __init__(self):
        self.description = "根据数据类型和查询内容推荐合适的图表类型"
        # 为ADK框架添加__name__属性
        self.__name__ = "chart_recommender"
        self.chart_types = {
            1: "柱状图 - 适合比较不同类别的数值",
            2: "折线图 - 适合显示趋势变化",
            3: "饼图 - 适合显示比例关系",
            4: "散点图 - 适合显示相关性",
            5: "条形图 - 适合显示排名",
            6: "面积图 - 适合显示累积数据",
            7: "热力图 - 适合显示矩阵数据",
            8: "漏斗图 - 适合显示转化流程",
            9: "雷达图 - 适合显示多维度比较"
        }
        
    @property
    def name(self) -> str:
        """工具名称"""
        return self.__name__
    
    def __call__(self, query_content: str, data_sample: str = "", column_info: Optional[List[str]] = None) -> Dict[str, Any]:
        """推荐图表类型
        
        Args:
            query_content: 查询内容
            data_sample: 数据样本
            column_info: 列信息
            
        Returns:
            包含推荐结果的字典
        """
        try:
            chart_type = self._analyze_chart_type(query_content, data_sample, column_info)
            
            return {
                "success": True,
                "content": f"推荐使用图表编号: {chart_type}",
                "chart_type": chart_type,
                "chart_description": self.chart_types.get(chart_type, "柱状图"),
                "reason": f"基于查询内容'{query_content}'的分析",
                "alternative_charts": self._get_alternative_charts(chart_type)
            }
            
        except Exception as e:
            return {
                "success": False,
                "content": f"图表推荐失败: {str(e)}",
                "error": str(e)
            }
    
    def _analyze_chart_type(self, query_content: str, data_sample: str, column_info: Optional[List[str]]) -> int:
        """分析并推荐图表类型"""
        query_lower = query_content.lower()
        
        # 基于查询内容的关键词匹配
        if any(keyword in query_lower for keyword in ["趋势", "时间", "月份", "年份", "变化", "增长", "下降"]):
            return 2  # 折线图
        elif any(keyword in query_lower for keyword in ["比例", "占比", "百分比", "份额", "分布"]):
            return 3  # 饼图
        elif any(keyword in query_lower for keyword in ["排名", "排序", "前几", "前十", "top"]):
            return 5  # 条形图
        elif any(keyword in query_lower for keyword in ["对比", "比较", "分类", "类别"]):
            return 1  # 柱状图
        elif any(keyword in query_lower for keyword in ["相关", "关系", "散布"]):
            return 4  # 散点图
        elif any(keyword in query_lower for keyword in ["累积", "累计", "总和"]):
            return 6  # 面积图
        elif any(keyword in query_lower for keyword in ["转化", "漏斗", "流程"]):
            return 8  # 漏斗图
        elif any(keyword in query_lower for keyword in ["多维", "维度", "评分", "能力"]):
            return 9  # 雷达图
        
        # 基于列信息的智能推荐
        if column_info:
            if len(column_info) >= 3:
                # 多维数据，可能适合雷达图或热力图
                return 7 if len(column_info) > 5 else 9
            elif any('time' in col.lower() or 'date' in col.lower() for col in column_info):
                return 2  # 时间序列数据用折线图
        
        return 1  # 默认柱状图
    
    def _get_alternative_charts(self, primary_chart: int) -> List[Dict[str, Any]]:
        """获取备选图表建议"""
        alternatives = []
        
        # 基于主推荐图表提供备选方案
        if primary_chart == 1:  # 柱状图
            alternatives = [2, 5]  # 折线图、条形图
        elif primary_chart == 2:  # 折线图
            alternatives = [1, 6]  # 柱状图、面积图
        elif primary_chart == 3:  # 饼图
            alternatives = [1, 5]  # 柱状图、条形图
        
        return [
            {"type": alt, "description": self.chart_types.get(alt, "")}
            for alt in alternatives[:2]  # 最多返回2个备选
        ]


class DataValidator:
    """数据验证工具"""
    
    def __init__(self):
        self.description = "验证和清理数据，检查数据质量"
        # 为ADK框架添加__name__属性
        self.__name__ = "data_validator"
    
    @property
    def name(self) -> str:
        """工具名称"""
        return self.__name__
    
    def __call__(self, data: str, data_type: str = "csv") -> Dict[str, Any]:
        """验证数据质量
        
        Args:
            data: 数据内容
            data_type: 数据类型
            
        Returns:
            验证结果
        """
        try:
            if data_type == "csv":
                return self._validate_csv_data(data)
            else:
                return {
                    "success": False,
                    "content": f"不支持的数据类型: {data_type}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "content": f"数据验证失败: {str(e)}",
                "error": str(e)
            }
    
    def _validate_csv_data(self, csv_data: str) -> Dict[str, Any]:
        """验证CSV数据"""
        if not csv_data.strip():
            return {
                "success": False,
                "content": "数据为空"
            }
        
        lines = csv_data.strip().split('\n')
        if len(lines) < 2:
            return {
                "success": False,
                "content": "数据行数不足，需要至少包含标题行和一行数据"
            }
        
        # 分析数据质量
        header = lines[0].split(',')
        data_lines = lines[1:]
        
        quality_info = {
            "total_rows": len(data_lines),
            "total_columns": len(header),
            "column_names": header,
            "has_empty_cells": any('' in line.split(',') for line in data_lines),
            "duplicate_rows": len(data_lines) - len(set(data_lines))
        }
        
        return {
            "success": True,
            "content": "数据验证完成",
            "quality_info": quality_info,
            "recommendations": self._get_data_recommendations(quality_info)
        }
    
    def _get_data_recommendations(self, quality_info: Dict[str, Any]) -> List[str]:
        """获取数据改进建议"""
        recommendations = []
        
        if quality_info.get("has_empty_cells"):
            recommendations.append("检测到空值，建议进行数据清理")
        
        if quality_info.get("duplicate_rows", 0) > 0:
            recommendations.append(f"检测到 {quality_info['duplicate_rows']} 行重复数据")
        
        if quality_info.get("total_rows", 0) < 10:
            recommendations.append("数据量较少，分析结果可能不够准确")
        
        return recommendations


class QueryExtractor:
    """查询提取工具 - 兼容原有功能"""
    
    def __init__(self):
        self.description = "从文本中提取SQL查询语句"
        # 为ADK框架添加__name__属性
        self.__name__ = "query_extractor"
    
    @property
    def name(self) -> str:
        """工具名称"""
        return self.__name__
    
    def extract_sql_queries(self, text: str) -> List[str]:
        """提取SQL查询语句"""
        return extractor.extract_sql_queries(text)
    
    def extract_analysis_intent(self, text: str) -> Dict[str, Any]:
        """提取分析意图"""
        intent_keywords = {
            "statistical": ["统计", "总数", "平均", "最大", "最小", "求和"],
            "comparison": ["对比", "比较", "差异", "变化"],
            "trend": ["趋势", "增长", "下降", "变化趋势"],
            "ranking": ["排名", "排序", "前几", "后几", "top"],
            "distribution": ["分布", "比例", "占比", "百分比"]
        }
        
        detected_intents = []
        text_lower = text.lower()
        
        for intent_type, keywords in intent_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_intents.append(intent_type)
        
        return {
            "intents": detected_intents,
            "primary_intent": detected_intents[0] if detected_intents else "general",
            "confidence": len(detected_intents) / len(intent_keywords)
        } 