-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: localhost    Database: stocks
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `audit_logs`
--

DROP TABLE IF EXISTS `audit_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audit_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `action` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `table_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `record_id` int DEFAULT NULL,
  `old_values` json DEFAULT NULL,
  `new_values` json DEFAULT NULL,
  `action_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `ip_address` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `idx_action_date` (`action_date`),
  CONSTRAINT `audit_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `audit_logs`
--

LOCK TABLES `audit_logs` WRITE;
/*!40000 ALTER TABLE `audit_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `audit_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `authorized_devices`
--

DROP TABLE IF EXISTS `authorized_devices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `authorized_devices` (
  `id` int NOT NULL AUTO_INCREMENT,
  `device_id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `device_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `mac_address` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `store_id` int DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `registered_by` int DEFAULT NULL,
  `registered_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `last_used` timestamp NULL DEFAULT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_device_user` (`device_id`,`user_id`),
  KEY `user_id` (`user_id`),
  KEY `registered_by` (`registered_by`),
  KEY `idx_device_id` (`device_id`),
  KEY `idx_store_user` (`store_id`,`user_id`),
  KEY `idx_active` (`is_active`),
  CONSTRAINT `authorized_devices_ibfk_1` FOREIGN KEY (`store_id`) REFERENCES `stores` (`id`),
  CONSTRAINT `authorized_devices_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `authorized_devices_ibfk_3` FOREIGN KEY (`registered_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `authorized_devices`
--

LOCK TABLES `authorized_devices` WRITE;
/*!40000 ALTER TABLE `authorized_devices` DISABLE KEYS */;
INSERT INTO `authorized_devices` VALUES (17,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','f9:e7:9c:72:c9:25',NULL,1,1,1,'2026-02-09 07:16:03','2026-02-13 11:39:48','تسجيل تلقائي - admin'),(18,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','f9:e7:9c:72:c9:25',2,2,1,1,'2026-02-09 07:16:34','2026-02-14 01:02:25',''),(19,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','f9:e7:9c:72:c9:25',2,5,1,1,'2026-02-09 07:16:56','2026-02-13 11:11:17',''),(20,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','f9:e7:9c:72:c9:25',NULL,13,1,13,'2026-02-09 08:29:22',NULL,'تسجيل تلقائي للمطور');
/*!40000 ALTER TABLE `authorized_devices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `category_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'مواد غذائية','منتجات البقالة الأساسية',1,'2026-01-21 11:22:02'),(2,'مشروبات','مشروبات غازية، عصائر، مياه',1,'2026-01-21 11:22:02'),(3,'عناية شخصية','شامبو، صابون، معجون أسنان',1,'2026-01-21 11:22:02'),(4,'منظفات منزلية','مساحيق غسيل، منظفات أسطح',1,'2026-01-21 11:22:02'),(5,'سناكس وحلويات','شيبسي، بسكويت، شوكولاتة',1,'2026-01-21 11:22:02'),(6,'منتجات ألبان','حليب، زبادي، أجبان',1,'2026-01-21 11:22:02'),(7,'لحوم ومجمدات','لحوم بقرية، دواجن، خضروات مجمدة',1,'2026-01-21 11:22:02'),(8,'مخبوزات','خبز، كيك، معجنات',1,'2026-01-21 11:22:02'),(9,'إلكترونيات','ملحقات موبايل، بطاريات، سماعات',1,'2026-01-21 11:22:02'),(10,'خضروات وفواكه','منتجات طازجة',1,'2026-01-21 11:22:02');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `drawer_closing_details`
--

DROP TABLE IF EXISTS `drawer_closing_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `drawer_closing_details` (
  `id` int NOT NULL AUTO_INCREMENT,
  `drawer_log_id` int NOT NULL,
  `denomination` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `quantity` int NOT NULL,
  `total_amount` decimal(12,2) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `drawer_log_id` (`drawer_log_id`),
  CONSTRAINT `drawer_closing_details_ibfk_1` FOREIGN KEY (`drawer_log_id`) REFERENCES `drawer_logs` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `drawer_closing_details`
--

LOCK TABLES `drawer_closing_details` WRITE;
/*!40000 ALTER TABLE `drawer_closing_details` DISABLE KEYS */;
INSERT INTO `drawer_closing_details` VALUES (1,1,'200',10,2000.00,'2026-01-21 22:27:13'),(2,2,'200',6,1200.00,'2026-01-22 00:15:42'),(3,3,'200',20,4000.00,'2026-01-22 10:29:14'),(4,4,'1',32,32.00,'2026-01-31 16:33:26'),(5,6,'10',3,30.00,'2026-01-31 17:49:34'),(6,6,'1',2,2.00,'2026-01-31 17:49:34'),(7,8,'200',1,200.00,'2026-01-31 18:28:08'),(8,8,'20',2,40.00,'2026-01-31 18:28:08'),(9,8,'10',1,10.00,'2026-01-31 18:28:08'),(10,8,'1',2,2.00,'2026-01-31 18:28:08'),(11,8,'0.5',1,0.50,'2026-01-31 18:28:08'),(12,15,'1ج',3500,3500.00,'2026-02-12 08:49:26'),(13,15,'Visa',1,100.00,'2026-02-12 08:49:26');
/*!40000 ALTER TABLE `drawer_closing_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `drawer_logs`
--

DROP TABLE IF EXISTS `drawer_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `drawer_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `store_id` int NOT NULL,
  `cashier_id` int NOT NULL,
  `opening_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `opening_balance` decimal(12,2) DEFAULT '0.00',
  `closing_date` datetime DEFAULT NULL,
  `closing_balance` decimal(12,2) DEFAULT NULL,
  `status` enum('Open','Closed') COLLATE utf8mb4_unicode_ci DEFAULT 'Open',
  `notes` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `store_id` (`store_id`),
  KEY `cashier_id` (`cashier_id`),
  KEY `idx_drawer_status` (`status`),
  CONSTRAINT `drawer_logs_ibfk_1` FOREIGN KEY (`store_id`) REFERENCES `stores` (`id`),
  CONSTRAINT `drawer_logs_ibfk_2` FOREIGN KEY (`cashier_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `drawer_logs`
--

LOCK TABLES `drawer_logs` WRITE;
/*!40000 ALTER TABLE `drawer_logs` DISABLE KEYS */;
INSERT INTO `drawer_logs` VALUES (1,2,2,'2026-01-21 11:34:33',1000.00,'2026-01-22 00:27:13',2000.00,'Closed',NULL,'2026-01-21 11:34:33','2026-01-21 22:27:13'),(2,1,1,'2026-01-21 21:58:34',1000.00,'2026-01-22 02:15:42',1200.00,'Closed',NULL,'2026-01-21 21:58:34','2026-01-22 00:15:42'),(3,2,2,'2026-01-22 10:24:43',1000.00,'2026-01-22 12:29:14',4000.00,'Closed',NULL,'2026-01-22 10:24:43','2026-01-22 10:29:14'),(4,4,1,'2026-01-31 16:17:10',0.00,'2026-01-31 18:33:26',32.00,'Closed',NULL,'2026-01-31 16:17:10','2026-01-31 16:33:26'),(5,3,3,'2026-01-31 16:20:27',0.00,'2026-01-31 18:30:28',0.00,'Closed',NULL,'2026-01-31 16:20:27','2026-01-31 16:30:28'),(6,2,2,'2026-01-31 16:54:56',0.00,'2026-01-31 19:49:34',32.00,'Closed',NULL,'2026-01-31 16:54:56','2026-01-31 17:49:34'),(7,2,2,'2026-01-31 17:53:33',0.00,'2026-01-31 19:54:30',0.00,'Closed',NULL,'2026-01-31 17:53:33','2026-01-31 17:54:30'),(8,2,2,'2026-01-31 18:14:23',0.00,'2026-01-31 20:28:08',252.50,'Closed',NULL,'2026-01-31 18:14:23','2026-01-31 18:28:08'),(9,2,2,'2026-02-01 17:19:46',0.00,'2026-02-01 19:22:29',0.00,'Closed',NULL,'2026-02-01 17:19:46','2026-02-01 17:22:29'),(10,2,2,'2026-02-01 17:23:13',0.00,'2026-02-01 19:23:25',0.00,'Closed',NULL,'2026-02-01 17:23:13','2026-02-01 17:23:25'),(11,2,2,'2026-02-02 17:01:20',0.00,'2026-02-02 19:12:58',0.00,'Closed',NULL,'2026-02-02 17:01:20','2026-02-02 17:12:58'),(12,2,5,'2026-02-02 17:03:40',0.00,'2026-02-02 19:12:09',0.00,'Closed',NULL,'2026-02-02 17:03:40','2026-02-02 17:12:09'),(13,2,5,'2026-02-02 17:18:46',0.00,'2026-02-02 19:19:06',0.00,'Closed',NULL,'2026-02-02 17:18:46','2026-02-02 17:19:06'),(14,2,2,'2026-02-02 17:22:00',0.00,'2026-02-08 12:04:43',10000.00,'Closed',NULL,'2026-02-02 17:22:00','2026-02-08 10:04:43'),(15,2,5,'2026-02-08 10:06:29',0.00,'2026-02-12 10:49:25',3500.00,'Closed',NULL,'2026-02-08 10:06:29','2026-02-12 08:49:25'),(16,2,5,'2026-02-12 10:32:49',0.00,NULL,NULL,'Open',NULL,'2026-02-12 10:32:49','2026-02-12 10:32:49');
/*!40000 ALTER TABLE `drawer_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `expenses`
--

DROP TABLE IF EXISTS `expenses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `expenses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `store_id` int NOT NULL,
  `user_id` int NOT NULL,
  `expense_type` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_personal` tinyint(1) DEFAULT '0',
  `amount` decimal(10,2) NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `expense_date` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `store_id` (`store_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `expenses_ibfk_1` FOREIGN KEY (`store_id`) REFERENCES `stores` (`id`),
  CONSTRAINT `expenses_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `expenses`
--

LOCK TABLES `expenses` WRITE;
/*!40000 ALTER TABLE `expenses` DISABLE KEYS */;
INSERT INTO `expenses` VALUES (4,2,1,'كهرباء',0,1000.00,'كهرباء شهر واحد لفرع الاسكندرية','2026-02-09 06:58:33'),(5,2,1,'شخصي',1,500.00,'البيت','2026-02-09 09:24:41'),(7,2,1,'إيجار',0,500.00,'','2026-02-12 11:02:14');
/*!40000 ALTER TABLE `expenses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `invoice_items`
--

DROP TABLE IF EXISTS `invoice_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoice_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `invoice_id` int NOT NULL,
  `product_id` int NOT NULL,
  `quantity` int NOT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  `discount` decimal(10,2) DEFAULT '0.00',
  `total_price` decimal(12,2) NOT NULL,
  `notes` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `invoice_id` (`invoice_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `invoice_items_ibfk_1` FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`id`) ON DELETE CASCADE,
  CONSTRAINT `invoice_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=202 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoice_items`
--

LOCK TABLES `invoice_items` WRITE;
/*!40000 ALTER TABLE `invoice_items` DISABLE KEYS */;
INSERT INTO `invoice_items` VALUES (1,1,9,1,30.00,0.00,30.00,NULL,'2026-01-21 11:54:58'),(2,1,22,1,18.00,0.00,18.00,NULL,'2026-01-21 11:54:58'),(3,2,3,1,11.00,0.00,11.00,NULL,'2026-01-21 12:30:41'),(4,2,2,1,28.00,0.00,28.00,NULL,'2026-01-21 12:30:41'),(5,2,7,1,22.00,0.00,22.00,NULL,'2026-01-21 12:30:41'),(6,2,5,1,58.00,0.00,58.00,NULL,'2026-01-21 12:30:41'),(7,3,1,1,32.00,0.00,32.00,NULL,'2026-01-21 13:22:41'),(8,3,2,1,28.00,0.00,28.00,NULL,'2026-01-21 13:22:41'),(9,3,3,1,11.00,0.00,11.00,NULL,'2026-01-21 13:22:41'),(10,3,5,2,58.00,0.00,116.00,NULL,'2026-01-21 13:22:41'),(11,4,1,2,32.00,0.00,64.00,NULL,'2026-01-21 13:23:08'),(12,4,6,1,24.00,0.00,24.00,NULL,'2026-01-21 13:23:08'),(13,4,20,1,48.00,0.00,48.00,NULL,'2026-01-21 13:23:08'),(14,4,17,1,35.00,0.00,35.00,NULL,'2026-01-21 13:23:08'),(15,4,22,1,18.00,0.00,18.00,NULL,'2026-01-21 13:23:08'),(16,4,21,1,38.00,0.00,38.00,NULL,'2026-01-21 13:23:08'),(17,4,35,1,25.00,0.00,25.00,NULL,'2026-01-21 13:23:08'),(18,5,9,1,30.00,0.00,30.00,NULL,'2026-01-21 13:23:46'),(19,5,22,1,18.00,0.00,18.00,NULL,'2026-01-21 13:23:46'),(20,6,6,1,24.00,0.00,24.00,NULL,'2026-01-21 22:09:02'),(21,6,1,1,32.00,0.00,32.00,NULL,'2026-01-21 22:09:02'),(22,6,20,1,48.00,0.00,48.00,NULL,'2026-01-21 22:09:02'),(23,6,17,1,35.00,0.00,35.00,NULL,'2026-01-21 22:09:02'),(24,6,22,1,18.00,0.00,18.00,NULL,'2026-01-21 22:09:02'),(25,6,21,1,38.00,0.00,38.00,NULL,'2026-01-21 22:09:02'),(26,6,31,1,65.00,0.00,65.00,NULL,'2026-01-21 22:09:02'),(27,6,26,1,5.00,0.00,5.00,NULL,'2026-01-21 22:09:02'),(28,6,35,1,25.00,0.00,25.00,NULL,'2026-01-21 22:09:02'),(29,7,1,1,32.00,0.00,32.00,NULL,'2026-01-21 22:26:13'),(30,7,17,1,35.00,0.00,35.00,NULL,'2026-01-21 22:26:13'),(31,7,6,1,24.00,0.00,24.00,NULL,'2026-01-21 22:26:13'),(32,7,20,1,48.00,0.00,48.00,NULL,'2026-01-21 22:26:13'),(33,8,1,1,32.00,0.00,32.00,NULL,'2026-01-22 00:14:40'),(34,8,2,1,28.00,0.00,28.00,NULL,'2026-01-22 00:14:40'),(35,9,3,1,11.00,0.00,11.00,NULL,'2026-01-22 10:25:49'),(36,10,1,1,32.00,0.00,32.00,NULL,'2026-01-22 10:28:33'),(37,10,2,1,28.00,0.00,28.00,NULL,'2026-01-22 10:28:33'),(38,10,9,1,30.00,0.00,30.00,NULL,'2026-01-22 10:28:33'),(39,10,5,1,58.00,0.00,58.00,NULL,'2026-01-22 10:28:33'),(40,11,2,1,28.00,0.00,28.00,NULL,'2026-01-31 16:22:16'),(41,11,1,1,32.00,0.00,32.00,NULL,'2026-01-31 16:22:16'),(42,12,1,1,32.00,0.00,32.00,NULL,'2026-01-31 16:32:29'),(43,13,1,1,32.00,0.00,32.00,NULL,'2026-01-31 17:48:38'),(44,14,1,1,32.00,0.00,32.00,NULL,'2026-01-31 18:19:10'),(45,14,2,1,28.00,0.00,28.00,NULL,'2026-01-31 18:19:10'),(46,14,3,1,11.00,0.00,11.00,NULL,'2026-01-31 18:19:10'),(47,14,4,1,68.00,0.00,68.00,NULL,'2026-01-31 18:19:10'),(48,14,5,1,58.00,0.00,58.00,NULL,'2026-01-31 18:19:10'),(49,14,6,1,24.00,0.00,24.00,NULL,'2026-01-31 18:19:10'),(50,14,7,1,22.00,0.00,22.00,NULL,'2026-01-31 18:19:10'),(51,14,8,1,52.00,0.00,52.00,NULL,'2026-01-31 18:19:10'),(52,14,20,1,48.00,0.00,48.00,NULL,'2026-01-31 18:19:10'),(53,14,21,1,38.00,0.00,38.00,NULL,'2026-01-31 18:19:10'),(54,14,22,1,18.00,0.00,18.00,NULL,'2026-01-31 18:19:10'),(55,14,23,1,55.00,0.00,55.00,NULL,'2026-01-31 18:19:10'),(56,14,24,1,22.00,0.00,22.00,NULL,'2026-01-31 18:19:10'),(57,15,1,1,32.00,0.00,32.00,NULL,'2026-02-03 16:59:27'),(58,15,2,1,28.00,0.00,28.00,NULL,'2026-02-03 16:59:27'),(59,15,3,1,11.00,0.00,11.00,NULL,'2026-02-03 16:59:27'),(60,15,4,1,68.00,0.00,68.00,NULL,'2026-02-03 16:59:27'),(61,16,1,10,32.00,0.00,320.00,NULL,'2026-02-05 05:50:18'),(62,16,2,10,28.00,0.00,280.00,NULL,'2026-02-05 05:50:18'),(63,16,3,10,11.00,0.00,110.00,NULL,'2026-02-05 05:50:18'),(64,16,4,10,68.00,0.00,680.00,NULL,'2026-02-05 05:50:18'),(65,16,5,10,58.00,0.00,580.00,NULL,'2026-02-05 05:50:18'),(66,16,6,10,24.00,0.00,240.00,NULL,'2026-02-05 05:50:18'),(67,16,7,10,22.00,0.00,220.00,NULL,'2026-02-05 05:50:18'),(68,16,8,10,52.00,0.00,520.00,NULL,'2026-02-05 05:50:18'),(69,16,20,20,48.00,0.00,960.00,NULL,'2026-02-05 05:50:18'),(70,16,21,10,38.00,0.00,380.00,NULL,'2026-02-05 05:50:18'),(71,16,22,10,18.00,0.00,180.00,NULL,'2026-02-05 05:50:18'),(72,16,23,10,55.00,0.00,550.00,NULL,'2026-02-05 05:50:18'),(73,16,24,10,22.00,0.00,220.00,NULL,'2026-02-05 05:50:18'),(74,16,30,10,45.00,0.00,450.00,NULL,'2026-02-05 05:50:18'),(75,16,31,10,65.00,0.00,650.00,NULL,'2026-02-05 05:50:18'),(76,16,32,20,15.00,0.00,300.00,NULL,'2026-02-05 05:50:18'),(77,16,9,10,30.00,0.00,300.00,NULL,'2026-02-05 05:50:18'),(78,16,10,10,7.00,0.00,70.00,NULL,'2026-02-05 05:50:18'),(79,16,11,10,24.00,0.00,240.00,NULL,'2026-02-05 05:50:18'),(80,16,12,10,6.00,0.00,60.00,NULL,'2026-02-05 05:50:18'),(81,16,13,10,40.00,0.00,400.00,NULL,'2026-02-05 05:50:18'),(82,16,14,10,18.00,0.00,180.00,NULL,'2026-02-05 05:50:18'),(83,17,1,1,32.00,0.00,32.00,NULL,'2026-02-05 06:37:02'),(84,17,2,1,28.00,0.00,28.00,NULL,'2026-02-05 06:37:02'),(85,17,3,1,11.00,0.00,11.00,NULL,'2026-02-05 06:37:02'),(86,17,4,1,68.00,0.00,68.00,NULL,'2026-02-05 06:37:02'),(87,17,5,1,58.00,0.00,58.00,NULL,'2026-02-05 06:37:02'),(88,17,6,1,24.00,0.00,24.00,NULL,'2026-02-05 06:37:02'),(89,17,7,1,22.00,0.00,22.00,NULL,'2026-02-05 06:37:02'),(90,17,8,1,52.00,0.00,52.00,NULL,'2026-02-05 06:37:02'),(91,18,128,1,10.00,0.00,10.00,NULL,'2026-02-05 06:47:39'),(92,18,1,1,32.00,0.00,32.00,NULL,'2026-02-05 06:47:39'),(93,18,2,1,28.00,0.00,28.00,NULL,'2026-02-05 06:47:39'),(94,19,1,5,32.00,0.00,160.00,NULL,'2026-02-07 19:07:01'),(95,19,2,1,28.00,0.00,28.00,NULL,'2026-02-07 19:07:01'),(96,19,3,1,11.00,0.00,11.00,NULL,'2026-02-07 19:07:01'),(97,19,4,1,68.00,0.00,68.00,NULL,'2026-02-07 19:07:01'),(98,20,1,1,32.00,0.00,32.00,NULL,'2026-02-11 09:37:36'),(99,21,1,1,32.00,0.00,32.00,NULL,'2026-02-11 22:07:33'),(100,22,1,1,32.00,0.00,32.00,NULL,'2026-02-12 08:17:26'),(101,22,2,1,28.00,0.00,28.00,NULL,'2026-02-12 08:17:26'),(102,22,3,1,11.00,0.00,11.00,NULL,'2026-02-12 08:17:26'),(103,22,4,1,68.00,0.00,68.00,NULL,'2026-02-12 08:17:26'),(104,22,5,1,58.00,0.00,58.00,NULL,'2026-02-12 08:17:26'),(105,22,6,1,24.00,0.00,24.00,NULL,'2026-02-12 08:17:26'),(106,22,7,1,22.00,0.00,22.00,NULL,'2026-02-12 08:17:26'),(107,22,8,1,52.00,0.00,52.00,NULL,'2026-02-12 08:17:26'),(108,23,1,10,32.00,0.00,320.00,NULL,'2026-02-12 08:26:01'),(109,23,2,2,28.00,0.00,56.00,NULL,'2026-02-12 08:26:01'),(110,23,3,10,11.00,0.00,110.00,NULL,'2026-02-12 08:26:01'),(111,23,4,1,68.00,0.00,68.00,NULL,'2026-02-12 08:26:01'),(112,23,5,1,58.00,0.00,58.00,NULL,'2026-02-12 08:26:01'),(113,23,6,1,24.00,0.00,24.00,NULL,'2026-02-12 08:26:01'),(114,23,7,3,22.00,0.00,66.00,NULL,'2026-02-12 08:26:01'),(115,23,8,1,52.00,0.00,52.00,NULL,'2026-02-12 08:26:01'),(116,23,37,4,15.00,0.00,60.00,NULL,'2026-02-12 08:26:02'),(117,23,33,1,18.00,0.00,18.00,NULL,'2026-02-12 08:26:02'),(118,23,34,1,22.00,0.00,22.00,NULL,'2026-02-12 08:26:02'),(119,23,35,1,25.00,0.00,25.00,NULL,'2026-02-12 08:26:02'),(120,23,36,1,20.00,0.00,20.00,NULL,'2026-02-12 08:26:02'),(121,23,20,1,48.00,0.00,48.00,NULL,'2026-02-12 08:26:02'),(122,23,21,1,38.00,0.00,38.00,NULL,'2026-02-12 08:26:02'),(123,23,22,1,18.00,0.00,18.00,NULL,'2026-02-12 08:26:02'),(124,23,23,1,55.00,0.00,55.00,NULL,'2026-02-12 08:26:02'),(125,23,24,1,22.00,0.00,22.00,NULL,'2026-02-12 08:26:02'),(126,23,30,2,45.00,0.00,90.00,NULL,'2026-02-12 08:26:02'),(127,23,31,1,65.00,0.00,65.00,NULL,'2026-02-12 08:26:02'),(128,23,32,1,15.00,0.00,15.00,NULL,'2026-02-12 08:26:02'),(129,23,15,1,85.00,0.00,85.00,NULL,'2026-02-12 08:26:02'),(130,23,16,1,30.00,0.00,30.00,NULL,'2026-02-12 08:26:02'),(131,23,17,1,35.00,0.00,35.00,NULL,'2026-02-12 08:26:02'),(132,23,18,2,25.00,0.00,50.00,NULL,'2026-02-12 08:26:02'),(133,23,19,1,75.00,0.00,75.00,NULL,'2026-02-12 08:26:02'),(134,24,1,1,32.00,0.00,32.00,NULL,'2026-02-12 08:35:28'),(135,24,2,1,28.00,0.00,28.00,NULL,'2026-02-12 08:35:28'),(136,24,3,1,11.00,0.00,11.00,NULL,'2026-02-12 08:35:28'),(137,24,4,1,68.00,0.00,68.00,NULL,'2026-02-12 08:35:29'),(138,24,5,2,58.00,0.00,116.00,NULL,'2026-02-12 08:35:29'),(139,24,6,1,24.00,0.00,24.00,NULL,'2026-02-12 08:35:29'),(140,24,7,2,22.00,0.00,44.00,NULL,'2026-02-12 08:35:29'),(141,24,8,1,52.00,0.00,52.00,NULL,'2026-02-12 08:35:29'),(142,24,72,1,17.50,0.00,17.50,NULL,'2026-02-12 08:35:29'),(143,24,83,1,8.70,0.00,8.70,NULL,'2026-02-12 08:35:29'),(144,24,38,2,20.45,0.00,40.90,NULL,'2026-02-12 08:35:29'),(145,24,39,2,20.95,0.00,41.90,NULL,'2026-02-12 08:35:29'),(146,24,41,2,37.95,0.00,75.90,NULL,'2026-02-12 08:35:29'),(147,24,42,1,7.45,0.00,7.45,NULL,'2026-02-12 08:35:29'),(148,24,43,2,23.95,0.00,47.90,NULL,'2026-02-12 08:35:29'),(149,24,46,2,71.95,0.00,143.90,NULL,'2026-02-12 08:35:29'),(150,24,47,2,14.45,0.00,28.90,NULL,'2026-02-12 08:35:29'),(151,24,48,1,75.00,0.00,75.00,NULL,'2026-02-12 08:35:29'),(152,24,49,2,23.95,0.00,47.90,NULL,'2026-02-12 08:35:29'),(153,24,50,1,57.95,0.00,57.95,NULL,'2026-02-12 08:35:29'),(154,24,52,1,0.85,0.00,0.85,NULL,'2026-02-12 08:35:29'),(155,24,53,2,1.50,0.00,3.00,NULL,'2026-02-12 08:35:29'),(156,24,55,2,50.95,0.00,101.90,NULL,'2026-02-12 08:35:29'),(157,24,56,1,5.00,0.00,5.00,NULL,'2026-02-12 08:35:29'),(158,24,60,2,3.00,0.00,6.00,NULL,'2026-02-12 08:35:29'),(159,24,62,1,29.95,0.00,29.95,NULL,'2026-02-12 08:35:29'),(160,24,63,1,6.50,0.00,6.50,NULL,'2026-02-12 08:35:29'),(161,24,65,1,5.70,0.00,5.70,NULL,'2026-02-12 08:35:29'),(162,24,68,1,65.95,0.00,65.95,NULL,'2026-02-12 08:35:29'),(163,24,70,1,15.45,0.00,15.45,NULL,'2026-02-12 08:35:29'),(164,24,17,1,35.00,0.00,35.00,NULL,'2026-02-12 08:35:29'),(165,24,40,1,9.25,0.00,9.25,NULL,'2026-02-12 08:35:29'),(166,24,44,1,33.95,0.00,33.95,NULL,'2026-02-12 08:35:29'),(167,24,58,1,5.20,0.00,5.20,NULL,'2026-02-12 08:35:29'),(168,24,61,1,21.99,0.00,21.99,NULL,'2026-02-12 08:35:29'),(169,25,1,1,32.00,0.00,32.00,NULL,'2026-02-12 08:39:47'),(170,25,2,1,28.00,0.00,28.00,NULL,'2026-02-12 08:39:47'),(171,25,3,1,11.00,0.00,11.00,NULL,'2026-02-12 08:39:47'),(172,25,4,1,68.00,0.00,68.00,NULL,'2026-02-12 08:39:47'),(173,25,5,1,58.00,0.00,58.00,NULL,'2026-02-12 08:39:47'),(174,25,6,1,24.00,0.00,24.00,NULL,'2026-02-12 08:39:47'),(175,25,7,1,22.00,0.00,22.00,NULL,'2026-02-12 08:39:47'),(176,25,8,1,52.00,0.00,52.00,NULL,'2026-02-12 08:39:47'),(177,25,20,1,48.00,0.00,48.00,NULL,'2026-02-12 08:39:47'),(178,25,21,1,38.00,0.00,38.00,NULL,'2026-02-12 08:39:47'),(179,25,22,1,18.00,0.00,18.00,NULL,'2026-02-12 08:39:47'),(180,25,23,1,55.00,0.00,55.00,NULL,'2026-02-12 08:39:47'),(181,25,24,1,22.00,0.00,22.00,NULL,'2026-02-12 08:39:47'),(182,25,30,1,45.00,0.00,45.00,NULL,'2026-02-12 08:39:47'),(183,25,31,1,65.00,0.00,65.00,NULL,'2026-02-12 08:39:47'),(184,25,32,1,15.00,0.00,15.00,NULL,'2026-02-12 08:39:47'),(185,25,15,1,85.00,0.00,85.00,NULL,'2026-02-12 08:39:47'),(186,25,16,1,30.00,0.00,30.00,NULL,'2026-02-12 08:39:47'),(187,25,17,1,35.00,0.00,35.00,NULL,'2026-02-12 08:39:47'),(188,25,18,1,25.00,0.00,25.00,NULL,'2026-02-12 08:39:47'),(189,25,19,1,75.00,0.00,75.00,NULL,'2026-02-12 08:39:47'),(190,25,25,1,10.00,0.00,10.00,NULL,'2026-02-12 08:39:47'),(191,25,26,1,5.00,0.00,5.00,NULL,'2026-02-12 08:39:47'),(192,25,27,1,25.00,0.00,25.00,NULL,'2026-02-12 08:39:47'),(193,25,28,1,15.00,0.00,15.00,NULL,'2026-02-12 08:39:47'),(194,25,29,1,6.00,0.00,6.00,NULL,'2026-02-12 08:39:47'),(195,25,33,1,18.00,0.00,18.00,NULL,'2026-02-12 08:39:47'),(196,25,34,1,22.00,0.00,22.00,NULL,'2026-02-12 08:39:47'),(197,25,35,1,25.00,0.00,25.00,NULL,'2026-02-12 08:39:48'),(198,25,36,1,20.00,0.00,20.00,NULL,'2026-02-12 08:39:48'),(199,26,1,1,32.00,0.00,32.00,NULL,'2026-02-12 10:33:01'),(200,27,1,1,32.00,0.00,32.00,NULL,'2026-02-12 10:44:02'),(201,28,1,42,32.00,0.00,1344.00,NULL,'2026-02-12 10:53:35');
/*!40000 ALTER TABLE `invoice_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `invoices`
--

DROP TABLE IF EXISTS `invoices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoices` (
  `id` int NOT NULL AUTO_INCREMENT,
  `invoice_number` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `store_id` int NOT NULL,
  `cashier_id` int NOT NULL,
  `customer_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `customer_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `customer_address` text COLLATE utf8mb4_unicode_ci,
  `drawer_id` int DEFAULT NULL,
  `invoice_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `total_amount` decimal(12,2) NOT NULL,
  `paid_amount` decimal(12,2) DEFAULT NULL,
  `remaining_amount` decimal(12,2) DEFAULT NULL,
  `payment_method` enum('Cash','Card','Mixed') COLLATE utf8mb4_unicode_ci DEFAULT 'Cash',
  `status` enum('Completed','Cancelled','Draft') COLLATE utf8mb4_unicode_ci DEFAULT 'Completed',
  `notes` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `cash_amount` decimal(10,2) DEFAULT '0.00',
  `card_amount` decimal(10,2) DEFAULT '0.00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `invoice_number` (`invoice_number`),
  KEY `store_id` (`store_id`),
  KEY `cashier_id` (`cashier_id`),
  KEY `idx_invoice_number` (`invoice_number`),
  KEY `idx_invoice_date` (`invoice_date`),
  CONSTRAINT `invoices_ibfk_1` FOREIGN KEY (`store_id`) REFERENCES `stores` (`id`),
  CONSTRAINT `invoices_ibfk_2` FOREIGN KEY (`cashier_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoices`
--

LOCK TABLES `invoices` WRITE;
/*!40000 ALTER TABLE `invoices` DISABLE KEYS */;
INSERT INTO `invoices` VALUES (1,'INV-20260121135458',2,2,'طارق','01229525691',NULL,1,'2026-01-21 11:54:58',48.00,NULL,NULL,'Cash','Completed',NULL,'2026-01-21 11:54:58','2026-01-21 22:36:09',0.00,0.00),(2,'INV-20260121143041',2,2,'محمد طارق','01010101010',NULL,1,'2026-01-21 12:30:41',119.00,NULL,NULL,'Cash','Completed',NULL,'2026-01-21 12:30:41','2026-01-21 22:36:09',0.00,0.00),(3,'INV-20260121152241',2,2,'عبده','01070276578',NULL,1,'2026-01-21 13:22:41',187.00,NULL,NULL,'Cash','Completed',NULL,'2026-01-21 13:22:41','2026-01-21 22:36:09',0.00,0.00),(4,'INV-20260121152308',2,2,'خالد شوقي','01234567890',NULL,1,'2026-01-21 13:23:08',252.00,NULL,NULL,'Cash','Completed',NULL,'2026-01-21 13:23:08','2026-01-21 22:36:09',0.00,0.00),(5,'INV-20260121152346',2,2,'طارق','01229525691',NULL,1,'2026-01-21 13:23:46',48.00,NULL,NULL,'Cash','Completed',NULL,'2026-01-21 13:23:46','2026-01-21 22:36:09',0.00,0.00),(6,'INV-20260122000902',2,2,'خالد شوقي','01108261455','القلج',1,'2026-01-21 22:09:02',290.00,NULL,NULL,'Cash','Completed',NULL,'2026-01-21 22:09:02','2026-01-21 22:36:09',0.00,0.00),(7,'INV-20260122002613',2,2,'محمد شوقي','01070276578','القلج',1,'2026-01-21 22:26:13',139.00,NULL,NULL,'Cash','Completed',NULL,'2026-01-21 22:26:13','2026-01-21 22:36:09',0.00,0.00),(8,'INV-20260122021440',1,1,'ghg','3216445','ggg',2,'2026-01-22 00:14:40',60.00,NULL,NULL,'Cash','Completed',NULL,'2026-01-22 00:14:40','2026-01-22 00:14:40',0.00,0.00),(9,'INV-20260122122549',2,2,'ا','1','1',3,'2026-01-22 10:25:49',11.00,NULL,NULL,'Cash','Completed',NULL,'2026-01-22 10:25:49','2026-01-22 10:25:49',0.00,0.00),(10,'INV-20260122122833',2,2,'عبدالقادر طارق','01070276578','المرج',3,'2026-01-22 10:28:33',148.00,NULL,NULL,'Cash','Completed',NULL,'2026-01-22 10:28:33','2026-01-22 10:28:33',0.00,0.00),(11,'INV-20260131182216',3,3,'عبدالحميد','01234567890','الشروق',5,'2026-01-31 16:22:16',60.00,NULL,NULL,'Card','Completed',NULL,'2026-01-31 16:22:16','2026-01-31 16:22:16',0.00,0.00),(12,'INV-20260131183229',4,1,'عبدالقادر طارق','01070276578','المرج',4,'2026-01-31 16:32:29',32.00,NULL,NULL,'Cash','Completed',NULL,'2026-01-31 16:32:29','2026-01-31 16:32:29',0.00,0.00),(13,'INV-20260131194838',2,2,'عبدالحميد','01234567890','الشروق',6,'2026-01-31 17:48:38',32.00,NULL,NULL,'Cash','Completed',NULL,'2026-01-31 17:48:38','2026-01-31 17:48:38',0.00,0.00),(14,'INV-20260131201910',2,2,'عبدالقادر طارق','01070276578','المرج',8,'2026-01-31 18:19:10',476.00,NULL,NULL,'Mixed','Completed',NULL,'2026-01-31 18:19:10','2026-01-31 18:19:10',250.00,202.25),(15,'INV-20260203185927',2,2,'عبدالقادر طارق','01070276578','المرج',14,'2026-02-03 16:59:27',139.00,NULL,NULL,'Cash','Completed',NULL,'2026-02-03 16:59:27','2026-02-03 16:59:27',139.00,0.00),(16,'INV-20260205075018',2,2,'طارق','01229525691','القلج ش المدرسة الثانوية كركز الخانكة القليوبية ',14,'2026-02-05 05:50:18',7890.00,NULL,NULL,'Cash','Completed',NULL,'2026-02-05 05:50:18','2026-02-05 05:50:18',7600.00,0.00),(17,'INV-20260205083701',2,5,'Cash Customer','','',14,'2026-02-05 06:37:01',295.00,NULL,NULL,'Cash','Completed',NULL,'2026-02-05 06:37:01','2026-02-05 06:37:02',295.00,0.00),(18,'INV-20260205084739',2,5,'Cash Customer','','',14,'2026-02-05 06:47:39',70.00,NULL,NULL,'Cash','Completed',NULL,'2026-02-05 06:47:39','2026-02-05 06:47:39',70.00,0.00),(19,'INV-20260207210701',2,5,'عبدالقادر طارق','01070276578','المرج',14,'2026-02-07 19:07:01',267.00,NULL,NULL,'Cash','Completed',NULL,'2026-02-07 19:07:01','2026-02-07 19:07:01',247.00,0.00),(20,'INV-20260211113736',2,5,'عبدالقادر طارق','01070276578','المرج',15,'2026-02-11 09:37:36',32.00,NULL,NULL,'Cash','Completed',NULL,'2026-02-11 09:37:36','2026-02-11 09:37:36',32.00,0.00),(21,'INV-20260212000733',2,13,'Cash Customer','','',15,'2026-02-11 22:07:33',32.00,NULL,NULL,'Cash','Completed',NULL,'2026-02-11 22:07:33','2026-02-11 22:07:33',32.00,0.00),(22,'INV-20260212101726',2,13,'عبدالقادر طارق','01070276578','المرج',15,'2026-02-12 08:17:26',295.00,NULL,NULL,'Cash','Completed',NULL,'2026-02-12 08:17:26','2026-02-12 08:17:26',295.00,0.00),(23,'INV-20260212102601',2,13,'طارق','01229525691','القلج ش المدرسة الثانوية كركز الخانكة القليوبية',15,'2026-02-12 08:26:01',1525.00,NULL,NULL,'Cash','Completed',NULL,'2026-02-12 08:26:01','2026-02-12 08:26:02',1525.00,0.00),(24,'INV-20260212103528',2,5,'خالد شوقي','01108261455','القلج',15,'2026-02-12 08:35:28',1314.59,NULL,NULL,'Cash','Completed',NULL,'2026-02-12 08:35:28','2026-02-12 08:35:29',1314.59,0.00),(25,'INV-20260212103947',2,5,'Cash Customer','','',15,'2026-02-12 08:39:47',997.00,NULL,NULL,'Cash','Completed',NULL,'2026-02-12 08:39:47','2026-02-12 08:39:48',997.00,0.00),(26,'INV-20260212123301',2,5,'Cash Customer','','',16,'2026-02-12 10:33:01',32.00,NULL,NULL,'Cash','Completed',NULL,'2026-02-12 10:33:01','2026-02-12 10:33:01',32.00,0.00),(27,'INV-20260212124402',2,5,'Cash Customer','','',16,'2026-02-12 10:44:02',32.00,NULL,NULL,'Cash','Completed',NULL,'2026-02-12 10:44:02','2026-02-12 10:44:02',32.00,0.00),(28,'INV-20260212125335',2,5,'Cash Customer','','',16,'2026-02-12 10:53:35',1344.00,NULL,NULL,'Cash','Completed',NULL,'2026-02-12 10:53:35','2026-02-12 10:53:35',1344.00,0.00);
/*!40000 ALTER TABLE `invoices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `login_attempts`
--

DROP TABLE IF EXISTS `login_attempts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `login_attempts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  `device_id` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `device_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ip_address` varchar(45) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `attempt_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `success` tinyint(1) DEFAULT NULL,
  `failure_reason` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `idx_user_time` (`user_email`,`attempt_time`),
  KEY `idx_success` (`success`),
  KEY `idx_device` (`device_id`),
  CONSTRAINT `login_attempts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=339 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `login_attempts`
--

LOCK TABLES `login_attempts` WRITE;
/*!40000 ALTER TABLE `login_attempts` DISABLE KEYS */;
INSERT INTO `login_attempts` VALUES (1,'admin@posapp.com',1,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 17:13:28',0,'جهاز غير مصرح به'),(2,'apdo@gmail.com',2,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 17:14:16',0,'جهاز غير مصرح به'),(3,'admin@posapp.com',1,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 17:21:48',0,'جهاز غير مصرح به'),(4,'admin@posapp.com',1,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 17:23:52',1,NULL),(5,'mt@pos.com',5,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 17:28:26',0,'جهاز غير مصرح به'),(6,'apdo@gmail.com',2,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 17:28:39',0,'جهاز غير مصرح به'),(7,'admin@posapp.com',1,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 17:29:02',1,NULL),(8,'apdo@gmail.com',2,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 17:31:31',0,'جهاز غير مصرح به'),(9,'apdo@gmail.com',2,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 17:32:09',0,'جهاز غير مصرح به'),(10,'admin@posapp.com',NULL,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 17:32:23',0,'بيانات دخول غير صحيحة'),(11,'admin@posapp.com',1,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 17:32:26',1,NULL),(12,'admin@posapp.com',1,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 17:41:38',1,NULL),(13,'apdo@gmail.com',2,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 17:42:41',1,NULL),(14,'apdo@gmail.com',2,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 17:48:09',1,NULL),(15,'apdo@gmail.com',NULL,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 17:53:22',0,'بيانات دخول غير صحيحة'),(16,'apdo@gmail.com',2,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 17:53:25',1,NULL),(17,'apdo@gmail.com',2,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 17:53:52',1,NULL),(18,'apdo@gmail.com',2,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 18:14:19',1,NULL),(19,'apdo@gmail.com',2,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 18:14:40',1,NULL),(20,'apdo@gmail.com',2,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 18:16:57',1,NULL),(21,'apdo@gmail.com',2,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 18:26:49',1,NULL),(22,'admin@posapp.com',1,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 18:29:32',1,NULL),(23,'admin@posapp.com',1,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 19:03:29',1,NULL),(24,'apdo@gmail.com',2,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 19:04:28',1,NULL),(25,'admin@posapp.com',1,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 19:08:10',1,NULL),(26,'admin@posapp.com',1,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 19:40:12',1,NULL),(27,'admin@posapp.com',1,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 19:44:41',1,NULL),(28,'apdo@gmail.com',2,'e0:80:03:0e:3a:e8_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-01-31 19:52:30',1,NULL),(29,'admin@posapp.com',1,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-02-01 16:20:03',1,NULL),(30,'admin@posapp.com',1,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-02-01 16:27:22',1,NULL),(31,'admin@posapp.com',1,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-02-01 16:28:37',1,NULL),(32,'admin@posapp.com',1,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-02-01 16:32:02',1,NULL),(33,'admin@posapp.com',1,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-02-01 16:38:02',1,NULL),(34,'admin@posapp.com',1,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-02-01 16:53:54',1,NULL),(35,'admin@posapp.com',1,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-02-01 16:58:03',1,NULL),(36,'admin@posapp.com',1,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-02-01 17:02:28',1,NULL),(37,'admin@posapp.com',1,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-02-01 17:09:37',1,NULL),(38,'apdo@gmail.com',2,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-02-01 17:13:13',0,'جهاز غير مصرح به'),(39,'apdo@gmail.com',2,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-02-01 17:13:18',0,'جهاز غير مصرح به'),(40,'admin@posapp.com',1,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-02-01 17:13:30',1,NULL),(41,'apdo@gmail.com',2,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-02-01 17:14:58',0,'جهاز غير مصرح به'),(42,'mt@pos.com',5,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-02-01 17:15:18',0,'جهاز غير مصرح به'),(43,'admin@posapp.com',1,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-02-01 17:15:38',1,NULL),(44,'apdo@gmail.com',2,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-02-01 17:17:17',1,NULL),(45,'apdo@gmail.com',2,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-02-01 17:19:41',1,NULL),(46,'apdo@gmail.com',2,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-02-01 17:22:12',1,NULL),(47,'apdo@gmail.com',2,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-02-01 17:23:08',1,NULL),(48,'admin@posapp.com',1,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-02-01 17:28:59',1,NULL),(49,'apdo@gmail.com',2,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.5','2026-02-01 17:29:23',1,NULL),(50,'admin@posapp.com',NULL,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.4','2026-02-02 16:58:08',0,'بيانات دخول غير صحيحة'),(51,'admin@posapp.com',NULL,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.4','2026-02-02 16:58:10',0,'بيانات دخول غير صحيحة'),(52,'admin@posapp.com',1,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.4','2026-02-02 16:58:14',1,NULL),(53,'mt@pos.com',NULL,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.4','2026-02-02 16:59:44',0,'بيانات دخول غير صحيحة'),(54,'mt@pos.com',5,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.4','2026-02-02 16:59:50',1,NULL),(55,'apdo@gmail.com',2,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.4','2026-02-02 17:01:14',1,NULL),(56,'apdo@gmail.com',2,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.4','2026-02-02 17:02:11',1,NULL),(57,'mt@pos.com',5,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.4','2026-02-02 17:03:33',1,NULL),(58,'mt@pos.com',5,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.4','2026-02-02 17:04:15',1,NULL),(59,'apdo@gmail.com',2,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.4','2026-02-02 17:04:52',1,NULL),(60,'apdo@gmail.com',2,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.4','2026-02-02 17:05:33',1,NULL),(61,'apdo@gmail.com',2,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.4','2026-02-02 17:10:33',1,NULL),(62,'admin@posapp.com',1,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.4','2026-02-02 17:10:50',1,NULL),(63,'mt@pos.com',5,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.4','2026-02-02 17:11:15',1,NULL),(64,'mt@pos.com',5,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.4','2026-02-02 17:12:00',1,NULL),(65,'apdo@gmail.com',2,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.4','2026-02-02 17:12:39',1,NULL),(66,'mt@pos.com',5,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.4','2026-02-02 17:18:30',1,NULL),(67,'apdo@gmail.com',2,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.4','2026-02-02 17:21:57',1,NULL),(68,'mt@pos.com',5,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.4','2026-02-02 17:22:43',1,NULL),(69,'apdo@gmail.com',2,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.4','2026-02-02 17:23:50',1,NULL),(70,'admin@posapp.com',1,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.4','2026-02-02 19:37:14',1,NULL),(71,'admin@posapp.com',1,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.4','2026-02-03 16:31:57',1,NULL),(72,'admin@posapp.com',1,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.4','2026-02-03 16:33:11',1,NULL),(73,'admin@posapp.com',1,'7e:f8:e3:8d:35:d7_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.4','2026-02-03 16:43:11',1,NULL),(74,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-03 16:50:51',1,NULL),(75,'apdo@gmail.com',2,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-03 16:52:03',0,'جهاز غير مصرح به'),(76,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-03 16:52:27',1,NULL),(77,'apdo@gmail.com',2,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-03 16:53:56',1,NULL),(78,'apdo@gmail.com',2,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-03 16:56:53',1,NULL),(79,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-03 16:57:54',1,NULL),(80,'apdo@gmai.com',NULL,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-03 16:59:02',0,'بيانات دخول غير صحيحة'),(81,'apdo@gmai.com',NULL,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-03 16:59:04',0,'بيانات دخول غير صحيحة'),(82,'apdo@gmail.com',2,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-03 16:59:13',1,NULL),(83,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-03 17:15:08',1,NULL),(84,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-03 17:17:33',1,NULL),(85,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-03 17:20:13',1,NULL),(86,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-03 17:25:37',1,NULL),(87,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-03 17:37:34',1,NULL),(88,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-03 17:38:30',1,NULL),(89,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-03 17:40:02',1,NULL),(90,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-03 17:41:27',1,NULL),(91,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-03 17:46:34',1,NULL),(92,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-03 17:51:10',1,NULL),(93,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-04 09:05:35',1,NULL),(94,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-04 09:13:34',1,NULL),(95,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-04 09:22:44',1,NULL),(96,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-04 09:25:52',1,NULL),(97,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-04 09:26:03',1,NULL),(98,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-04 09:28:29',1,NULL),(99,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-04 09:35:06',1,NULL),(100,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-04 09:38:56',1,NULL),(101,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-04 09:47:00',1,NULL),(102,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-04 09:48:42',1,NULL),(103,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-04 09:51:52',1,NULL),(104,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-04 09:53:51',1,NULL),(105,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-04 09:54:30',1,NULL),(106,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-04 09:56:45',1,NULL),(107,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-04 09:58:21',1,NULL),(108,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-04 10:00:05',1,NULL),(109,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-04 10:00:26',1,NULL),(110,'apdo@gmail.com',2,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-05 05:44:40',1,NULL),(111,'mt@poscom',NULL,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-05 06:02:09',0,'بيانات دخول غير صحيحة'),(112,'mt@poscom',NULL,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-05 06:02:11',0,'بيانات دخول غير صحيحة'),(113,'mt@poscom',NULL,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-05 06:02:14',0,'بيانات دخول غير صحيحة'),(114,'mt@poscom',NULL,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-05 06:02:17',0,'بيانات دخول غير صحيحة'),(115,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-05 06:02:23',1,NULL),(116,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-05 06:17:47',1,NULL),(117,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-05 06:26:31',1,NULL),(118,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-05 06:35:15',1,NULL),(119,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-05 06:44:55',1,NULL),(120,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-05 06:49:25',1,NULL),(121,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-05 06:57:05',1,NULL),(122,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-05 06:59:30',1,NULL),(123,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-05 07:02:11',1,NULL),(124,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-05 07:05:36',1,NULL),(125,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-05 07:10:07',1,NULL),(126,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-05 07:12:03',1,NULL),(127,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-05 07:15:45',1,NULL),(128,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-05 16:57:12',1,NULL),(129,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-06 09:40:41',1,NULL),(130,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-06 09:53:19',1,NULL),(131,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-06 09:56:06',1,NULL),(132,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-06 10:00:03',1,NULL),(133,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-07 18:22:06',1,NULL),(134,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-07 18:44:53',1,NULL),(135,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-07 18:46:12',1,NULL),(136,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-07 18:59:19',1,NULL),(137,'th@pos.com',8,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-07 19:09:31',1,NULL),(138,'apdo@gmail.com',2,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-07 19:14:13',1,NULL),(139,'admin@pos.com',NULL,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 08:33:11',0,'بيانات دخول غير صحيحة'),(140,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 08:33:27',1,NULL),(141,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 08:34:03',1,NULL),(142,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 08:57:19',1,NULL),(143,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 08:58:43',1,NULL),(144,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 09:03:16',1,NULL),(145,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 09:11:32',1,NULL),(146,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 09:13:26',1,NULL),(147,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 09:16:10',1,NULL),(148,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 09:18:24',1,NULL),(149,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 09:20:28',1,NULL),(150,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 09:23:31',1,NULL),(151,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 09:48:39',1,NULL),(152,'apdo@gmail.com',2,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 09:49:57',1,NULL),(153,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 09:54:56',1,NULL),(154,'apdo@gmail.com',2,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 09:56:28',1,NULL),(155,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 09:57:15',1,NULL),(156,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 10:00:32',1,NULL),(157,'apdo@gmail.com',2,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 10:01:21',1,NULL),(158,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 10:03:03',1,NULL),(159,'apdo@gmail.com',2,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 10:04:34',1,NULL),(160,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 10:05:43',1,NULL),(161,'apdo@gmail.com',2,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 10:07:18',1,NULL),(162,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 10:08:54',1,NULL),(163,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 10:13:23',1,NULL),(164,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 10:20:25',1,NULL),(165,'admin@posapp.com',NULL,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 10:30:44',0,'بيانات دخول غير صحيحة'),(166,'admin@posapp.com',NULL,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 10:30:46',0,'بيانات دخول غير صحيحة'),(167,'admin@posapp.com',NULL,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 10:30:56',0,'بيانات دخول غير صحيحة'),(168,'admin@posapp.com',NULL,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 10:31:10',0,'بيانات دخول غير صحيحة'),(169,'admin@posapp.com',NULL,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 10:31:38',0,'بيانات دخول غير صحيحة'),(170,'admin@posapp.com',NULL,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 10:31:41',0,'بيانات دخول غير صحيحة'),(171,'admin@posapp.com',NULL,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 10:31:43',0,'بيانات دخول غير صحيحة'),(172,'admin@admin.com',NULL,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 10:33:35',0,'بيانات دخول غير صحيحة'),(173,'admin@admin.com',NULL,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 10:33:56',0,'بيانات دخول غير صحيحة'),(174,'admin@admin.com',NULL,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 10:34:02',0,'بيانات دخول غير صحيحة'),(175,'admin@admin.com',NULL,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 10:34:41',0,'بيانات دخول غير صحيحة'),(176,'admin@admin.com',NULL,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 10:35:26',0,'بيانات دخول غير صحيحة'),(177,'admin@posapp.com',NULL,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 10:39:17',0,'بيانات دخول غير صحيحة'),(178,'admin@posapp.com',NULL,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 10:39:41',0,'بيانات دخول غير صحيحة'),(179,'admin@posapp.com',NULL,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 10:44:32',0,'بيانات دخول غير صحيحة'),(180,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 10:44:38',1,NULL),(181,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 20:32:34',1,NULL),(182,'apdo@gmail.com',2,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 20:33:44',1,NULL),(183,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 20:34:39',1,NULL),(184,'mt@pos.com',NULL,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 20:40:32',0,'بيانات دخول غير صحيحة'),(185,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 20:40:36',1,NULL),(186,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 20:57:31',1,NULL),(187,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 20:59:03',1,NULL),(188,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 21:14:02',1,NULL),(189,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 21:18:58',1,NULL),(190,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 21:24:04',1,NULL),(191,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 21:24:29',1,NULL),(192,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 21:28:03',1,NULL),(193,'mt@pos.com',5,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-08 21:32:52',1,NULL),(194,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 04:28:33',1,NULL),(195,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 04:40:18',1,NULL),(196,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 04:50:23',1,NULL),(197,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 04:51:01',1,NULL),(198,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 04:57:24',1,NULL),(199,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 05:01:41',1,NULL),(200,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 05:04:52',1,NULL),(201,'admin@posapp.com',1,'fb:ef:be:f9:e7:9d_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 05:14:32',1,NULL),(202,'admin@posapp.com',1,'f9:e7:9c:72:c9:25_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 05:58:55',1,NULL),(203,'admin@posapp.com',1,'f9:e7:9c:72:c9:25_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 06:14:23',1,NULL),(204,'admin@posapp.com',1,'f9:e7:9c:72:c9:25_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 06:31:24',1,NULL),(205,'admin@posapp.com',1,'f9:e7:9c:72:c9:25_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 06:34:46',1,NULL),(206,'admin@posapp.com',1,'f9:e7:9c:72:c9:25_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 06:42:12',1,NULL),(207,'admin@posapp.com',1,'f9:e7:9c:72:c9:25_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 06:55:25',1,NULL),(208,'mt@pos.com',5,'f9:e7:9c:72:c9:25_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 07:03:03',0,'جهاز غير مصرح به'),(209,'admin@posapp.com',1,'f9:e7:9c:72:c9:25_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 07:03:23',1,NULL),(210,'mt@pos.com',5,'f9:e7:9c:72:c9:25_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 07:06:10',0,'جهاز غير مصرح به'),(211,'mt@pos.com',5,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 07:14:03',0,'جهاز غير مصرح به'),(212,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 07:14:14',1,NULL),(213,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 07:16:03',1,NULL),(214,'mt@pos.com',5,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 07:17:28',1,NULL),(215,'mt@pos.com',5,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 07:18:34',1,NULL),(216,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 07:23:51',1,NULL),(217,'mt@pos.com',5,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 07:25:12',1,NULL),(218,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 07:29:50',1,NULL),(219,'mt@pos.com',5,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 07:30:25',1,NULL),(220,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 07:39:53',1,NULL),(221,'dev@admin.com',NULL,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 08:09:33',0,'بيانات دخول غير صحيحة'),(222,'dev@admin.com',NULL,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 08:09:35',0,'بيانات دخول غير صحيحة'),(223,'dev@admin.com',NULL,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 08:09:53',0,'بيانات دخول غير صحيحة'),(224,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 08:10:12',1,NULL),(225,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-09 08:29:22',1,NULL),(226,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-10 17:18:21',1,NULL),(227,'mt@pos.com',5,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-10 17:29:39',1,NULL),(228,'mt@pos.com',5,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-10 17:45:32',1,NULL),(229,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','10.229.72.124','2026-02-10 19:48:14',1,NULL),(230,'admin@posapp.com',NULL,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 08:39:10',0,'بيانات دخول غير صحيحة'),(231,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 08:39:14',1,NULL),(232,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 08:42:00',1,NULL),(233,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 08:44:35',1,NULL),(234,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 08:46:27',1,NULL),(235,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 08:51:53',1,NULL),(236,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 08:54:49',1,NULL),(237,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 09:00:46',1,NULL),(238,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 09:09:30',1,NULL),(239,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 09:14:02',1,NULL),(240,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 09:25:44',1,NULL),(241,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 09:30:40',1,NULL),(242,'mt@pos.com',5,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 09:36:18',1,NULL),(243,'dev@admin.com',NULL,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 18:08:51',0,'بيانات دخول غير صحيحة'),(244,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 18:08:54',1,NULL),(245,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 21:49:44',1,NULL),(246,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 21:57:25',1,NULL),(247,'mt@pos.com',5,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 21:58:00',1,NULL),(248,'apdo@gmail.com',2,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 21:59:09',1,NULL),(249,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 21:59:44',1,NULL),(250,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 22:06:41',1,NULL),(251,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 22:13:02',1,NULL),(252,'dev@admin.com',NULL,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 22:16:07',0,'بيانات دخول غير صحيحة'),(253,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 22:16:13',1,NULL),(254,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 22:38:02',1,NULL),(255,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 22:44:00',1,NULL),(256,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 22:48:23',1,NULL),(257,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-11 22:55:45',1,NULL),(258,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 06:32:52',1,NULL),(259,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 06:44:27',1,NULL),(260,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 06:47:23',1,NULL),(261,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 06:52:15',1,NULL),(262,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 06:59:37',1,NULL),(263,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:02:00',1,NULL),(264,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:03:53',1,NULL),(265,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:06:38',1,NULL),(266,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:08:05',1,NULL),(267,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:09:00',1,NULL),(268,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:10:01',1,NULL),(269,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:11:34',1,NULL),(270,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:12:14',1,NULL),(271,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:14:18',1,NULL),(272,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:16:03',1,NULL),(273,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:17:52',1,NULL),(274,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:19:04',1,NULL),(275,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:20:03',1,NULL),(276,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:21:12',1,NULL),(277,'dev@admin.com',NULL,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:23:00',0,'بيانات دخول غير صحيحة'),(278,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:23:04',1,NULL),(279,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:23:59',1,NULL),(280,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:25:04',1,NULL),(281,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:26:17',1,NULL),(282,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:27:49',1,NULL),(283,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:29:29',1,NULL),(284,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:35:10',1,NULL),(285,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:41:32',1,NULL),(286,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:44:22',1,NULL),(287,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:45:26',1,NULL),(288,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:49:53',1,NULL),(289,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:52:28',1,NULL),(290,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:54:59',1,NULL),(291,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:56:21',1,NULL),(292,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 07:58:47',1,NULL),(293,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 08:02:00',1,NULL),(294,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 08:04:54',1,NULL),(295,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 08:09:19',1,NULL),(296,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 08:10:56',1,NULL),(297,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 08:12:50',1,NULL),(298,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 08:14:26',1,NULL),(299,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 08:16:05',1,NULL),(300,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 08:22:28',1,NULL),(301,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 08:31:32',1,NULL),(302,'mt@pos.com',5,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 08:32:08',1,NULL),(303,'mt@pos.com',5,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 08:37:02',1,NULL),(304,'mt@pos.com',5,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 08:42:43',1,NULL),(305,'mt@pos.com',5,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 08:49:00',1,NULL),(306,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 08:50:59',1,NULL),(307,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 08:51:45',1,NULL),(308,'mt@pos.com',5,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 08:52:18',1,NULL),(309,'apdo@gmail.com',2,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 08:52:50',1,NULL),(310,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 08:55:20',1,NULL),(311,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 09:01:00',1,NULL),(312,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 09:01:44',1,NULL),(313,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 10:25:58',1,NULL),(314,'mt@pos.com',5,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 10:27:16',1,NULL),(315,'mt@pos.com',5,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 10:31:45',1,NULL),(316,'mt@pos.com',5,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 10:42:26',1,NULL),(317,'mt@pos.com',NULL,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 10:51:07',0,'بيانات دخول غير صحيحة'),(318,'mt@pos.com',5,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 10:51:10',1,NULL),(319,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 10:56:46',1,NULL),(320,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 11:03:00',1,NULL),(321,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 11:07:45',1,NULL),(322,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 11:12:17',1,NULL),(323,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 11:18:11',1,NULL),(324,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-12 11:27:25',1,NULL),(325,'apdo@gmail.com',2,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-13 11:10:22',1,NULL),(326,'mt@pos.com',5,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-13 11:11:17',1,NULL),(327,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-13 11:12:28',1,NULL),(328,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-13 11:14:10',1,NULL),(329,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-13 11:26:28',1,NULL),(330,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-13 11:27:18',1,NULL),(331,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-13 11:31:24',1,NULL),(332,'admin@posapp.com',1,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-13 11:39:48',1,NULL),(333,'dev@admin.com',NULL,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-14 00:51:22',0,'بيانات دخول غير صحيحة'),(334,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-14 00:51:25',1,NULL),(335,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-14 00:54:50',1,NULL),(336,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-14 01:01:53',1,NULL),(337,'apdo@gmail.com',2,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-14 01:02:25',1,NULL),(338,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-14 01:18:52',1,NULL);
/*!40000 ALTER TABLE `login_attempts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_items`
--

DROP TABLE IF EXISTS `order_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `product_id` int NOT NULL,
  `quantity` int NOT NULL,
  `unit_price` decimal(10,2) DEFAULT NULL,
  `total_price` decimal(12,2) DEFAULT NULL,
  `notes` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `order_id` (`order_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `order_items_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `order_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=106 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_items`
--

LOCK TABLES `order_items` WRITE;
/*!40000 ALTER TABLE `order_items` DISABLE KEYS */;
INSERT INTO `order_items` VALUES (1,1,4,1,68.00,68.00,NULL,'2026-01-21 11:42:40'),(2,1,5,1,58.00,58.00,NULL,'2026-01-21 11:42:40'),(3,1,8,1,52.00,52.00,NULL,'2026-01-21 11:42:40'),(4,2,9,1,30.00,30.00,NULL,'2026-01-21 11:48:49'),(5,2,22,1,18.00,18.00,NULL,'2026-01-21 11:48:49'),(6,3,1,1,32.00,32.00,NULL,'2026-01-21 11:53:57'),(7,3,2,1,28.00,28.00,NULL,'2026-01-21 11:53:57'),(8,3,3,1,11.00,11.00,NULL,'2026-01-21 11:53:57'),(9,3,5,2,58.00,116.00,NULL,'2026-01-21 11:53:57'),(10,4,3,1,11.00,11.00,NULL,'2026-01-21 12:28:55'),(11,4,2,1,28.00,28.00,NULL,'2026-01-21 12:28:55'),(12,4,7,1,22.00,22.00,NULL,'2026-01-21 12:28:55'),(13,4,5,1,58.00,58.00,NULL,'2026-01-21 12:28:55'),(14,5,1,2,32.00,64.00,NULL,'2026-01-21 13:21:41'),(15,5,6,1,24.00,24.00,NULL,'2026-01-21 13:21:41'),(16,5,20,1,48.00,48.00,NULL,'2026-01-21 13:21:41'),(17,5,17,1,35.00,35.00,NULL,'2026-01-21 13:21:41'),(18,5,22,1,18.00,18.00,NULL,'2026-01-21 13:21:41'),(19,5,21,1,38.00,38.00,NULL,'2026-01-21 13:21:41'),(20,5,35,1,25.00,25.00,NULL,'2026-01-21 13:21:41'),(21,6,3,1,11.00,11.00,NULL,'2026-01-21 13:38:22'),(22,7,6,1,24.00,24.00,NULL,'2026-01-21 22:07:31'),(23,7,1,1,32.00,32.00,NULL,'2026-01-21 22:07:31'),(24,7,20,1,48.00,48.00,NULL,'2026-01-21 22:07:31'),(25,7,17,1,35.00,35.00,NULL,'2026-01-21 22:07:31'),(26,7,22,1,18.00,18.00,NULL,'2026-01-21 22:07:31'),(27,7,21,1,38.00,38.00,NULL,'2026-01-21 22:07:31'),(28,7,31,1,65.00,65.00,NULL,'2026-01-21 22:07:31'),(29,7,26,1,5.00,5.00,NULL,'2026-01-21 22:07:31'),(30,7,35,1,25.00,25.00,NULL,'2026-01-21 22:07:31'),(31,8,1,1,32.00,32.00,NULL,'2026-01-21 22:23:58'),(32,8,17,1,35.00,35.00,NULL,'2026-01-21 22:23:58'),(33,8,6,1,24.00,24.00,NULL,'2026-01-21 22:23:58'),(34,8,20,1,48.00,48.00,NULL,'2026-01-21 22:23:58'),(35,9,1,1,32.00,32.00,NULL,'2026-02-11 09:31:04'),(36,10,1,1,32.00,32.00,NULL,'2026-02-11 09:31:29'),(37,11,1,1,32.00,32.00,NULL,'2026-02-12 08:16:52'),(38,11,2,1,28.00,28.00,NULL,'2026-02-12 08:16:52'),(39,11,3,1,11.00,11.00,NULL,'2026-02-12 08:16:52'),(40,11,4,1,68.00,68.00,NULL,'2026-02-12 08:16:52'),(41,11,5,1,58.00,58.00,NULL,'2026-02-12 08:16:52'),(42,11,6,1,24.00,24.00,NULL,'2026-02-12 08:16:52'),(43,11,7,1,22.00,22.00,NULL,'2026-02-12 08:16:52'),(44,11,8,1,52.00,52.00,NULL,'2026-02-12 08:16:52'),(45,12,1,10,32.00,320.00,NULL,'2026-02-12 08:24:38'),(46,12,2,2,28.00,56.00,NULL,'2026-02-12 08:24:38'),(47,12,3,10,11.00,110.00,NULL,'2026-02-12 08:24:38'),(48,12,4,1,68.00,68.00,NULL,'2026-02-12 08:24:38'),(49,12,5,1,58.00,58.00,NULL,'2026-02-12 08:24:38'),(50,12,6,1,24.00,24.00,NULL,'2026-02-12 08:24:38'),(51,12,7,3,22.00,66.00,NULL,'2026-02-12 08:24:38'),(52,12,8,1,52.00,52.00,NULL,'2026-02-12 08:24:39'),(53,12,37,4,15.00,60.00,NULL,'2026-02-12 08:24:39'),(54,12,33,1,18.00,18.00,NULL,'2026-02-12 08:24:39'),(55,12,34,1,22.00,22.00,NULL,'2026-02-12 08:24:39'),(56,12,35,1,25.00,25.00,NULL,'2026-02-12 08:24:39'),(57,12,36,1,20.00,20.00,NULL,'2026-02-12 08:24:39'),(58,12,20,1,48.00,48.00,NULL,'2026-02-12 08:24:39'),(59,12,21,1,38.00,38.00,NULL,'2026-02-12 08:24:39'),(60,12,22,1,18.00,18.00,NULL,'2026-02-12 08:24:39'),(61,12,23,1,55.00,55.00,NULL,'2026-02-12 08:24:39'),(62,12,24,1,22.00,22.00,NULL,'2026-02-12 08:24:39'),(63,12,30,2,45.00,90.00,NULL,'2026-02-12 08:24:39'),(64,12,31,1,65.00,65.00,NULL,'2026-02-12 08:24:39'),(65,12,32,1,15.00,15.00,NULL,'2026-02-12 08:24:39'),(66,12,15,1,85.00,85.00,NULL,'2026-02-12 08:24:39'),(67,12,16,1,30.00,30.00,NULL,'2026-02-12 08:24:39'),(68,12,17,1,35.00,35.00,NULL,'2026-02-12 08:24:39'),(69,12,18,2,25.00,50.00,NULL,'2026-02-12 08:24:39'),(70,12,19,1,75.00,75.00,NULL,'2026-02-12 08:24:39'),(71,13,1,1,32.00,32.00,NULL,'2026-02-12 08:35:09'),(72,13,2,1,28.00,28.00,NULL,'2026-02-12 08:35:09'),(73,13,3,1,11.00,11.00,NULL,'2026-02-12 08:35:09'),(74,13,4,1,68.00,68.00,NULL,'2026-02-12 08:35:09'),(75,13,5,2,58.00,116.00,NULL,'2026-02-12 08:35:09'),(76,13,6,1,24.00,24.00,NULL,'2026-02-12 08:35:09'),(77,13,7,2,22.00,44.00,NULL,'2026-02-12 08:35:09'),(78,13,8,1,52.00,52.00,NULL,'2026-02-12 08:35:09'),(79,13,72,1,17.50,17.50,NULL,'2026-02-12 08:35:09'),(80,13,83,1,8.70,8.70,NULL,'2026-02-12 08:35:09'),(81,13,38,2,20.45,40.90,NULL,'2026-02-12 08:35:09'),(82,13,39,2,20.95,41.90,NULL,'2026-02-12 08:35:09'),(83,13,41,2,37.95,75.90,NULL,'2026-02-12 08:35:09'),(84,13,42,1,7.45,7.45,NULL,'2026-02-12 08:35:09'),(85,13,43,2,23.95,47.90,NULL,'2026-02-12 08:35:09'),(86,13,46,2,71.95,143.90,NULL,'2026-02-12 08:35:09'),(87,13,47,2,14.45,28.90,NULL,'2026-02-12 08:35:09'),(88,13,48,1,75.00,75.00,NULL,'2026-02-12 08:35:09'),(89,13,49,2,23.95,47.90,NULL,'2026-02-12 08:35:09'),(90,13,50,1,57.95,57.95,NULL,'2026-02-12 08:35:09'),(91,13,52,1,0.85,0.85,NULL,'2026-02-12 08:35:09'),(92,13,53,2,1.50,3.00,NULL,'2026-02-12 08:35:09'),(93,13,55,2,50.95,101.90,NULL,'2026-02-12 08:35:09'),(94,13,56,1,5.00,5.00,NULL,'2026-02-12 08:35:09'),(95,13,60,2,3.00,6.00,NULL,'2026-02-12 08:35:09'),(96,13,62,1,29.95,29.95,NULL,'2026-02-12 08:35:09'),(97,13,63,1,6.50,6.50,NULL,'2026-02-12 08:35:09'),(98,13,65,1,5.70,5.70,NULL,'2026-02-12 08:35:09'),(99,13,68,1,65.95,65.95,NULL,'2026-02-12 08:35:09'),(100,13,70,1,15.45,15.45,NULL,'2026-02-12 08:35:09'),(101,13,17,1,35.00,35.00,NULL,'2026-02-12 08:35:09'),(102,13,40,1,9.25,9.25,NULL,'2026-02-12 08:35:09'),(103,13,44,1,33.95,33.95,NULL,'2026-02-12 08:35:09'),(104,13,58,1,5.20,5.20,NULL,'2026-02-12 08:35:09'),(105,13,61,1,21.99,21.99,NULL,'2026-02-12 08:35:09');
/*!40000 ALTER TABLE `order_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_number` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `customer_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `customer_phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `customer_address` text COLLATE utf8mb4_unicode_ci,
  `customer_city` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `source_store_id` int NOT NULL,
  `destination_store_id` int DEFAULT NULL,
  `call_center_user_id` int NOT NULL,
  `order_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `expected_delivery_date` datetime DEFAULT NULL,
  `total_amount` decimal(12,2) DEFAULT NULL,
  `status` enum('Pending','Confirmed','Prepared','Delivered','Cancelled') COLLATE utf8mb4_unicode_ci DEFAULT 'Pending',
  `notes` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_number` (`order_number`),
  KEY `source_store_id` (`source_store_id`),
  KEY `destination_store_id` (`destination_store_id`),
  KEY `call_center_user_id` (`call_center_user_id`),
  KEY `idx_order_number` (`order_number`),
  KEY `idx_order_status` (`status`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`source_store_id`) REFERENCES `stores` (`id`),
  CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`destination_store_id`) REFERENCES `stores` (`id`),
  CONSTRAINT `orders_ibfk_3` FOREIGN KEY (`call_center_user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (1,'ORD-20260121134240','طارق عبدالقادر','01229525691','القلج',NULL,1,NULL,1,'2026-01-21 11:42:40',NULL,178.00,'Pending',NULL,'2026-01-21 11:42:40','2026-01-21 11:42:40'),(2,'ORD-20260121134849','طارق','01229525691','القلج',NULL,1,2,4,'2026-01-21 11:48:49',NULL,48.00,'Delivered',NULL,'2026-01-21 11:48:49','2026-01-21 13:23:46'),(3,'ORD-20260121135357','عبده','01070276578','القلج',NULL,1,2,4,'2026-01-21 11:53:57',NULL,187.00,'Delivered',NULL,'2026-01-21 11:53:57','2026-01-21 13:22:41'),(4,'ORD-20260121142855','محمد طارق','01010101010','القلج',NULL,1,2,1,'2026-01-21 12:28:55',NULL,119.00,'Delivered',NULL,'2026-01-21 12:28:55','2026-01-21 12:30:41'),(5,'ORD-20260121152141','خالد شوقي','01234567890','المرج',NULL,1,2,4,'2026-01-21 13:21:41',NULL,252.00,'Delivered',NULL,'2026-01-21 13:21:41','2026-01-21 13:23:08'),(6,'ORD-20260121153822','ا','1','1',NULL,1,2,4,'2026-01-21 13:38:22',NULL,11.00,'Delivered',NULL,'2026-01-21 13:38:22','2026-01-22 10:25:49'),(7,'ORD-20260122000731','خالد شوقي','01108261455','القلج',NULL,1,2,1,'2026-01-21 22:07:31',NULL,290.00,'Delivered',NULL,'2026-01-21 22:07:31','2026-01-21 22:09:02'),(8,'ORD-20260122002358','محمد شوقي','01070276578','القلج',NULL,1,2,1,'2026-01-21 22:23:58',NULL,139.00,'Delivered',NULL,'2026-01-21 22:23:58','2026-01-21 22:26:13'),(9,'ORD-20260211113104','عبدالقادر طارق','01070276578','المرج',NULL,1,1,1,'2026-02-11 09:31:04',NULL,32.00,'Pending',NULL,'2026-02-11 09:31:04','2026-02-11 09:31:04'),(10,'ORD-20260211113129','عبدالقادر طارق','01070276578','المرج',NULL,1,2,1,'2026-02-11 09:31:29',NULL,32.00,'Delivered',NULL,'2026-02-11 09:31:29','2026-02-11 09:37:36'),(11,'ORD-20260212101652','عبدالقادر طارق','01070276578','المرج',NULL,2,2,13,'2026-02-12 08:16:52',NULL,295.00,'Delivered',NULL,'2026-02-12 08:16:52','2026-02-12 08:17:26'),(12,'ORD-20260212102438','طارق','01229525691','القلج ش المدرسة الثانوية كركز الخانكة القليوبية',NULL,2,2,13,'2026-02-12 08:24:38',NULL,1525.00,'Delivered',NULL,'2026-02-12 08:24:38','2026-02-12 08:26:02'),(13,'ORD-20260212103509','خالد شوقي','01108261455','القلج',NULL,2,2,5,'2026-02-12 08:35:09',NULL,1314.59,'Delivered',NULL,'2026-02-12 08:35:09','2026-02-12 08:35:29');
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `price_history`
--

DROP TABLE IF EXISTS `price_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `price_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` int NOT NULL,
  `old_buy_price` decimal(10,2) DEFAULT NULL,
  `new_buy_price` decimal(10,2) DEFAULT NULL,
  `old_sell_price` decimal(10,2) DEFAULT NULL,
  `new_sell_price` decimal(10,2) DEFAULT NULL,
  `changed_by` int NOT NULL,
  `change_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `notes` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `product_id` (`product_id`),
  KEY `changed_by` (`changed_by`),
  CONSTRAINT `price_history_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `price_history_ibfk_2` FOREIGN KEY (`changed_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `price_history`
--

LOCK TABLES `price_history` WRITE;
/*!40000 ALTER TABLE `price_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `price_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `product_inventory`
--

DROP TABLE IF EXISTS `product_inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `product_inventory` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` int NOT NULL,
  `store_id` int NOT NULL,
  `quantity_in_stock` int NOT NULL DEFAULT '0',
  `minimum_quantity` int DEFAULT '10',
  `last_count_date` datetime DEFAULT NULL,
  `last_counted_by` int DEFAULT NULL,
  `notes` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_product_store` (`product_id`,`store_id`),
  KEY `last_counted_by` (`last_counted_by`),
  KEY `idx_store_quantity` (`store_id`,`quantity_in_stock`),
  CONSTRAINT `product_inventory_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `product_inventory_ibfk_2` FOREIGN KEY (`store_id`) REFERENCES `stores` (`id`),
  CONSTRAINT `product_inventory_ibfk_3` FOREIGN KEY (`last_counted_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=802 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_inventory`
--

LOCK TABLES `product_inventory` WRITE;
/*!40000 ALTER TABLE `product_inventory` DISABLE KEYS */;
INSERT INTO `product_inventory` VALUES (1,1,1,100,20,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-11 09:01:11'),(2,1,2,0,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 10:53:35'),(3,1,3,73,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-07 19:13:41'),(4,2,1,19,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-22 00:14:40'),(5,2,2,63,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:47'),(6,2,3,87,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-31 16:22:16'),(7,3,1,57,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(8,3,2,20,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:47'),(9,3,3,65,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(10,4,1,70,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(11,4,2,30,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:47'),(12,4,3,60,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(13,5,1,51,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(14,5,2,72,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:47'),(15,5,3,86,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(16,6,1,36,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(17,6,2,55,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:47'),(18,6,3,26,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(19,7,1,65,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(20,7,2,42,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:47'),(21,7,3,31,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(22,8,1,25,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(23,8,2,71,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:47'),(24,8,3,93,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(25,9,1,87,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(26,9,2,30,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-05 05:50:18'),(27,9,3,46,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(28,10,1,73,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(29,10,2,23,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-05 05:50:18'),(30,10,3,50,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(31,11,1,95,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(32,11,2,88,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-05 05:50:18'),(33,11,3,50,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(34,12,1,32,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(35,12,2,90,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-05 05:50:18'),(36,12,3,33,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(37,13,1,60,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(38,13,2,79,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-05 05:50:18'),(39,13,3,76,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(40,14,1,50,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(41,14,2,90,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-05 05:50:18'),(42,14,3,45,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(43,15,1,81,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(44,15,2,95,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:47'),(45,15,3,38,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(46,16,1,86,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(47,16,2,90,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:47'),(48,16,3,61,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(49,17,1,40,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(50,17,2,93,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:47'),(51,17,3,33,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(52,18,1,29,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(53,18,2,78,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:47'),(54,18,3,84,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(55,19,1,32,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(56,19,2,28,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:47'),(57,19,3,59,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(58,20,1,94,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(59,20,2,3,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:47'),(60,20,3,49,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(61,21,1,78,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(62,21,2,63,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:47'),(63,21,3,86,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(64,22,1,49,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(65,22,2,8,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:47'),(66,22,3,43,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(67,23,1,36,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(68,23,2,67,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:47'),(69,23,3,79,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(70,24,1,24,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(71,24,2,46,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:47'),(72,24,3,77,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(73,25,1,86,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(74,25,2,73,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:47'),(75,25,3,50,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(76,26,1,96,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(77,26,2,71,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:47'),(78,26,3,68,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(79,27,1,46,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(80,27,2,86,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:47'),(81,27,3,87,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(82,28,1,33,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(83,28,2,37,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:47'),(84,28,3,72,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(85,29,1,76,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(86,29,2,64,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:47'),(87,29,3,52,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(88,30,1,39,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(89,30,2,10,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:47'),(90,30,3,75,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(91,31,1,94,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(92,31,2,87,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:47'),(93,31,3,26,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(94,32,1,29,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(95,32,2,38,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:47'),(96,32,3,78,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(97,33,1,66,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(98,33,2,24,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:47'),(99,33,3,75,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(100,34,1,57,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(101,34,2,72,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:48'),(102,34,3,62,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(103,35,1,79,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(104,35,2,83,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:48'),(105,35,3,96,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(106,36,1,31,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(107,36,2,48,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-02-12 08:39:48'),(108,36,3,61,10,NULL,NULL,NULL,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(159,1,4,-1,10,NULL,NULL,NULL,'2026-01-31 16:32:29','2026-01-31 16:32:29'),(174,37,1,100,10,NULL,NULL,NULL,'2026-01-31 19:06:59','2026-02-11 09:01:02'),(175,37,2,-4,10,NULL,NULL,NULL,'2026-01-31 19:06:59','2026-02-12 08:26:02'),(176,37,3,0,10,NULL,NULL,NULL,'2026-01-31 19:06:59','2026-01-31 19:06:59'),(177,37,4,0,10,NULL,NULL,NULL,'2026-01-31 19:06:59','2026-01-31 19:06:59'),(178,38,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:03:21'),(179,38,2,-2,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-12 08:35:29'),(180,38,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(181,38,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(182,39,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:16:50'),(183,39,2,-2,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-12 08:35:29'),(184,39,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(185,39,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(186,40,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:10:10'),(187,40,2,-1,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-12 08:35:29'),(188,40,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(189,40,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(190,41,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:16:05'),(191,41,2,-2,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-12 08:35:29'),(192,41,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(193,41,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(194,42,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:16:21'),(195,42,2,-1,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-12 08:35:29'),(196,42,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(197,42,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(198,43,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:15:41'),(199,43,2,-2,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-12 08:35:29'),(200,43,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(201,43,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(202,44,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:03:13'),(203,44,2,-1,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-12 08:35:29'),(204,44,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(205,44,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(206,45,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:15:15'),(207,45,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(208,45,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(209,45,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(210,46,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:16:18'),(211,46,2,-2,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-12 08:35:29'),(212,46,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(213,46,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(214,47,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:03:32'),(215,47,2,-2,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-12 08:35:29'),(216,47,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(217,47,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(218,48,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:02:34'),(219,48,2,-1,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-12 08:35:29'),(220,48,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(221,48,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(222,49,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:15:34'),(223,49,2,-2,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-12 08:35:29'),(224,49,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(225,49,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(226,50,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 08:46:03'),(227,50,2,-1,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-12 08:35:29'),(228,50,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(229,50,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(230,51,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:15:18'),(231,51,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(232,51,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(233,51,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(234,52,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:14:46'),(235,52,2,-1,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-12 08:35:29'),(236,52,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(237,52,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(238,53,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:15:50'),(239,53,2,-2,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-12 08:35:29'),(240,53,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(241,53,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(242,54,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:03:26'),(243,54,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(244,54,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(245,54,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(246,55,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 08:52:27'),(247,55,2,-2,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-12 08:35:29'),(248,55,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(249,55,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(250,56,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:16:39'),(251,56,2,-1,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-12 08:35:29'),(252,56,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(253,56,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(254,57,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:01:52'),(255,57,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(256,57,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(257,57,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(258,58,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:02:58'),(259,58,2,-1,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-12 08:35:29'),(260,58,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(261,58,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(262,59,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:16:14'),(263,59,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(264,59,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(265,59,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(266,60,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 08:52:37'),(267,60,2,-2,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-12 08:35:29'),(268,60,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(269,60,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(270,61,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:02:18'),(271,61,2,-1,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-12 08:35:29'),(272,61,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(273,61,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(274,62,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 08:53:12'),(275,62,2,-1,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-12 08:35:29'),(276,62,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(277,62,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(278,63,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 08:45:56'),(279,63,2,-1,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-12 08:35:29'),(280,63,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(281,63,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(282,64,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:16:10'),(283,64,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(284,64,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(285,64,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(286,65,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:16:45'),(287,65,2,-1,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-12 08:35:29'),(288,65,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(289,65,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(290,66,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:16:01'),(291,66,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(292,66,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(293,66,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(294,67,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:01:30'),(295,67,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(296,67,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(297,67,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(298,68,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 08:53:17'),(299,68,2,-1,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-12 08:35:29'),(300,68,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(301,68,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(302,69,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 08:53:08'),(303,69,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(304,69,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(305,69,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(306,70,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:15:02'),(307,70,2,-1,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-12 08:35:29'),(308,70,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(309,70,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(310,71,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 08:53:04'),(311,71,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(312,71,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(313,71,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(314,72,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:02:22'),(315,72,2,-1,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-12 08:35:29'),(316,72,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(317,72,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(318,73,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-02-11 09:16:55'),(319,73,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(320,73,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(321,73,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(322,74,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:15:26'),(323,74,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(324,74,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(325,74,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(326,75,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:03:08'),(327,75,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(328,75,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(329,75,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(330,76,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:03:05'),(331,76,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(332,76,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(333,76,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(334,77,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 08:45:49'),(335,77,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(336,77,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(337,77,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(338,78,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 08:52:56'),(339,78,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(340,78,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(341,78,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(342,79,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 08:45:41'),(343,79,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(344,79,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(345,79,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(346,80,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 08:52:52'),(347,80,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(348,80,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(349,80,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(350,81,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:02:54'),(351,81,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(352,81,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(353,81,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(354,82,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:10:16'),(355,82,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(356,82,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(357,82,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(358,83,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:02:00'),(359,83,2,-1,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-12 08:35:29'),(360,83,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(361,83,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(362,84,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:01:41'),(363,84,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(364,84,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(365,84,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(366,85,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:14:54'),(367,85,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(368,85,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(369,85,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(370,86,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:14:23'),(371,86,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(372,86,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(373,86,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(374,87,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 08:52:22'),(375,87,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(376,87,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(377,87,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(378,88,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:14:42'),(379,88,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(380,88,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(381,88,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(382,89,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:01:20'),(383,89,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(384,89,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(385,89,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(386,90,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:02:46'),(387,90,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(388,90,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(389,90,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(390,91,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:02:42'),(391,91,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(392,91,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(393,91,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(394,92,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:02:12'),(395,92,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(396,92,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(397,92,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(398,93,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:15:44'),(399,93,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(400,93,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(401,93,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(402,94,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:02:09'),(403,94,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(404,94,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(405,94,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(406,95,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:16:42'),(407,95,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(408,95,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(409,95,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(410,96,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:14:37'),(411,96,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(412,96,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(413,96,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(414,97,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 08:53:31'),(415,97,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(416,97,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(417,97,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(418,98,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:02:39'),(419,98,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(420,98,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(421,98,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(422,99,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:15:54'),(423,99,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(424,99,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(425,99,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(426,100,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:15:37'),(427,100,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(428,100,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(429,100,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(430,101,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:15:31'),(431,101,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(432,101,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(433,101,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(434,102,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:02:28'),(435,102,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(436,102,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(437,102,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(438,103,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 08:45:28'),(439,103,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(440,103,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(441,103,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(442,104,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:16:36'),(443,104,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(444,104,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(445,104,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(446,105,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:10:04'),(447,105,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(448,105,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(449,105,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(450,106,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 08:52:48'),(451,106,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(452,106,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(453,106,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(454,107,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:14:32'),(455,107,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(456,107,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(457,107,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(458,108,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:16:26'),(459,108,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(460,108,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(461,108,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(462,109,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:10:21'),(463,109,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(464,109,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(465,109,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(466,110,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 08:52:42'),(467,110,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(468,110,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(469,110,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(470,111,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:15:57'),(471,111,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(472,111,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(473,111,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(474,112,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:14:50'),(475,112,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(476,112,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(477,112,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(478,113,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:15:48'),(479,113,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(480,113,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(481,113,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(482,114,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:14:58'),(483,114,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(484,114,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(485,114,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(486,115,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:03:18'),(487,115,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(488,115,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(489,115,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(490,116,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:01:35'),(491,116,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(492,116,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(493,116,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(494,117,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 08:53:20'),(495,117,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(496,117,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(497,117,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(498,118,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:09:59'),(499,118,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(500,118,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(501,118,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(502,119,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 08:53:23'),(503,119,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(504,119,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(505,119,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(506,120,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:01:45'),(507,120,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(508,120,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(509,120,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(510,121,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:03:37'),(511,121,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(512,121,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(513,121,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(514,122,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 08:52:16'),(515,122,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(516,122,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(517,122,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(518,123,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 08:46:09'),(519,123,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(520,123,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(521,123,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(522,124,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:15:10'),(523,124,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(524,124,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(525,124,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(526,125,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:02:15'),(527,125,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(528,125,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(529,125,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(530,126,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:02:03'),(531,126,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(532,126,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(533,126,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(534,127,1,100,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-02-11 09:01:56'),(535,127,2,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(536,127,3,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(537,127,4,0,10,NULL,NULL,NULL,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(538,128,1,100,10,NULL,NULL,NULL,'2026-02-01 16:21:30','2026-02-11 09:14:18'),(539,128,2,-1,10,NULL,NULL,NULL,'2026-02-01 16:21:30','2026-02-05 06:47:39'),(540,128,3,0,10,NULL,NULL,NULL,'2026-02-01 16:21:30','2026-02-01 16:21:30'),(541,128,4,0,10,NULL,NULL,NULL,'2026-02-01 16:21:30','2026-02-01 16:21:30'),(542,130,1,100,10,NULL,NULL,NULL,'2026-02-01 17:11:48','2026-02-11 09:15:22'),(543,130,2,0,10,NULL,NULL,NULL,'2026-02-01 17:11:48','2026-02-01 17:11:48'),(544,130,3,0,10,NULL,NULL,NULL,'2026-02-01 17:11:48','2026-02-01 17:11:48'),(545,130,4,0,10,NULL,NULL,NULL,'2026-02-01 17:11:48','2026-02-01 17:11:48');
/*!40000 ALTER TABLE `product_inventory` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `product_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `category_id` int NOT NULL,
  `buy_price` decimal(10,2) NOT NULL,
  `sell_price` decimal(10,2) NOT NULL,
  `profit_margin` decimal(5,2) DEFAULT NULL,
  `unit` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'piece',
  `barcode` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `image_path` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `product_code` (`product_code`),
  UNIQUE KEY `barcode` (`barcode`),
  KEY `category_id` (`category_id`),
  KEY `idx_product_code` (`product_code`),
  KEY `idx_barcode` (`barcode`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=131 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (1,'G001','أرز مصري 1 كجم',1,25.00,32.00,NULL,'كجم',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(2,'G002','سكر ناعم 1 كجم',1,22.00,28.00,NULL,'كجم',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(3,'G003','مكرونة الملكة 400 جم',1,8.50,11.00,NULL,'قطعة',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(4,'G004','زيت خليط 1 لتر',1,55.00,68.00,NULL,'لتر',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(5,'G005','سمن كريستال 700 جم',1,45.00,58.00,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(6,'G006','عدس أصفر 500 جم',1,18.00,24.00,NULL,'قطعة',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(7,'G007','دقيق المطبخ 1 كجم',1,16.00,22.00,NULL,'كجم',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(8,'G008','شاي لبتون خرز 250 جم',1,42.00,52.00,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(9,'B001','بيبسي 2.5 لتر',2,24.00,30.00,NULL,'زجاجة',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(10,'B002','مياه معدنية 1.5 لتر',2,5.00,7.00,NULL,'زجاجة',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(11,'B003','عصير جهينة 1 لتر',2,18.00,24.00,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(12,'B004','نيسكافيه 3 في 1',2,4.50,6.00,NULL,'كيس',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(13,'B005','لبن جهينة كامل الدسم 1 لتر',2,32.00,40.00,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(14,'B006','شويبس رمان 1 لتر',2,14.00,18.00,NULL,'زجاجة',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(15,'P001','شامبو هيد آند شودلرز 400 مل',3,65.00,85.00,NULL,'عبوة',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(16,'P002','صابون دوف 125 جم',3,22.00,30.00,NULL,'قطعة',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(17,'P003','معجون أسنان سيجنال 75 مل',3,25.00,35.00,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(18,'P004','جل شعر هير كود 150 مل',3,18.00,25.00,NULL,'عبوة',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(19,'P005','مزيل عرق آكس 150 مل',3,55.00,75.00,NULL,'عبوة',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(20,'D001','مسحوق أريال يدوي 500 جم',4,35.00,48.00,NULL,'كيس',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(21,'D002','بريل منظف أطباق 1 لتر',4,28.00,38.00,NULL,'زجاجة',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(22,'D003','كلوركس أبيض 1 لتر',4,12.00,18.00,NULL,'زجاجة',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(23,'D004','داوني منعم ملابس 1 لتر',4,40.00,55.00,NULL,'زجاجة',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(24,'D005','فلاش ملمع سيراميك',4,15.00,22.00,NULL,'زجاجة',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(25,'S001','شيبسي عائلي',5,8.00,10.00,NULL,'كيس',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(26,'S002','بسكويت أولكر بالتمر',5,4.00,5.00,NULL,'قطعة',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(27,'S003','شوكولاتة جلاكسي سادة',5,18.00,25.00,NULL,'قطعة',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(28,'S004','شيمبوزي 500 جم',5,12.00,15.00,NULL,'كيس',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(29,'S005','كرانشي فلفل وحلو',5,4.50,6.00,NULL,'كيس',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(30,'E001','وصلة شاحن Type-C',9,25.00,45.00,NULL,'قطعة',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(31,'E002','سماعة أذن سلكية',9,35.00,65.00,NULL,'قطعة',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(32,'E003','بطارية ريموت (جوز)',9,10.00,15.00,NULL,'جوز',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(33,'V001','طماطم فريش (كجم)',10,12.00,18.00,NULL,'كجم',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(34,'V002','بطاطس تحمير (كجم)',10,15.00,22.00,NULL,'كجم',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(35,'V003','بصل أحمر (كجم)',10,18.00,25.00,NULL,'كجم',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(36,'V004','موز بلدي (كجم)',10,15.00,20.00,NULL,'كجم',NULL,NULL,NULL,1,'2026-01-21 11:22:02','2026-01-21 11:22:02'),(37,'TEST_FIX_001','Test Fix Product',1,10.00,15.00,NULL,'unit',NULL,NULL,NULL,1,'2026-01-31 19:06:59','2026-01-31 19:06:59'),(38,'6281100590439','رينادا مبيض كلور سائل 3.78لتر',1,18.45,20.45,NULL,'قطعة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(39,'6295120047798','هاربيك منظف المرحاض قالب حافة المرحاض أكتيڤ فريش برائحة أمواج البحر ، 35 جم  (3)',1,18.95,20.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(40,'8697422822741','سمارت فرشاة تنظيف الأحذية',1,7.25,9.25,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(41,'6281101531769','مشوار ماكسي رول مناديل 500م',1,35.95,37.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(42,'6281015005141','موج اكياس حفظ الطعام - 25 حبة',1,5.45,7.45,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(43,'6281065007089','كلوركس منظف متعدد الاستعمالات 750 مل',1,21.95,23.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(44,'5000146059790','ديتول باور منظف الحمامات لإزالة 100٪ من عفن الصابون (يقتل 99.9٪ من الجراثيم) ، زجاجة بزناد لإطلاق الرذاذ - 500 ملل',1,31.95,33.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(45,'4023103129030','فيلدا فرشاة للمراحيض',1,37.00,39.00,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(46,'6295120046807','مناديل ديتول المبللة بعطر الرمان المضادة للبكتريا  لتنظيف الأسطح المتعددة بغطاء قابل لإعادة الإغلاق ، عبوة تحتوي على 80 منديل كبير',1,69.95,71.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(47,'6281006141148','سائل غسيل الصحون من لوكس، أطباق نظيفة ولامعة، بالليمون، قوي على الدهون، لطيف على اليدين، 750 مل',1,12.45,14.45,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(48,'6281006141656','جهاز قياس رقمي الحموضة للسوائل',1,73.00,75.00,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(49,'6281017840399','كارفور مناديل وجه 180 منديل × 10',1,21.95,23.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(50,'6295120005835','إير ويك فريشماتيك رشاش بخاخ أتوماتيكي عبوة إعادة تعبئة ، الورد ، 250 مل',1,55.95,57.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(51,'4003790023538','فيليدا إسفنجة غسيل صحون 3 حبات',1,8.95,10.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(52,'6251001213010','فاين مناديل جيب',1,0.50,0.85,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(53,'6271002113218','كي دي دي حليب طويل الأجل 180مل',1,1.00,1.50,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(54,'2140011000007','زيتون أسود منزوع النواة',1,8.49,10.49,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(55,'6281073160103','السنبلة جبنة موزاريلا مبشورة  1 كجم',1,48.95,50.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(56,'6281057002658','نادك حليب طازج كامل الدسم 800 مل',1,3.00,5.00,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(57,'9009301000352','بوك جبنة شرائح قليلة الدسم  - 200 جرام',1,9.45,11.45,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(58,'9009301000654','دانيت حلوى الفانيليا 75جرام مع كرات الشوكولاتة ×2',1,3.20,5.20,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(59,'2149810000003','مكدوس أردني (للكيلو)',1,10.49,12.49,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(60,'6281022115741','الصافي لبن بنكهة المانجو 340 مل',1,1.00,3.00,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(61,'2140570000005','جبنة إيمنتال الفرنسية',1,19.99,21.99,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(62,'6281007036146','المراعي شرائح جبنة 200جرام × 3 + 1 مجاناً',1,27.95,29.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(63,'6281102721732','إنتاج أجنحة دجاج طازج 450 جرام',1,4.50,6.50,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(64,'2123007000007','مفصل لحم العجل طازج',1,39.48,41.48,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(65,'6281018130383','ندى زبادي يوناني 160 جرام',1,3.70,5.70,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(66,'2000006531759','مخلل فلفل هلابينو',1,4.86,6.86,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(67,'8692971482644','برايد كريمة الطبخ  1 لتر',1,21.95,23.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(68,'6281050510846','امريكانا زينجر روبيان بالبقسماط حار ومقرمش  750 جرام',1,63.95,65.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(69,'5033712160514','الكبير دجاج مفروم مجمد 400 جرام',1,11.50,13.50,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(70,'6271100084274','فوديز بامية زيرو مجمدة 400 جرام',1,13.45,15.45,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(71,'5033712111004','الكبير جمبو هوت دوغ 400 جرام',1,15.00,17.00,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(72,'6223006611573','جرين آيس فراولة مجمدة 1000جرام',1,15.50,17.50,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(73,'6281102685041','هرفي برجر دجاج بالبقسماط 1344 جرام × 24',1,45.50,47.50,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:23','2026-01-31 19:08:23'),(74,'3560071270407','كارفور بطاطس كلاسيك كلاسيك مجمدة خاصة بأربعة فرن 1.5 كج',1,25.95,27.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(75,'3280316007857','دو دجاج كامل 10 × 1300 جرام',1,227.00,229.00,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(76,'6287007092373','دجاج رضوى برجر دجاج بالبقسماط 224 جرام × 4',1,8.95,10.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(77,'6281050114020','أمريكانا 12 برجر الدجاج بالبقسماط 678 جرام',1,29.95,31.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(78,'5033712465503','الكبير برجر دجاج جامبو بالبقسماط 1 كج',1,34.95,36.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(79,'6281050115041','أمريكانا - شيش كباب لحم بقري سوبر 600 جرام (10 قطع)',1,24.45,26.45,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(80,'5203912721000','العملاق الأخضر بازلاء خضراء 450 جرام',1,13.45,15.45,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(81,'6281051099593','داري - بطاطس فرنسية رفيعة 1 كج',1,13.45,15.45,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(82,'7894904256730','سيارا برجر دجاج جامبو بالبقسماط 840 جرام',1,34.95,36.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(83,'6223001531364','بيكو ليتشي 250 جرام',1,6.70,8.70,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(84,'2131304000002','بطيخ اصفر',1,1.00,1.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(85,'2001107000007','فلفل حار اخضر (صحن)',1,4.70,6.70,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(86,'2131303000003','شمام',1,9.13,11.13,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(87,'2131713000006','البرقوق الأحمر',1,30.95,32.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(88,'2131905000005','فاكهة التنين (دراغون فروت) - أحمر',1,7.98,9.98,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(89,'8807889971016','براعم نبتة الفاصوليا 300 جرام',1,7.95,9.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(90,'6287001830117','خيار - علبة 2.8 كج',1,19.95,21.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(91,'2132203000001','خس آيسبيرغ',1,4.73,6.73,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(92,'2000075000002','تفاح رويال جالا عبوة',1,13.45,15.45,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(93,'2000006456557','كمثرى صحن',1,7.95,9.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(94,'2000076000001','تفاح احمر (رد ديليشوس) صحن',1,13.45,15.45,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(95,'6281057012619','نادك طماطم سترابينا 390 جرام',1,14.45,16.45,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(96,'2133101000001','عشب الليمون (للكيلو)',1,7.98,9.98,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(97,'2000004683696','باروك سلطة خس المشكلة 280 جرام مغسول وجاهز للأكل',1,14.45,16.45,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(98,'6281063460633','حدائق اورينت عصير ليمون 1 لتر',1,12.95,14.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(99,'6281003122423','مازولا مايونيز حار عبوة ضاغطة 650 مل',1,22.45,24.45,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(100,'2062630174245','كارفور ميني ويفر الفانيليا 125جرام',1,7.95,9.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(101,'3245412418136','كارفور شوكلاه داكنة 64% 200 جرام',1,10.45,12.45,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(102,'5056036501245','جرينز ملون طعام ازرق 28 مل',1,1.45,3.45,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(103,'0717273509092','أمريكان جاردان صلصة سيزر بالكريمة 473 مل',1,21.45,23.45,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(104,'6281016904382','ميموريز جوي ويفر بالكاكاو 25 جرام',1,1.00,1.25,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(105,'6281016904656','سكر زيادة سكر خشن 5كجم',1,25.50,27.50,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(106,'0617950703341','العلالي ذرة حب حلوة 340 جرام',1,5.20,7.20,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(107,'9310140010151','صنوايت أرز كالروز 1 كج',1,9.95,11.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(108,'6281016904535','ميموريز جوي ويفر بالبندق 25 جرام × 24',1,27.95,29.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(109,'0788821007148','شان مزيج توابل  الدجاج كاري ماسالا 50 جرام',1,3.70,5.70,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(110,'617950200116','العلالي خلطة لقمة القاضي مع الخميرة 453 جرام',1,6.95,8.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(111,'0681250060718','مجدي هيل متوسط 75 جرام',1,27.45,29.45,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(112,'6281063771524','فرشلي مكرونه فوتشيني  454 جرام',1,13.50,15.50,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(113,'6271002203414','كي دي دي 0٪ سكر نكتار جوافة 1 لتر',1,6.20,8.20,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(114,'6281018261469','فلوريدا ناتشورال عصير رمان طبيعي 900مل',1,14.45,16.45,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(115,'6281018261586','ريد بول مشروب طاقة خال من السكر 250مل',1,9.25,11.25,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(116,'5010102241541','بريتفيك مشروب ليمون 300 مل',1,2.25,4.25,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(117,'6281105796218','باجة بن كلاسيك معتدل 50 جرام',1,5.20,7.20,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(118,'5711953026096','ستاربكس موكا فرابوتشينو 250 مل',1,9.75,11.75,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(119,'6281105797642','باجة شاي أخضر فرط 100 جرام',1,5.95,7.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(120,'2132393000003','بطيخ حلو مقطع في كوب',1,5.70,7.70,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(121,'5449000277374','سبرايت 320مل عبوة',1,0.55,2.55,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(122,'6281013131088','ابو جبل شاي العراقة 200 جرام',1,23.95,25.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(123,'3068320111094','إيفيان - مياه معدنية طبيعية 1 لتر',1,13.45,15.45,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(124,'5352101000157','فوستر كلاركس شراب سريع التحضير بالمانجو 2.5 كج',1,55.95,57.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(125,'0012000056109','جاتوريد مشروب بنكهة التوت الأزرق 495 مل × 12',1,74.95,76.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(126,'6281103270055','تانيا مياه 330 مل × 40',1,20.95,22.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(127,'6281101220564','بيرين مياه 12 لتر × 2',1,17.95,19.95,NULL,'علبة',NULL,NULL,NULL,1,'2026-01-31 19:08:24','2026-01-31 19:08:24'),(128,'444444','شاي العروسه',1,9.00,10.00,NULL,'باكو','1',NULL,NULL,1,'2026-02-01 16:21:30','2026-02-01 16:21:30'),(130,'69965868736','قتيلو جبن ملح خفيف',1,210.00,240.00,NULL,'علبة','69965868736',NULL,NULL,1,'2026-02-01 17:11:48','2026-02-01 17:11:48');
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `return_items`
--

DROP TABLE IF EXISTS `return_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `return_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `return_id` int NOT NULL,
  `product_id` int NOT NULL,
  `quantity` int NOT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  `total_price` decimal(12,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `return_id` (`return_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `return_items_ibfk_1` FOREIGN KEY (`return_id`) REFERENCES `sales_returns` (`id`) ON DELETE CASCADE,
  CONSTRAINT `return_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `return_items`
--

LOCK TABLES `return_items` WRITE;
/*!40000 ALTER TABLE `return_items` DISABLE KEYS */;
INSERT INTO `return_items` VALUES (1,1,1,1,32.00,32.00),(2,2,1,1,32.00,32.00),(3,3,6,1,24.00,24.00),(4,4,1,1,32.00,32.00),(5,5,9,1,30.00,30.00),(6,6,1,3,32.00,96.00),(7,7,22,1,18.00,18.00),(8,8,1,1,32.00,32.00);
/*!40000 ALTER TABLE `return_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `role_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `role_name` (`role_name`)
) ENGINE=InnoDB AUTO_INCREMENT=100 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'admin','مدير النظام - يمتلك جميع الصلاحيات','2026-01-19 18:28:58'),(2,'manager','مدير المخزن','2026-01-19 18:28:58'),(3,'cashier','كاشير','2026-01-19 18:28:58'),(4,'call_center','موظف Call Center','2026-01-19 18:28:58'),(5,'warehouse_staff','موظف المخزن','2026-01-19 18:28:58'),(99,'Developer',NULL,'2026-02-09 08:13:56');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sales_returns`
--

DROP TABLE IF EXISTS `sales_returns`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sales_returns` (
  `id` int NOT NULL AUTO_INCREMENT,
  `return_number` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `invoice_id` int NOT NULL,
  `store_id` int NOT NULL,
  `cashier_id` int NOT NULL,
  `return_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `total_return_amount` decimal(12,2) NOT NULL,
  `reason` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `drawer_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `return_number` (`return_number`),
  KEY `invoice_id` (`invoice_id`),
  KEY `store_id` (`store_id`),
  KEY `cashier_id` (`cashier_id`),
  KEY `drawer_id` (`drawer_id`),
  CONSTRAINT `sales_returns_ibfk_1` FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`id`),
  CONSTRAINT `sales_returns_ibfk_2` FOREIGN KEY (`store_id`) REFERENCES `stores` (`id`),
  CONSTRAINT `sales_returns_ibfk_3` FOREIGN KEY (`cashier_id`) REFERENCES `users` (`id`),
  CONSTRAINT `sales_returns_ibfk_4` FOREIGN KEY (`drawer_id`) REFERENCES `drawer_logs` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sales_returns`
--

LOCK TABLES `sales_returns` WRITE;
/*!40000 ALTER TABLE `sales_returns` DISABLE KEYS */;
INSERT INTO `sales_returns` VALUES (1,'RET-20260122004027',7,1,1,'2026-01-21 22:40:27',32.00,'رغبة العميل','2026-01-21 22:40:27',2),(2,'RET-20260122004849',7,2,1,'2026-01-21 22:48:49',32.00,'رغبة العميل','2026-01-21 22:48:49',1),(3,'RET-20260122005926',6,2,1,'2026-01-21 22:59:26',24.00,'رغبة العميل','2026-01-21 22:59:26',1),(4,'RET-20260122010318',6,2,1,'2026-01-21 23:03:18',32.00,'رغبة العميل','2026-01-21 23:03:18',1),(5,'RET-20260202214442',1,2,1,'2026-02-02 19:44:42',30.00,'رغبة العميل','2026-02-02 19:44:42',14),(6,'RET-20260207211047',19,2,8,'2026-02-07 19:10:47',96.00,'رغبة العميل','2026-02-07 19:10:47',14),(7,'RET-20260210194821',1,2,5,'2026-02-10 17:48:21',18.00,'رغبة العميل','2026-02-10 17:48:21',15),(8,'RET-20260212000945',21,2,13,'2026-02-11 22:09:45',32.00,'رغبة العميل','2026-02-11 22:09:45',15);
/*!40000 ALTER TABLE `sales_returns` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stores`
--

DROP TABLE IF EXISTS `stores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stores` (
  `id` int NOT NULL AUTO_INCREMENT,
  `store_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `store_type` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `city` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `manager_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `ip_range_start` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ip_range_end` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `require_ip_check` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stores`
--

LOCK TABLES `stores` WRITE;
/*!40000 ALTER TABLE `stores` DISABLE KEYS */;
INSERT INTO `stores` VALUES (1,'المخزن الرئيسي','Main','القاهرة','شارع النيل','0201234567',NULL,'أحمد محمد',1,'2026-01-19 18:28:58','2026-02-12 06:41:12','192.168.3.0','192.168.3.255',1),(2,'فرع القلج','Branch','الإسكندرية','شارع البحر','0203456789',NULL,'محمد علي',1,'2026-01-19 18:28:58','2026-02-12 06:48:29','192.168.1.0','192.168.1.255',1),(3,'فرع الجيزة','Branch','الجيزة','شارع الهرم','0202345678',NULL,'فاطمة محمود',0,'2026-01-19 18:28:58','2026-02-12 06:48:43','192.168.2.0','192.168.2.255',0),(4,'مدير عام','GM','القاهرة','المقر الرئيسي','01070276578',NULL,'عبدالقادر طارق',0,'2026-01-22 00:11:50','2026-02-08 10:19:42',NULL,NULL,0);
/*!40000 ALTER TABLE `stores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `system_license`
--

DROP TABLE IF EXISTS `system_license`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_license` (
  `id` int NOT NULL AUTO_INCREMENT,
  `hardware_id` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `activation_key` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `activated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `expiry_date` date DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'active',
  PRIMARY KEY (`id`),
  UNIQUE KEY `hardware_id` (`hardware_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_license`
--

LOCK TABLES `system_license` WRITE;
/*!40000 ALTER TABLE `system_license` DISABLE KEYS */;
INSERT INTO `system_license` VALUES (1,'2C32-A7F6-7749-E863','CA63-1FCC-B0B0-99F3','2026-02-09 08:09:03',NULL,'active');
/*!40000 ALTER TABLE `system_license` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `system_settings`
--

DROP TABLE IF EXISTS `system_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `system_settings` (
  `setting_key` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `setting_value` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`setting_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_settings`
--

LOCK TABLES `system_settings` WRITE;
/*!40000 ALTER TABLE `system_settings` DISABLE KEYS */;
INSERT INTO `system_settings` VALUES ('backup_path','backups'),('receipt_footer','شكراً لزيارتكم'),('store_address','عنوان المحل غير محدد'),('store_name','نظام POS المتكامل'),('store_phone','0123456789');
/*!40000 ALTER TABLE `system_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `temporary_invoice_items`
--

DROP TABLE IF EXISTS `temporary_invoice_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `temporary_invoice_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `temp_invoice_id` int NOT NULL,
  `product_id` int NOT NULL,
  `quantity` int NOT NULL,
  `unit_price` decimal(10,2) NOT NULL,
  `discount` decimal(10,2) DEFAULT '0.00',
  `total_price` decimal(12,2) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `temp_invoice_id` (`temp_invoice_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `temporary_invoice_items_ibfk_1` FOREIGN KEY (`temp_invoice_id`) REFERENCES `temporary_invoices` (`id`) ON DELETE CASCADE,
  CONSTRAINT `temporary_invoice_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `temporary_invoice_items`
--

LOCK TABLES `temporary_invoice_items` WRITE;
/*!40000 ALTER TABLE `temporary_invoice_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `temporary_invoice_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `temporary_invoices`
--

DROP TABLE IF EXISTS `temporary_invoices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `temporary_invoices` (
  `id` int NOT NULL AUTO_INCREMENT,
  `temp_invoice_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `store_id` int NOT NULL,
  `cashier_id` int NOT NULL,
  `customer_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `customer_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `customer_address` text COLLATE utf8mb4_unicode_ci,
  `total_amount` decimal(12,2) DEFAULT NULL,
  `saved_by` int NOT NULL,
  `saved_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `notes` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `temp_invoice_code` (`temp_invoice_code`),
  KEY `store_id` (`store_id`),
  KEY `cashier_id` (`cashier_id`),
  KEY `saved_by` (`saved_by`),
  CONSTRAINT `temporary_invoices_ibfk_1` FOREIGN KEY (`store_id`) REFERENCES `stores` (`id`),
  CONSTRAINT `temporary_invoices_ibfk_2` FOREIGN KEY (`cashier_id`) REFERENCES `users` (`id`),
  CONSTRAINT `temporary_invoices_ibfk_3` FOREIGN KEY (`saved_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `temporary_invoices`
--

LOCK TABLES `temporary_invoices` WRITE;
/*!40000 ALTER TABLE `temporary_invoices` DISABLE KEYS */;
/*!40000 ALTER TABLE `temporary_invoices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transfer_items`
--

DROP TABLE IF EXISTS `transfer_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transfer_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `transfer_id` int NOT NULL,
  `product_id` int NOT NULL,
  `quantity_sent` int NOT NULL,
  `quantity_received` int DEFAULT NULL,
  `notes` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `transfer_id` (`transfer_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `transfer_items_ibfk_1` FOREIGN KEY (`transfer_id`) REFERENCES `warehouse_transfers` (`id`) ON DELETE CASCADE,
  CONSTRAINT `transfer_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transfer_items`
--

LOCK TABLES `transfer_items` WRITE;
/*!40000 ALTER TABLE `transfer_items` DISABLE KEYS */;
INSERT INTO `transfer_items` VALUES (1,1,1,41,41,NULL,'2026-01-30 20:05:20'),(2,2,1,1,1,NULL,'2026-01-31 16:17:46'),(3,3,1,20,20,NULL,'2026-02-03 17:16:59'),(4,4,1,20,20,NULL,'2026-02-03 17:26:42'),(5,5,1,20,20,NULL,'2026-02-04 10:01:08'),(6,6,1,1,1,NULL,'2026-02-07 19:02:30'),(7,7,1,10,10,NULL,'2026-02-07 19:03:05');
/*!40000 ALTER TABLE `transfer_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `role_id` int NOT NULL,
  `store_id` int DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1',
  `last_login` timestamp NULL DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `role_id` (`role_id`),
  KEY `store_id` (`store_id`),
  KEY `created_by` (`created_by`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`),
  CONSTRAINT `users_ibfk_2` FOREIGN KEY (`store_id`) REFERENCES `stores` (`id`),
  CONSTRAINT `users_ibfk_3` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'عبدالقادر طارق','admin@posapp.com','$2b$12$LLA1vWCEd/pDwv4lBtThnuG97IS6x/t42Dmts2.ChB9sPmzFFCkWW','01108261455',1,NULL,1,'2026-02-13 11:39:48',NULL,'2026-01-19 18:28:58','2026-02-13 11:39:48'),(2,'عبدالقادر','apdo@gmail.com','$2b$12$u5mW5qsd2nS2PPTyNKrXNeOdKzrWhoQ6dTO3nZ/NcBMBgOFkymLf6','01070276578',3,2,1,'2026-02-14 01:02:25',1,'2026-01-20 23:13:36','2026-02-14 01:02:25'),(3,'محمد طارق','mohamed@pos.com','$2b$12$8T6/xnxiZxOtNiVXjKADSu1xcOXrrZEONwk7I1JAn26bu0cV6hvUu','01552773309',3,3,0,'2026-01-31 16:57:06',1,'2026-01-21 11:25:43','2026-02-11 22:16:27'),(4,'طارق عبدالقادر','tarek@pos.com','$2b$12$cHeNtPPU9hI33wE20L1HneLlmZvOOXF/CJidinp97bMs0TcMfDW4.','01229525691',4,1,0,'2026-01-31 16:19:38',1,'2026-01-21 11:26:40','2026-02-11 22:16:33'),(5,'محمود طلعت','mt@pos.com','$2b$12$IouXnmZi9OGqlERaRpt9Xuo5T8yHKXUCH.gtNyD/pce/bDAKrMZtW','012224552588',2,2,1,'2026-02-13 11:11:17',1,'2026-01-30 20:07:39','2026-02-13 11:11:17'),(8,'طارق هلال','th@pos.com','$2b$12$F0cviQWL6nGd7aer9b7yXurTx4CVw6DW5IbUI1.pstMxfKC4KTerm','01009314678',1,NULL,1,'2026-02-07 19:09:31',1,'2026-02-07 18:56:58','2026-02-08 10:19:42'),(13,'المطور','dev@admin.com','$2b$12$hCgCr5DXy4r84MpNW8r71.geWV/0ya3sYwZ1BIq0ATV2NSRVoxm8G','',99,NULL,1,'2026-02-14 01:18:52',1,'2026-02-09 08:13:56','2026-02-14 01:18:52');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `warehouse_transfers`
--

DROP TABLE IF EXISTS `warehouse_transfers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `warehouse_transfers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `transfer_number` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `from_store_id` int NOT NULL,
  `to_store_id` int NOT NULL,
  `transfer_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `received_date` datetime DEFAULT NULL,
  `created_by` int NOT NULL,
  `received_by` int DEFAULT NULL,
  `status` enum('Pending','In Transit','Received','Cancelled') COLLATE utf8mb4_unicode_ci DEFAULT 'Pending',
  `notes` text COLLATE utf8mb4_unicode_ci,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `transfer_number` (`transfer_number`),
  KEY `from_store_id` (`from_store_id`),
  KEY `to_store_id` (`to_store_id`),
  KEY `created_by` (`created_by`),
  KEY `received_by` (`received_by`),
  KEY `idx_transfer_status` (`status`),
  CONSTRAINT `warehouse_transfers_ibfk_1` FOREIGN KEY (`from_store_id`) REFERENCES `stores` (`id`),
  CONSTRAINT `warehouse_transfers_ibfk_2` FOREIGN KEY (`to_store_id`) REFERENCES `stores` (`id`),
  CONSTRAINT `warehouse_transfers_ibfk_3` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  CONSTRAINT `warehouse_transfers_ibfk_4` FOREIGN KEY (`received_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `warehouse_transfers`
--

LOCK TABLES `warehouse_transfers` WRITE;
/*!40000 ALTER TABLE `warehouse_transfers` DISABLE KEYS */;
INSERT INTO `warehouse_transfers` VALUES (1,'TRF-20260130220520',1,2,'2026-01-30 20:05:20','2026-01-30 22:44:03',1,5,'Received','','2026-01-30 20:05:20','2026-01-30 20:44:03'),(2,'TRF-20260131181746',1,2,'2026-01-31 16:17:46','2026-01-31 18:19:02',1,5,'Received','','2026-01-31 16:17:46','2026-01-31 16:19:02'),(3,'TRF-20260203191659',1,2,'2026-02-03 17:16:59','2026-02-03 19:25:49',1,5,'Received','تجربة 1 تحويلات','2026-02-03 17:16:59','2026-02-03 17:25:49'),(4,'TRF-20260203192642',2,1,'2026-02-03 17:26:42','2026-02-04 11:47:32',5,1,'Received','ارجاع الصنف المحول الي المخزن لعدم وجوده في الطلبية','2026-02-03 17:26:42','2026-02-04 09:47:32'),(5,'TRF-20260204120108',2,3,'2026-02-04 10:01:08','2026-02-07 21:13:41',5,8,'Received','','2026-02-04 10:01:08','2026-02-07 19:13:41'),(6,'TRF-20260207210230',2,1,'2026-02-07 19:02:30','2026-02-07 21:13:37',5,8,'Received','','2026-02-07 19:02:30','2026-02-07 19:13:37'),(7,'TRF-20260207210305',2,1,'2026-02-07 19:03:05','2026-02-07 21:13:32',5,8,'Received','كمية زائدة','2026-02-07 19:03:05','2026-02-07 19:13:32');
/*!40000 ALTER TABLE `warehouse_transfers` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-14  3:20:21
