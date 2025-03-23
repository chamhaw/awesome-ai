/*
 Navicat Premium Data Transfer

 Source Server         : 交投
 Source Server Type    : MySQL
 Source Server Version : 50725
 Source Host           : 10.100.179.252:8008
 Source Schema         : maintenance-assets

 Target Server Type    : MySQL
 Target Server Version : 50725
 File Encoding         : 65001

 Date: 27/02/2025 13:48:08
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for highway_segment_0227_to_li
-- ----------------------------
DROP TABLE IF EXISTS `highway_segment_0227_to_li`;
CREATE TABLE `highway_segment_0227_to_li`  (
  `id` bigint(20) NOT NULL COMMENT '路段id',
  `management_segment_id` bigint(20) NULL DEFAULT NULL COMMENT '管理路线id',
  `code` varchar(50) CHARACTER SET sjis COLLATE sjis_japanese_ci NULL DEFAULT NULL COMMENT '路段编号',
  `full_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '路段全称',
  `simple_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '路段简称',
  `highway_id` bigint(20) NULL DEFAULT NULL COMMENT '路线id',
  `highway_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '路线编码',
  `region_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '所在政区',
  `region_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '区划代码',
  `start_pile_code` decimal(8, 3) NULL DEFAULT NULL COMMENT '起点桩号编号(单位:km)',
  `start_pile_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '起点桩号名称',
  `center_pile_code` decimal(8, 3) NULL DEFAULT NULL COMMENT '中点桩号编号(单位:km)',
  `end_pile_code` decimal(8, 3) NULL DEFAULT NULL COMMENT '终点桩号编号(单位:km)',
  `end_pile_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '终点桩号名称',
  `start_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '起点名称',
  `end_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '终点名称',
  `upward_direction` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '上行方向',
  `downward_direction` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '下行方向',
  `broken_chain_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '断链类型(字典：1 正常；2 长链；3 短链；4 其他)',
  `mileage` decimal(8, 3) NULL DEFAULT NULL COMMENT '里程(单位:km)',
  `design_speed` decimal(8, 3) NULL DEFAULT NULL COMMENT '设计速度(单位:km/h)',
  `maintenance_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '养护类别(字典：1 一类；2 二类；3 三类)',
  `management_unit_id` bigint(20) NULL DEFAULT NULL COMMENT '管养单位id',
  `management_unit_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '管养单位名称',
  `legal_unit_id` bigint(20) NULL DEFAULT NULL COMMENT '法人单位id',
  `legal_unit_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '法人单位名称',
  `company_segment_id` bigint(20) NULL DEFAULT NULL COMMENT '公司级管理段id',
  `company_segment_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '公司级管理段名称',
  `center_segment_id` bigint(20) NULL DEFAULT NULL COMMENT '中心级管理段id',
  `center_segment_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '中心级管理段名称',
  `cost_benchmarking` float NULL DEFAULT NULL COMMENT '成本对标',
  `standard_mileage` decimal(8, 3) NULL DEFAULT NULL COMMENT '养护标准里程',
  `create_user` bigint(20) NULL DEFAULT NULL COMMENT '创建人',
  `create_dept` bigint(20) NULL DEFAULT NULL COMMENT '创建部门',
  `create_time` datetime(0) NULL DEFAULT NULL COMMENT '创建时间',
  `update_user` bigint(20) NULL DEFAULT NULL COMMENT '修改人',
  `update_time` datetime(0) NULL DEFAULT NULL COMMENT '修改时间',
  `status` int(2) NULL DEFAULT NULL COMMENT '状态',
  `is_deleted` int(2) NULL DEFAULT 0 COMMENT '是否已删除',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '路段数据' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of highway_segment_0227_to_li
-- ----------------------------
INSERT INTO `highway_segment_0227_to_li` VALUES (1505830070116270081, 103368523400781825, 'G15', '宁波-台州-温州高速公路', '甬台温高速台州段', 1505792506961432578, 'G15', NULL, NULL, 1589.911, 'K1589+911', 1611.311, 1632.711, 'K1632+711', NULL, NULL, '海向', '沈向', '1', 42.800, 120.000, '1', 10009615, '台州管理中心', NULL, NULL, NULL, NULL, NULL, NULL, 1656, 48.957, NULL, 10000001, '2000-01-01 04:46:42', NULL, '2000-01-01 04:48:04', 1, 0);
INSERT INTO `highway_segment_0227_to_li` VALUES (1505830070116270089, 103368519730765830, 'G1522', '上虞-三门高速公路', '上三高速新天段', 1505792507125010433, 'G1522', NULL, NULL, 259.610, 'K259+610', 297.778, 335.946, 'K335+946', NULL, NULL, '三门向', '上虞向', '1', 76.336, 100.000, '1', 10009828, '绍兴管理中心', NULL, NULL, NULL, NULL, NULL, NULL, 2675.51, 84.962, NULL, 10000001, '2000-01-01 04:46:42', NULL, '2000-01-01 04:46:43', 1, 0);
INSERT INTO `highway_segment_0227_to_li` VALUES (1505830070179184650, 103368516228521992, 'G320', '上海-瑞丽高速公路', 'G320嘉兴段（K127-K146）', 1505792507125010438, 'G320', NULL, NULL, 127.000, 'K127.000', 136.850, 146.700, 'K146.700', NULL, NULL, '瑞向', '沪向', '1', 19.700, 80.000, '1', 10009826, '嘉兴管理中心', NULL, NULL, NULL, NULL, NULL, NULL, 597.6, 19.917, NULL, 10000001, '2000-01-01 04:46:42', NULL, '2000-01-01 04:46:43', 1, 1);

SET FOREIGN_KEY_CHECKS = 1;
