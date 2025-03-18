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

 Date: 27/02/2025 13:52:32
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for management_unit_0227_to_li
-- ----------------------------
DROP TABLE IF EXISTS `management_unit_0227_to_li`;
CREATE TABLE `management_unit_0227_to_li`  (
  `id` bigint(20) NOT NULL,
  `parent_id` bigint(64) NULL DEFAULT 0 COMMENT '父主键',
  `ancestors` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '祖级列表',
  `management_unit_name` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '部门名',
  `full_name` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '部门全称',
  `sort` int(11) NULL DEFAULT NULL COMMENT '排序',
  `is_deleted` int(2) NULL DEFAULT 0 COMMENT '是否已删除',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of management_unit_0227_to_li
-- ----------------------------
INSERT INTO `management_unit_0227_to_li` VALUES (1437327395446067201, 0, '0', '浙江交投集团', '浙江省交通投资集团有限公司', 2, 0);
INSERT INTO `management_unit_0227_to_li` VALUES (1437327534965395457, 1437327395446067201, '0,1437327395446067201', '沪杭甬公司', '浙江沪杭甬高速公路股份有限公司', 1, 0);
INSERT INTO `management_unit_0227_to_li` VALUES (1437328542420451329, 1437327534965395457, '0,1437327395446067201,1437327534965395457', '绍兴管理中心', '浙江省交通集团高速公路绍兴管理中心', 2, 0);
INSERT INTO `management_unit_0227_to_li` VALUES (1437328595121881089, 1437327534965395457, '0,1437327395446067201,1437327534965395457', '嘉兴管理中心', '浙江省交通集团高速公路嘉兴管理中心', 4, 0);
INSERT INTO `management_unit_0227_to_li` VALUES (1437328939809783809, 1437327622278221826, '0,1437327395446067201,1437327622278221826', '台州管理中心', '浙江省交通集团高速公路台州管理中心', 10, 0);
INSERT INTO `management_unit_0227_to_li` VALUES (1438321516184973313, 1437327622278221826, '0,1437327395446067201,1437327622278221826', '丽水管理中心', '浙江省交通集团高速公路丽水管理中心', 11, 0);

SET FOREIGN_KEY_CHECKS = 1;
