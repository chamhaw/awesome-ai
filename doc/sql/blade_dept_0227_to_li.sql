/*
 Navicat Premium Data Transfer

 Source Server         : 交投
 Source Server Type    : MySQL
 Source Server Version : 50725
 Source Host           : 10.100.179.252:8008
 Source Schema         : maintenance-base

 Target Server Type    : MySQL
 Target Server Version : 50725
 File Encoding         : 65001

 Date: 27/02/2025 18:06:37
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for blade_dept_0227_to_li
-- ----------------------------
DROP TABLE IF EXISTS `blade_dept_0227_to_li`;
CREATE TABLE `blade_dept_0227_to_li`  (
  `id` bigint(64) NOT NULL COMMENT '主键',
  `tenant_id` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '000000' COMMENT '租户ID',
  `parent_id` bigint(64) NULL DEFAULT 0 COMMENT '父主键',
  `ancestors` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '祖级列表',
  `dept_category` int(2) NULL DEFAULT NULL COMMENT '部门类型',
  `dept_name` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '部门名',
  `full_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '部门全称',
  `sort` int(11) NULL DEFAULT NULL COMMENT '排序',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '备注',
  `is_deleted` int(2) NULL DEFAULT 0 COMMENT '是否已删除',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '机构表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of blade_dept_0227_to_li
-- ----------------------------
INSERT INTO `blade_dept_0227_to_li` VALUES (10000001, '000000', 0, '0', 1, '浙江省交通投资集团有限公司', '浙江省交通投资集团有限公司', 1, '', 0);
INSERT INTO `blade_dept_0227_to_li` VALUES (10000083, '000000', 10000001, '0,10000001', 1, '浙高运公司', '浙江交投高速公路运营管理有限公司', 10003, NULL, 0);
INSERT INTO `blade_dept_0227_to_li` VALUES (10008529, '000000', 10000001, '0,10000001', 1, '浙江沪杭甬', '浙江沪杭甬高速公路股份有限公司', 10002, NULL, 0);
INSERT INTO `blade_dept_0227_to_li` VALUES (10009615, '000000', 10000083, '0,10000001,10000083', 1, '台州管理中心', '浙江省交通集团高速公路台州管理中心', 1331, NULL, 0);
INSERT INTO `blade_dept_0227_to_li` VALUES (10009618, '000000', 10000083, '0,10000001,10000083', 1, '杭州南管理中心', '浙江省交通集团高速公路杭州南管理中心', 1064, NULL, 0);
INSERT INTO `blade_dept_0227_to_li` VALUES (10009826, '000000', 10008529, '0,10000001,10008529', 1, '嘉兴管理中心', '浙江省交通集团高速公路嘉兴管理中心', 10013, NULL, 0);
INSERT INTO `blade_dept_0227_to_li` VALUES (10009827, '000000', 10008529, '0,10000001,10008529', 1, '宁波管理中心', '浙江省交通集团高速公路宁波管理中心', 10011, NULL, 0);
INSERT INTO `blade_dept_0227_to_li` VALUES (10009828, '000000', 10008529, '0,10000001,10008529', 1, '绍兴管理中心', '浙江省交通集团高速公路绍兴管理中心', 10009, NULL, 0);

SET FOREIGN_KEY_CHECKS = 1;
