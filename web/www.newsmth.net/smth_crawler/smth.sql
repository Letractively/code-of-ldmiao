-- phpMyAdmin SQL Dump
-- version 2.10.3
-- http://www.phpmyadmin.net
-- 
-- Host: localhost
-- Generation Time: Mar 05, 2008 at 04:40 AM
-- Server version: 5.0.24
-- PHP Version: 5.2.3

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";

-- 
-- Database: `smth`
-- 

-- --------------------------------------------------------

-- 
-- Table structure for table `article`
-- 

DROP TABLE IF EXISTS `article`;
CREATE TABLE IF NOT EXISTS `article` (
  `auto_increment_id` int(11) NOT NULL auto_increment COMMENT '系统自增ID号',
  `article_md5` char(60) NOT NULL default '' COMMENT '文章MD5值',
  `thread_md5` char(60) default NULL COMMENT '文章主题MD5',
  `reply_md5` char(60) default NULL COMMENT 'Re帖MD5',
  `article_id` int(11) default NULL COMMENT '文章ID号',
  `board_id` int(11) default NULL COMMENT '版面ID号',
  `thread_id` int(11) default NULL COMMENT '文章主题ID号',
  `reply_id` int(11) default NULL COMMENT 'Re帖ID号',
  `system_id` int(11) default NULL COMMENT '系统ID号',
  `user_name` varchar(255) default NULL COMMENT '用户英文ID',
  `user_nick_name` varchar(255) default NULL COMMENT '用户发表文章时的昵称',
  `user_signature` text COMMENT '用户签名档',
  `url` varchar(255) default NULL COMMENT '文章链接',
  `title` varchar(255) default NULL COMMENT '文章标题',
  `content` longtext COMMENT '文章全文内容',
  `content_text` longtext COMMENT '文章正文',
  `pub_time` datetime default NULL COMMENT '文章发表时间',
  `from_ip` varchar(50) default NULL COMMENT '用户发文章时的IP地址',
  `word_count` int(11) default '0' COMMENT '文章字数',
  `unknown_num1` int(11) default '0' COMMENT '未知数字1',
  `unknown_num2` int(11) default '0' COMMENT '未知数字2',
  `html` longtext COMMENT '文章的HTML源码',
  PRIMARY KEY  (`auto_increment_id`),
  UNIQUE KEY `article_md5` (`article_md5`),
  KEY `user_name` (`user_name`),
  KEY `pub_time` (`pub_time`),
  KEY `board_id` (`board_id`),
  KEY `thread_id` (`thread_id`),
  KEY `article_id` (`article_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='文章';

-- --------------------------------------------------------

-- 
-- Table structure for table `board`
-- 

DROP TABLE IF EXISTS `board`;
CREATE TABLE IF NOT EXISTS `board` (
  `auto_increment_id` int(11) NOT NULL auto_increment COMMENT '系统自增ID号',
  `id` int(11) NOT NULL COMMENT '版面ID号',
  `name` varchar(100) default NULL COMMENT '版面英文名称',
  `chn_name` varchar(255) default NULL COMMENT '版面中文名称',
  `description` text COMMENT '版面描述',
  `last_update_time` datetime default NULL COMMENT '最近更新时间',
  `update_num` int(11) NOT NULL default '0' COMMENT '最近更新数量',
  PRIMARY KEY  (`auto_increment_id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='版面';

-- --------------------------------------------------------

-- 
-- Table structure for table `board_update_history`
-- 

DROP TABLE IF EXISTS `board_update_history`;
CREATE TABLE IF NOT EXISTS `board_update_history` (
  `auto_increment_id` int(11) NOT NULL auto_increment COMMENT '系统自增ID号',
  `id` int(11) NOT NULL COMMENT '版面ID号',
  `name` varchar(100) default NULL COMMENT '版面英文名称',
  `last_update_time` datetime default NULL COMMENT '更新时间',
  `update_num` int(11) NOT NULL default '0' COMMENT '更新数量',
  PRIMARY KEY  (`auto_increment_id`),
  KEY `id` (`id`),
  KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='版面更新历史';

-- --------------------------------------------------------

-- 
-- Table structure for table `user`
-- 

DROP TABLE IF EXISTS `user`;
CREATE TABLE IF NOT EXISTS `user` (
  `id` int(10) unsigned NOT NULL auto_increment COMMENT '用户ID序号',
  `user_name` varchar(255) default NULL COMMENT '用户英文名',
  `nick_name` varchar(255) default NULL COMMENT '用户当前昵称',
  PRIMARY KEY  (`id`),
  UNIQUE KEY `user_name` (`user_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='用户';
