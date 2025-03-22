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

 Date: 27/02/2025 13:41:10
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for regular_unit_0227_to_li
-- ----------------------------
DROP TABLE IF EXISTS `regular_unit_0227_to_li`;
CREATE TABLE `regular_unit_0227_to_li`  (
  `id` bigint(64) NOT NULL COMMENT '路面定检id',
  `contract_id` bigint(64) NULL DEFAULT NULL COMMENT '合同id',
  `highway_segment_id` bigint(64) NOT NULL COMMENT '路段id',
  `highway_code` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '路线编码',
  `highway_segment_simple_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '路段简称',
  `check_year` date NULL DEFAULT NULL COMMENT '检测日期',
  `bilateral_pqi` decimal(10, 2) NULL DEFAULT NULL COMMENT '双侧轮PQI',
  `pqi` decimal(10, 2) NULL DEFAULT NULL COMMENT '右侧轮PQI',
  `pci` decimal(10, 2) NULL DEFAULT NULL COMMENT 'PCI',
  `rdi` decimal(10, 2) NULL DEFAULT NULL COMMENT 'RDI\r\n',
  `bilateral_rqi` decimal(10, 2) NULL DEFAULT NULL COMMENT '双侧RQI',
  `rqi` decimal(10, 2) NULL DEFAULT NULL COMMENT '右侧RQI',
  `pbi` decimal(10, 2) NULL DEFAULT NULL COMMENT 'PBI',
  `pwi` decimal(10, 2) NULL DEFAULT NULL COMMENT 'PWI',
  `sri` decimal(10, 2) NULL DEFAULT NULL COMMENT 'SRI',
  `pssi` decimal(10, 2) NULL DEFAULT NULL COMMENT 'PSSI',
  `check_length` int(20) NULL DEFAULT NULL COMMENT '单元长度',
  `data_source` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '数据来源',
  `bilateral_pqi_excellent` decimal(10, 2) NULL DEFAULT NULL COMMENT '双侧轮PQI优等路率',
  `right_pqi_excellent` decimal(10, 2) NULL DEFAULT NULL COMMENT '右侧轮PQI优等路率',
  `pci_excellent` decimal(10, 2) NULL DEFAULT NULL COMMENT 'PCI优等路率',
  `rdi_excellent` decimal(10, 2) NULL DEFAULT NULL COMMENT 'RDI优等路率',
  `bilateral_rqi_excellent` decimal(10, 2) NULL DEFAULT NULL COMMENT '双侧轮RQI优等路率',
  `right_rqi_excellent` decimal(10, 2) NULL DEFAULT NULL COMMENT '右侧轮RQI优等路率',
  `pbi_excellent` decimal(10, 2) NULL DEFAULT NULL COMMENT 'PBI优等路率',
  `pwi_excellent` decimal(10, 2) NULL DEFAULT NULL COMMENT 'PWI优等路率',
  `sri_excellent` decimal(10, 2) NULL DEFAULT NULL COMMENT 'SRI优等路率',
  `pssi_excellent` decimal(10, 2) NULL DEFAULT NULL COMMENT 'PSSI优等路率',
  `whole_bilateral_compliance_rate` decimal(10, 2) NULL DEFAULT NULL COMMENT '全指标（双侧RQI）达标率',
  `whole_right_compliance_rate` decimal(10, 2) NULL DEFAULT NULL COMMENT '全指标（右侧RQI）达标率',
  `pci_compliance_rate` decimal(10, 2) NULL DEFAULT NULL COMMENT 'PCI达标率',
  `rdi_compliance_rate` decimal(10, 2) NULL DEFAULT NULL COMMENT 'RDI达标率',
  `bilateral_pqi_compliance_rate` decimal(10, 2) NULL DEFAULT NULL COMMENT '双侧PQI达标率',
  `bilateral_rqi_compliance_rate` decimal(10, 2) NULL DEFAULT NULL COMMENT '双侧RQI达标率',
  `right_rqi_compliance_rate` decimal(10, 2) NULL DEFAULT NULL COMMENT '右侧RQI达标率',
  `rdi_hundred_metre` decimal(10, 2) NULL DEFAULT NULL COMMENT '百米RDI≥90占比',
  `disease_scale` decimal(10, 2) NULL DEFAULT NULL COMMENT '病害规模（单位平方米/车道公里）',
  `crack_scale` decimal(10, 2) NULL DEFAULT NULL COMMENT '裂缝规模（单位平方米/车道公里）',
  `disease_repair_rate` decimal(10, 2) NULL DEFAULT NULL COMMENT '病害修补率',
  `crack_repair_rate` decimal(10, 2) NULL DEFAULT NULL COMMENT '裂缝修补率',
  `cracking_area` decimal(10, 2) NULL DEFAULT NULL COMMENT '龟裂面积',
  `block_crack_area` decimal(10, 2) NULL DEFAULT NULL COMMENT '块状裂缝面积',
  `portrait_crack_area` decimal(10, 2) NULL DEFAULT NULL COMMENT '纵向裂缝面积',
  `across_crack_area` decimal(10, 2) NULL DEFAULT NULL COMMENT '横向裂缝面积',
  `pit_area` decimal(10, 2) NULL DEFAULT NULL COMMENT '坑槽面积',
  `loose_area` decimal(10, 2) NULL DEFAULT NULL COMMENT '松散面积',
  `settlement_area` decimal(10, 2) NULL DEFAULT NULL COMMENT '沉陷面积',
  `car_withdrawal` decimal(10, 2) NULL DEFAULT NULL COMMENT '车撤面积',
  `wave_embracing_bag_area` decimal(10, 2) NULL DEFAULT NULL COMMENT '波浪拥包面积',
  `oil_flashing_area` decimal(10, 2) NULL DEFAULT NULL COMMENT '泛油面积',
  `pumping_area` decimal(10, 2) NULL DEFAULT NULL COMMENT '唧浆面积',
  `block_crack_repair_area` decimal(10, 2) NULL DEFAULT NULL COMMENT '块状裂缝修补面积',
  `across_crack_repair_area` decimal(10, 2) NULL DEFAULT NULL COMMENT '横向裂缝修补面积',
  `portrait_crack_repair_area` decimal(10, 2) NULL DEFAULT NULL COMMENT '纵向裂缝修补面积',
  `crack_area_subtotal` decimal(10, 2) NULL DEFAULT NULL COMMENT '裂缝类面积小计',
  `deformation_area_subtotal` decimal(10, 2) NULL DEFAULT NULL COMMENT '变形类面积小计',
  `loose_area_subtotal` decimal(10, 2) NULL DEFAULT NULL COMMENT '松散类面积小计',
  `other_area_subtotal` decimal(10, 2) NULL DEFAULT NULL COMMENT '其他类面积小计',
  `disease_area_total` decimal(10, 2) NULL DEFAULT NULL COMMENT '病害面积总计',
  `management_unit_id` bigint(20) NULL DEFAULT NULL COMMENT '管养单位id',
  `management_unit_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '管养单位名称',
  `legal_unit_id` bigint(20) NULL DEFAULT NULL COMMENT '法人单位id',
  `legal_unit_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '法人单位名称',
  `create_user` bigint(64) NULL DEFAULT NULL COMMENT '创建人',
  `create_dept` bigint(64) NULL DEFAULT NULL COMMENT '创建部门',
  `create_time` datetime(0) NULL DEFAULT NULL COMMENT '创建时间',
  `update_user` bigint(64) NULL DEFAULT NULL COMMENT '修改人',
  `update_time` datetime(0) NULL DEFAULT NULL COMMENT '修改时间',
  `status` int(2) NULL DEFAULT NULL COMMENT '状态',
  `is_deleted` int(2) NULL DEFAULT 0 COMMENT '是否已删除',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '路面定检评定表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of regular_unit_0227_to_li
-- ----------------------------
INSERT INTO `regular_unit_0227_to_li` VALUES (1848566642561384450, 1848561611699257346, 1505830070116270089, 'G1522', NULL, '2024-06-01', 94.45, 94.45, 96.19, 95.20, 93.39, 93.39, 99.34, 69.14, NULL, NULL, 150938, '2', 100.00, 100.00, 100.00, 98.01, 100.00, 100.00, 97.35, 1.33, NULL, NULL, 98.01, 98.01, 100.00, 98.01, 98.01, 100.00, 100.00, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 10009828, '绍兴管理中心', NULL, NULL, NULL, NULL, '2024-10-22 11:26:47', 1123598821738675201, '2024-10-22 12:00:42', 1, 0);
INSERT INTO `regular_unit_0227_to_li` VALUES (1848566780684009474, 1848561611699257346, 1505830070116270081, 'G15', NULL, '2024-06-01', 94.19, 94.19, 96.26, 95.58, 92.52, 92.52, 97.96, 68.59, NULL, NULL, 85594, '2', 100.00, 100.00, 98.73, 100.00, 97.73, 97.73, 92.99, 0.00, NULL, NULL, 96.46, 96.46, 98.73, 100.00, 96.46, 97.73, 97.73, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 10009615, '台州管理中心', NULL, NULL, NULL, NULL, '2024-10-22 11:27:20', 1123598821738675201, '2024-10-22 12:01:08', 1, 0);
INSERT INTO `regular_unit_0227_to_li` VALUES (1872455302145572866, 1872452338844377090, 1505830070116270081, 'G15', NULL, '2024-11-01', 94.16, 94.57, 95.71, 95.13, 91.29, 92.69, 100.00, 81.93, NULL, NULL, 170250, '1', 99.55, 100.00, 94.30, 100.00, 70.13, 91.36, 100.00, 17.42, NULL, NULL, 67.78, 86.07, 94.30, 100.00, 87.77, 70.13, 91.36, NULL, 17.26, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 10009615, '台州管理中心', NULL, NULL, 1123598821738675201, 10015083, '2024-12-27 09:31:47', 1123598821738675201, '2025-01-02 13:55:37', 1, 1);
INSERT INTO `regular_unit_0227_to_li` VALUES (1872455308114067457, 1872452338844377090, 1505830070116270089, 'G1522', NULL, '2024-11-01', 94.95, 95.20, 96.13, 95.94, 93.10, 93.92, 99.83, 77.67, NULL, NULL, 299870, '1', 98.00, 98.00, 97.67, 100.00, 93.33, 99.67, 99.33, 2.67, NULL, NULL, 92.00, 97.33, 97.67, 100.00, 96.86, 93.33, 99.67, NULL, 15.61, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 10009828, '绍兴管理中心', NULL, NULL, 1123598821738675201, 10015083, '2024-12-27 09:31:49', 1123598821738675201, '2025-01-02 13:57:22', 1, 1);
INSERT INTO `regular_unit_0227_to_li` VALUES (1874033758196932609, 1874033345653833730, 1505830070116270089, 'G1522', NULL, '2024-11-01', 93.72, 93.97, 96.13, 95.94, 93.10, 93.92, 99.83, 77.67, NULL, NULL, 299870, NULL, 98.00, 98.00, 97.67, 100.00, 93.33, 99.67, 99.33, 2.67, NULL, NULL, 92.00, 97.33, 97.67, 100.00, 98.00, 93.33, 99.67, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 10009828, '绍兴管理中心', NULL, NULL, NULL, NULL, '2024-12-31 18:04:00', 1123598821738675201, '2024-12-31 18:13:11', 1, 1);
INSERT INTO `regular_unit_0227_to_li` VALUES (1874033877898174465, 1874033345653833730, 1505830070116270081, 'G15', NULL, '2024-11-01', 93.36, 93.79, 95.71, 95.13, 91.29, 92.69, 100.00, 81.93, NULL, NULL, 170250, NULL, 99.55, 100.00, 94.30, 100.00, 70.13, 91.36, 100.00, 17.42, NULL, NULL, 67.78, 86.07, 94.30, 100.00, 91.95, 70.13, 91.36, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 10009615, '台州管理中心', NULL, NULL, NULL, NULL, '2024-12-31 18:04:29', 1123598821738675201, '2024-12-31 18:13:11', 1, 1);
INSERT INTO `regular_unit_0227_to_li` VALUES (1874629552294002689, 1874626517530255361, 1505830070116270081, 'G15', NULL, '2024-11-01', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '1', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 48.54, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 10009615, '台州管理中心', NULL, NULL, NULL, NULL, '2025-01-02 09:31:29', 1123598821738675201, '2025-01-02 09:56:14', 1, 1);
INSERT INTO `regular_unit_0227_to_li` VALUES (1874631882326343681, 1874626517530255361, 1505830070116270089, 'G1522', NULL, '2024-11-01', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '1', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 63.71, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 10009828, '绍兴管理中心', NULL, NULL, NULL, NULL, '2025-01-02 09:40:44', 1123598821738675201, '2025-01-02 09:56:14', 1, 1);
INSERT INTO `regular_unit_0227_to_li` VALUES (1874701939983187970, 1874700514833932290, 1505830070116270089, 'G1522', NULL, '2024-11-01', 94.95, 95.20, 96.13, 95.94, 93.10, 93.92, 99.83, 77.67, NULL, NULL, 299870, '1', 100.00, 100.00, 97.67, 100.00, 93.33, 99.67, 99.33, 2.67, NULL, NULL, 92.00, 97.33, 97.67, 100.00, 100.00, 93.33, 99.67, NULL, 15.61, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 204.67, 0.00, 2.72, 4559.73, NULL, 10009828, '绍兴管理中心', NULL, NULL, NULL, NULL, '2025-01-02 14:19:07', 1123598821738675201, '2025-01-09 17:24:21', 1, 0);
INSERT INTO `regular_unit_0227_to_li` VALUES (1874702074309967874, 1874700514833932290, 1505830070116270081, 'G15', NULL, '2024-11-01', 94.16, 94.57, 95.71, 95.13, 91.29, 92.69, 100.00, 81.93, NULL, NULL, 170250, '1', 99.58, 100.00, 94.30, 100.00, 70.13, 91.36, 100.00, 17.42, NULL, NULL, 67.78, 86.07, 94.30, 100.00, 99.58, 70.13, 91.36, NULL, 17.26, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 140.89, 0.00, 1.49, 2811.83, NULL, 10009615, '台州管理中心', NULL, NULL, NULL, NULL, '2025-01-02 14:19:39', 1123598821738675201, '2025-01-09 17:24:20', 1, 0);

SET FOREIGN_KEY_CHECKS = 1;
