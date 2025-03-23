/*
 Navicat Premium Data Transfer

 Source Server         : 交投
 Source Server Type    : MySQL
 Source Server Version : 50725
 Source Host           : 10.100.179.252:8008
 Source Schema         : maintenance-road

 Target Server Type    : MySQL
 Target Server Version : 50725
 File Encoding         : 65001

 Date: 27/02/2025 13:44:10
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for regular_contract_0227_to_li
-- ----------------------------
DROP TABLE IF EXISTS `regular_contract_0227_to_li`;
CREATE TABLE `regular_contract_0227_to_li`  (
  `id` bigint(20) NOT NULL COMMENT '路面定检合同id',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '合同名称',
  `code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '合同编号',
  `project_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '项目名称',
  `check_year` int(11) NULL DEFAULT NULL COMMENT '所属年度',
  `check_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '检测类型（字典：1 集团检；2 省检）',
  `contract_status` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '合同状态（字典：0 未完成；1 已完成）',
  `contract_amount` decimal(12, 4) NULL DEFAULT NULL COMMENT '合同额',
  `start_time` date NULL DEFAULT NULL COMMENT '开始时间',
  `end_time` date NULL DEFAULT NULL COMMENT '结束时间',
  `check_unit_id` bigint(20) NULL DEFAULT NULL COMMENT '检测单位id',
  `check_unit_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '检测单位名称',
  `create_user` bigint(20) NULL DEFAULT NULL COMMENT '创建人',
  `create_dept` bigint(20) NULL DEFAULT NULL COMMENT '创建部门',
  `create_time` datetime(0) NULL DEFAULT NULL COMMENT '创建时间',
  `update_user` bigint(20) NULL DEFAULT NULL COMMENT '修改人',
  `update_time` datetime(0) NULL DEFAULT NULL COMMENT '修改时间',
  `status` int(2) NULL DEFAULT NULL COMMENT '状态',
  `is_deleted` int(2) NULL DEFAULT 0 COMMENT '是否已删除',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '路面定检合同表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of regular_contract_0227_to_li
-- ----------------------------
INSERT INTO `regular_contract_0227_to_li` VALUES (1848561611699257346, '2024年半年度省检（合）', NULL, NULL, 2024, '2', NULL, NULL, '2024-06-01', '2024-06-30', NULL, NULL, 1123598821738675201, 10015083, '2024-10-22 11:06:47', 1123598821738675201, '2024-12-30 08:47:08', 1, 0);
INSERT INTO `regular_contract_0227_to_li` VALUES (1872452338844377090, '集团路网2024年路面定检数据（定稿）', NULL, NULL, 2024, '1', NULL, NULL, '2024-08-01', '2024-11-30', NULL, NULL, 1123598821738675201, 10015083, '2024-12-27 09:20:01', 1123598821738675201, '2025-01-02 15:15:24', 1, 1);
INSERT INTO `regular_contract_0227_to_li` VALUES (1874033345653833730, '收到哇哦', NULL, NULL, 2024, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1123598821738675201, 10015083, '2024-12-31 18:02:22', 1123598821738675201, '2025-01-02 09:03:28', 1, 1);
INSERT INTO `regular_contract_0227_to_li` VALUES (1874626517530255361, '计算修正', NULL, NULL, 2024, '1', NULL, NULL, '2024-11-13', '2024-12-18', NULL, NULL, 1123598821738675201, 10015083, '2025-01-02 09:19:25', 1123598821738675201, '2025-01-02 11:41:31', 1, 1);
INSERT INTO `regular_contract_0227_to_li` VALUES (1874700514833932290, '集团路网2024年路面定检数据（定稿）', NULL, NULL, 2024, '1', NULL, NULL, '2024-08-01', '2024-11-30', NULL, NULL, 1123598821738675201, 10015083, '2025-01-02 14:13:28', 1123598821738675201, '2025-01-02 15:17:07', 1, 0);

SET FOREIGN_KEY_CHECKS = 1;
