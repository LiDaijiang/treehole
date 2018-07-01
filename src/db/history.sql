create database treehole_material;
CREATE TABLE `secret_material` (
`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
`secret` varchar(4096) CHARACTER SET utf8 NOT NULL DEFAULT '' COMMENT '秘密',
`outside_id` int(11) unsigned NOT NULL COMMENT '外部网站id',
PRIMARY KEY (`id`))
ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
CREATE TABLE `soul_soup` (
`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
`answer` varchar(4096) CHARACTER SET utf8 NOT NULL DEFAULT '' COMMENT '鸡汤回答',
`tag1` int(11) unsigned NOT NULL COMMENT '标签id1',
`tag2` int(11) unsigned NOT NULL COMMENT '标签id2',
`tag3` int(11) unsigned NOT NULL COMMENT '标签id3',
`tag4` int(11) unsigned NOT NULL COMMENT '标签id4',
`tag5` int(11) unsigned NOT NULL COMMENT '标签id5',
PRIMARY KEY (`id`))
ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
CREATE TABLE `soul_soup_tag` (
`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
`tag_name` varchar(4096) CHARACTER SET utf8 NOT NULL DEFAULT '' COMMENT '标签名',
PRIMARY KEY (`id`))
ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
CREATE TABLE `secret_record` (
`id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
`msg_file_id` varchar(128) CHARACTER NOT NULL DEFAULT '' COMMENT '录音未见id',
`xiaomi_id` int(11) unsigned NOT NULL DEFAULT 0 COMMENT '小米id',
`session_id` varchar(128) unsigned NOT NULL DEFAULT '' COMMENT '会话id',
PRIMARY KEY (`id`))
ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;