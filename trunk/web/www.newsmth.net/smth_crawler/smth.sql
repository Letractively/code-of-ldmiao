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
  `auto_increment_id` int(11) NOT NULL auto_increment COMMENT 'ϵͳ����ID��',
  `article_md5` char(60) NOT NULL default '' COMMENT '����MD5ֵ',
  `thread_md5` char(60) default NULL COMMENT '��������MD5',
  `reply_md5` char(60) default NULL COMMENT 'Re��MD5',
  `article_id` int(11) default NULL COMMENT '����ID��',
  `board_id` int(11) default NULL COMMENT '����ID��',
  `thread_id` int(11) default NULL COMMENT '��������ID��',
  `reply_id` int(11) default NULL COMMENT 'Re��ID��',
  `system_id` int(11) default NULL COMMENT 'ϵͳID��',
  `user_name` varchar(255) default NULL COMMENT '�û�Ӣ��ID',
  `user_nick_name` varchar(255) default NULL COMMENT '�û���������ʱ���ǳ�',
  `user_signature` text COMMENT '�û�ǩ����',
  `url` varchar(255) default NULL COMMENT '��������',
  `title` varchar(255) default NULL COMMENT '���±���',
  `content` longtext COMMENT '����ȫ������',
  `content_text` longtext COMMENT '��������',
  `pub_time` datetime default NULL COMMENT '���·���ʱ��',
  `from_ip` varchar(50) default NULL COMMENT '�û�������ʱ��IP��ַ',
  `word_count` int(11) default '0' COMMENT '��������',
  `unknown_num1` int(11) default '0' COMMENT 'δ֪����1',
  `unknown_num2` int(11) default '0' COMMENT 'δ֪����2',
  `html` longtext COMMENT '���µ�HTMLԴ��',
  PRIMARY KEY  (`auto_increment_id`),
  UNIQUE KEY `article_md5` (`article_md5`),
  KEY `user_name` (`user_name`),
  KEY `pub_time` (`pub_time`),
  KEY `board_id` (`board_id`),
  KEY `thread_id` (`thread_id`),
  KEY `article_id` (`article_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='����';

-- --------------------------------------------------------

-- 
-- Table structure for table `board`
-- 

DROP TABLE IF EXISTS `board`;
CREATE TABLE IF NOT EXISTS `board` (
  `auto_increment_id` int(11) NOT NULL auto_increment COMMENT 'ϵͳ����ID��',
  `id` int(11) NOT NULL COMMENT '����ID��',
  `name` varchar(100) default NULL COMMENT '����Ӣ������',
  `chn_name` varchar(255) default NULL COMMENT '������������',
  `description` text COMMENT '��������',
  `last_update_time` datetime default NULL COMMENT '�������ʱ��',
  `update_num` int(11) NOT NULL default '0' COMMENT '�����������',
  PRIMARY KEY  (`auto_increment_id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='����';

-- --------------------------------------------------------

-- 
-- Table structure for table `board_update_history`
-- 

DROP TABLE IF EXISTS `board_update_history`;
CREATE TABLE IF NOT EXISTS `board_update_history` (
  `auto_increment_id` int(11) NOT NULL auto_increment COMMENT 'ϵͳ����ID��',
  `id` int(11) NOT NULL COMMENT '����ID��',
  `name` varchar(100) default NULL COMMENT '����Ӣ������',
  `last_update_time` datetime default NULL COMMENT '����ʱ��',
  `update_num` int(11) NOT NULL default '0' COMMENT '��������',
  PRIMARY KEY  (`auto_increment_id`),
  KEY `id` (`id`),
  KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='���������ʷ';

-- --------------------------------------------------------

-- 
-- Table structure for table `user`
-- 

DROP TABLE IF EXISTS `user`;
CREATE TABLE IF NOT EXISTS `user` (
  `id` int(10) unsigned NOT NULL auto_increment COMMENT '�û�ID���',
  `user_name` varchar(255) default NULL COMMENT '�û�Ӣ����',
  `nick_name` varchar(255) default NULL COMMENT '�û���ǰ�ǳ�',
  PRIMARY KEY  (`id`),
  UNIQUE KEY `user_name` (`user_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='�û�';
