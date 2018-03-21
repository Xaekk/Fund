/*
SQLyog Ultimate v11.25 (64 bit)
MySQL - 5.0.96-community-nt : Database - fund
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`fund` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `fund`;

/*Table structure for table `dailyrate` */

DROP TABLE IF EXISTS `dailyrate`;

CREATE TABLE `dailyrate` (
  `id` int(255) NOT NULL auto_increment,
  `code` varchar(255) default NULL,
  `date` date default NULL,
  `rate` decimal(65,30) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1169 DEFAULT CHARSET=utf8;

/*Table structure for table `redeem` */

DROP TABLE IF EXISTS `redeem`;

CREATE TABLE `redeem` (
  `id` int(255) NOT NULL auto_increment,
  `code` varchar(255) default NULL,
  `fee` decimal(65,30) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=107981 DEFAULT CHARSET=utf8;

/*Table structure for table `unsupport` */

DROP TABLE IF EXISTS `unsupport`;

CREATE TABLE `unsupport` (
  `id` int(255) NOT NULL auto_increment,
  `code` varchar(255) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
