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

 Date: 27/02/2025 13:49:36
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for highway_0227_to_li
-- ----------------------------
DROP TABLE IF EXISTS `highway_0227_to_li`;
CREATE TABLE `highway_0227_to_li`  (
  `id` bigint(20) NOT NULL COMMENT '路线id',
  `code` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '路线编号',
  `full_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '路线全称',
  `simple_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '路线简称',
  `start_pile_code` decimal(8, 3) NULL DEFAULT NULL COMMENT '起点桩号编号(单位:km)',
  `start_pile_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '起点桩号名称',
  `end_pile_code` decimal(8, 3) NULL DEFAULT NULL COMMENT '终点桩号编号(单位:km)',
  `end_pile_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '终点桩号名称',
  `technical_grade` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '路线技术等级(字典：10 高速公路；11 一级公路；12 二级公路；13 三级公路；14 四级公路；30等外公路)',
  `administrative_grade` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '路线行政等级(字典：G 国道；S 省道；X 县道；Y 乡道；C 村道；Z 专用公路)',
  `highway_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '路线类型(字典：0 首都放射线；1 省会放射线；2 北南纵线；3 东西横线；4 地区环线；5 城市绕城环线；6 联络线；7 并行线；8 连接线)',
  `trend` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '走向(字典：0 北；1 东北；2 东；3 东南；4 南；5 西南；6 西；7 西北；8 环形；9 其他)',
  `upward_direction` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '上行方向',
  `downward_direction` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '下行方向',
  `create_user` bigint(20) NULL DEFAULT NULL COMMENT '创建人',
  `create_dept` bigint(20) NULL DEFAULT NULL COMMENT '创建部门',
  `create_time` datetime(0) NULL DEFAULT NULL COMMENT '创建时间',
  `update_user` bigint(20) NULL DEFAULT NULL COMMENT '修改人',
  `update_time` datetime(0) NULL DEFAULT NULL COMMENT '修改时间',
  `status` int(2) NULL DEFAULT NULL COMMENT '状态',
  `is_deleted` int(2) NULL DEFAULT 0 COMMENT '是否已删除',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '路线数据' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of highway_0227_to_li
-- ----------------------------
INSERT INTO `highway_0227_to_li` VALUES (1505792506961432578, 'G15', '沈阳-海口高速公路', '沈海高速', 0.000, 'K0+000', 3710.000, 'K3710+000', '10', 'G', '2', '3', '海向', '沈向', NULL, NULL, NULL, NULL, '2000-01-01 04:47:00', 1, 0);
INSERT INTO `highway_0227_to_li` VALUES (1505792507125010433, 'G1522', '常熟-台州高速公路', '常台高速', 0.000, 'K0+000', 335.946, 'K335+946', '10', 'G', '7', '0', '台向', '常向', NULL, NULL, NULL, NULL, '2000-01-01 04:47:00', 1, 0);
INSERT INTO `highway_0227_to_li` VALUES (1505792507125010437, 'G3', '北京-台北高速公路', '京台高速', 0.000, 'K0+000', 2030.000, 'K2030+000', '10', 'G', '0', '4', '台向', '京向', NULL, NULL, NULL, NULL, '2000-01-01 04:47:00', 1, 0);
INSERT INTO `highway_0227_to_li` VALUES (1505792507125010438, 'G320', '上海-瑞丽高速公路', '沪瑞公路', 0.000, 'K0+000', 3695.000, 'K3695+000', '12', 'G', '3', '5', '瑞向', '沪向', NULL, NULL, NULL, NULL, '2000-01-01 04:47:00', 1, 1);

SET FOREIGN_KEY_CHECKS = 1;
