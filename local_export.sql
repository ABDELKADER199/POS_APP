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
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `authorized_devices`
--

LOCK TABLES `authorized_devices` WRITE;
/*!40000 ALTER TABLE `authorized_devices` DISABLE KEYS */;
INSERT INTO `authorized_devices` VALUES (20,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','f9:e7:9c:72:c9:25',NULL,13,1,13,'2026-02-09 08:29:22',NULL,'تسجيل تلقائي للمطور'),(21,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','8f:3f:fd:f7:dd:77',5,NULL,1,NULL,'2026-02-16 14:58:37','2026-02-25 02:15:59','تم الربط تلقائياً عند إنشاء/تعديل فرع جمال الدين'),(22,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','8f:3f:fd:f7:dd:77',5,8,1,13,'2026-02-16 15:00:05','2026-02-16 15:12:05',''),(23,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','f9:e7:9c:72:c9:25',NULL,19,1,13,'2026-02-23 00:34:49','2026-02-23 01:19:46',''),(24,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','f9:e7:9c:72:c9:25',NULL,20,1,13,'2026-02-23 02:12:07','2026-02-24 00:35:17','');
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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'مواد غذائية',NULL,1,'2026-02-25 02:23:20');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address` text COLLATE utf8mb4_unicode_ci,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `current_balance` decimal(12,2) DEFAULT '0.00',
  `credit_limit` decimal(12,2) DEFAULT '0.00',
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `notes` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  UNIQUE KEY `phone` (`phone`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customers`
--

LOCK TABLES `customers` WRITE;
/*!40000 ALTER TABLE `customers` DISABLE KEYS */;
INSERT INTO `customers` VALUES (1,'عميل نقدي','0000000000',NULL,NULL,0.00,0.00,1,'2026-02-25 02:25:59','2026-02-25 02:45:53',NULL),(2,'Test Customer','0501234567','Test Address',NULL,0.00,0.00,1,'2026-02-27 00:25:49','2026-02-27 00:25:49',NULL);
/*!40000 ALTER TABLE `customers` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `drawer_closing_details`
--

LOCK TABLES `drawer_closing_details` WRITE;
/*!40000 ALTER TABLE `drawer_closing_details` DISABLE KEYS */;
INSERT INTO `drawer_closing_details` VALUES (1,1,'1ج',5000,5000.00,'2026-02-25 03:48:15'),(2,1,'Visa',1,1750.00,'2026-02-25 03:48:15');
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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `drawer_logs`
--

LOCK TABLES `drawer_logs` WRITE;
/*!40000 ALTER TABLE `drawer_logs` DISABLE KEYS */;
INSERT INTO `drawer_logs` VALUES (1,5,13,'2026-02-25 02:25:19',0.00,'2026-02-25 05:48:15',5000.00,'Closed',NULL,'2026-02-25 02:25:19','2026-02-25 03:48:15');
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `expenses`
--

LOCK TABLES `expenses` WRITE;
/*!40000 ALTER TABLE `expenses` DISABLE KEYS */;
/*!40000 ALTER TABLE `expenses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `financial_ledger`
--

DROP TABLE IF EXISTS `financial_ledger`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `financial_ledger` (
  `id` int NOT NULL AUTO_INCREMENT,
  `account_type` enum('Customer','Supplier','System','Expense') COLLATE utf8mb4_unicode_ci NOT NULL,
  `account_id` int DEFAULT NULL,
  `transaction_type` enum('Credit','Debit') COLLATE utf8mb4_unicode_ci NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `transaction_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `reference_type` enum('Invoice','Purchase','Payment','Return','Expense') COLLATE utf8mb4_unicode_ci NOT NULL,
  `reference_id` int DEFAULT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `attachment_path` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `is_settlement` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `created_by` (`created_by`),
  CONSTRAINT `financial_ledger_ibfk_1` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `financial_ledger`
--

LOCK TABLES `financial_ledger` WRITE;
/*!40000 ALTER TABLE `financial_ledger` DISABLE KEYS */;
INSERT INTO `financial_ledger` VALUES (1,'Customer',1,'Credit',1000.00,'2026-02-25 02:26:47','Invoice',2,'مديونية فاتورة رقم 2',NULL,13,0),(2,'Customer',1,'Debit',1000.00,'2026-02-25 02:28:09','Payment',NULL,'',NULL,13,0),(3,'Customer',1,'Credit',750.00,'2026-02-25 02:44:55','Invoice',4,'مديونية فاتورة رقم 4',NULL,13,0),(4,'Customer',1,'Debit',750.00,'2026-02-25 02:45:53','Payment',NULL,'',NULL,13,0);
/*!40000 ALTER TABLE `financial_ledger` ENABLE KEYS */;
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
  `buy_price` decimal(10,2) DEFAULT '0.00',
  PRIMARY KEY (`id`),
  KEY `invoice_id` (`invoice_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `invoice_items_ibfk_1` FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`id`) ON DELETE CASCADE,
  CONSTRAINT `invoice_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoice_items`
--

LOCK TABLES `invoice_items` WRITE;
/*!40000 ALTER TABLE `invoice_items` DISABLE KEYS */;
INSERT INTO `invoice_items` VALUES (1,1,1,10,150.00,0.00,1500.00,NULL,'2026-02-25 02:25:59',100.00),(2,1,2,10,75.00,0.00,750.00,NULL,'2026-02-25 02:25:59',50.00),(3,2,1,10,150.00,0.00,1500.00,NULL,'2026-02-25 02:26:47',100.00),(4,2,2,10,75.00,0.00,750.00,NULL,'2026-02-25 02:26:47',50.00),(5,3,1,10,150.00,0.00,1500.00,NULL,'2026-02-25 02:42:49',100.00),(6,4,1,10,150.00,0.00,1500.00,NULL,'2026-02-25 02:44:55',100.00),(7,6,1,2,100.00,0.00,200.00,NULL,'2026-02-27 00:26:46',100.00),(8,8,1,1,50.00,0.00,50.00,NULL,'2026-02-27 00:27:39',100.00);
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
  `customer_id` int DEFAULT NULL,
  `customer_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `customer_phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `customer_address` text COLLATE utf8mb4_unicode_ci,
  `drawer_id` int DEFAULT NULL,
  `invoice_date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `total_amount` decimal(12,2) NOT NULL,
  `paid_amount` decimal(12,2) DEFAULT NULL,
  `remaining_amount` decimal(12,2) DEFAULT NULL,
  `payment_method` enum('Cash','Card','Mixed','Credit') COLLATE utf8mb4_unicode_ci DEFAULT 'Cash',
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
  KEY `fk_inv_cust` (`customer_id`),
  CONSTRAINT `fk_inv_cust` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`),
  CONSTRAINT `invoices_ibfk_1` FOREIGN KEY (`store_id`) REFERENCES `stores` (`id`),
  CONSTRAINT `invoices_ibfk_2` FOREIGN KEY (`cashier_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoices`
--

LOCK TABLES `invoices` WRITE;
/*!40000 ALTER TABLE `invoices` DISABLE KEYS */;
INSERT INTO `invoices` VALUES (1,'1',5,13,1,'Cash Customer','','',1,'2026-02-25 02:25:59',2250.00,NULL,NULL,'Cash','Completed',NULL,'2026-02-25 02:25:59','2026-02-25 02:25:59',2250.00,0.00),(2,'2',5,13,1,'Cash Customer','','',1,'2026-02-25 02:26:47',2250.00,NULL,NULL,'Credit','Completed',NULL,'2026-02-25 02:26:47','2026-02-25 02:26:47',1250.00,0.00),(3,'3',5,13,1,'Cash Customer','','',1,'2026-02-25 02:42:49',1500.00,NULL,NULL,'Cash','Completed',NULL,'2026-02-25 02:42:49','2026-02-25 02:42:49',1500.00,0.00),(4,'4',5,13,1,'Cash Customer','','',1,'2026-02-25 02:44:55',1500.00,NULL,NULL,'Credit','Completed',NULL,'2026-02-25 02:44:55','2026-02-25 02:44:55',750.00,0.00),(5,'5',1,13,2,'Test Customer','0501234567','Test Address',1,'2026-02-27 00:25:49',0.00,NULL,NULL,'Cash','Completed',NULL,'2026-02-27 00:25:49','2026-02-27 00:25:49',0.00,0.00),(6,'6',1,13,2,'Test','0501234567','Test',1,'2026-02-27 00:26:46',200.00,NULL,NULL,'Cash','Completed',NULL,'2026-02-27 00:26:46','2026-02-27 00:26:46',0.00,0.00),(7,'7',1,13,2,'Test','0501234567','Test',1,'2026-02-27 00:27:18',0.00,NULL,NULL,'Cash','Completed',NULL,'2026-02-27 00:27:18','2026-02-27 00:27:18',0.00,0.00),(8,'8',1,13,2,'Test','0501234567','Addr',1,'2026-02-27 00:27:39',50.00,NULL,NULL,'Cash','Completed',NULL,'2026-02-27 00:27:39','2026-02-27 00:27:39',0.00,0.00);
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
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `login_attempts`
--

LOCK TABLES `login_attempts` WRITE;
/*!40000 ALTER TABLE `login_attempts` DISABLE KEYS */;
INSERT INTO `login_attempts` VALUES (1,'th@pos.com',NULL,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-25 02:21:43',0,'بيانات دخول غير صحيحة'),(2,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-25 02:22:00',1,NULL),(3,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-25 02:39:14',1,NULL),(4,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-25 02:47:38',1,NULL),(5,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-25 03:03:24',1,NULL),(6,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-25 03:34:00',1,NULL),(7,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-25 03:43:34',1,NULL),(8,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-25 03:47:30',1,NULL),(9,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-25 03:48:35',1,NULL),(10,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-25 13:37:50',1,NULL),(11,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-25 13:45:26',1,NULL),(12,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-25 13:50:21',1,NULL),(13,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-25 13:54:01',1,NULL),(14,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-25 13:56:36',1,NULL),(15,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-25 13:59:19',1,NULL),(16,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-25 14:01:24',1,NULL),(17,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-25 14:03:58',1,NULL),(18,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-25 14:07:36',1,NULL),(19,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-25 14:16:01',1,NULL),(20,'dev@admin.com',NULL,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-27 00:29:03',0,'بيانات دخول غير صحيحة'),(21,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-02-27 00:29:06',1,NULL),(22,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-03-02 02:00:07',1,NULL),(23,'dev@admin.com',13,'HW_5CD1416BYS_DESKTOP-3649MI1','DESKTOP-3649MI1','192.168.1.6','2026-03-02 02:12:34',1,NULL);
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_items`
--

LOCK TABLES `order_items` WRITE;
/*!40000 ALTER TABLE `order_items` DISABLE KEYS */;
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
  `customer_id` int DEFAULT NULL,
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
  KEY `fk_ord_cust` (`customer_id`),
  CONSTRAINT `fk_ord_cust` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`source_store_id`) REFERENCES `stores` (`id`),
  CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`destination_store_id`) REFERENCES `stores` (`id`),
  CONSTRAINT `orders_ibfk_3` FOREIGN KEY (`call_center_user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `product_inventory`
--

LOCK TABLES `product_inventory` WRITE;
/*!40000 ALTER TABLE `product_inventory` DISABLE KEYS */;
INSERT INTO `product_inventory` VALUES (1,1,1,0,10,NULL,NULL,NULL,'2026-02-25 02:24:52','2026-02-25 02:24:52'),(2,1,5,15,10,NULL,NULL,NULL,'2026-02-25 02:24:52','2026-02-25 03:19:48'),(3,2,1,0,10,NULL,NULL,NULL,'2026-02-25 02:24:52','2026-02-25 02:24:52'),(4,2,5,0,10,NULL,NULL,NULL,'2026-02-25 02:24:52','2026-02-25 02:26:47');
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
  `supplier_id` int DEFAULT NULL,
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
  `last_supplier` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `last_purchase_date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `product_code` (`product_code`),
  UNIQUE KEY `barcode` (`barcode`),
  KEY `category_id` (`category_id`),
  KEY `idx_product_code` (`product_code`),
  KEY `idx_barcode` (`barcode`),
  KEY `fk_product_supplier` (`supplier_id`),
  CONSTRAINT `fk_product_supplier` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (1,'1001','منتج تجريبي 1',1,1,100.00,150.00,NULL,'قطعة',NULL,NULL,NULL,1,'2026-02-25 02:24:52','2026-02-25 02:24:52',NULL,NULL),(2,'1002','منتج تجريبي 2',1,1,50.00,75.00,NULL,'كيلو',NULL,NULL,NULL,1,'2026-02-25 02:24:52','2026-02-25 02:24:52',NULL,NULL);
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purchase_invoices`
--

DROP TABLE IF EXISTS `purchase_invoices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchase_invoices` (
  `id` int NOT NULL AUTO_INCREMENT,
  `invoice_number` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ref_number` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `supplier_id` int DEFAULT NULL,
  `invoice_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `total_amount` decimal(10,2) DEFAULT '0.00',
  `subtotal` decimal(10,2) DEFAULT '0.00',
  `tax_amount` decimal(10,2) DEFAULT '0.00',
  `discount_amount` decimal(10,2) DEFAULT '0.00',
  `payment_method` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'Cash',
  `payment_status` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'paid',
  `paid_amount` decimal(10,2) DEFAULT '0.00',
  `remaining_amount` decimal(10,2) DEFAULT '0.00',
  `status` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'completed',
  `notes` text COLLATE utf8mb4_unicode_ci,
  `created_by` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `supplier_id` (`supplier_id`),
  KEY `created_by` (`created_by`),
  CONSTRAINT `purchase_invoices_ibfk_1` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`),
  CONSTRAINT `purchase_invoices_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchase_invoices`
--

LOCK TABLES `purchase_invoices` WRITE;
/*!40000 ALTER TABLE `purchase_invoices` DISABLE KEYS */;
/*!40000 ALTER TABLE `purchase_invoices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purchase_items`
--

DROP TABLE IF EXISTS `purchase_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchase_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `invoice_id` int DEFAULT NULL,
  `product_id` int DEFAULT NULL,
  `quantity` int NOT NULL,
  `unit_cost` decimal(10,2) NOT NULL,
  `total_cost` decimal(10,2) NOT NULL,
  `tax_percent` decimal(5,2) DEFAULT '0.00',
  `discount_value` decimal(10,2) DEFAULT '0.00',
  `expiry_date` date DEFAULT NULL,
  `production_date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `invoice_id` (`invoice_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `purchase_items_ibfk_1` FOREIGN KEY (`invoice_id`) REFERENCES `purchase_invoices` (`id`),
  CONSTRAINT `purchase_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchase_items`
--

LOCK TABLES `purchase_items` WRITE;
/*!40000 ALTER TABLE `purchase_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `purchase_items` ENABLE KEYS */;
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
  `buy_price` decimal(10,2) DEFAULT '0.00',
  PRIMARY KEY (`id`),
  KEY `return_id` (`return_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `return_items_ibfk_1` FOREIGN KEY (`return_id`) REFERENCES `sales_returns` (`id`) ON DELETE CASCADE,
  CONSTRAINT `return_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `return_items`
--

LOCK TABLES `return_items` WRITE;
/*!40000 ALTER TABLE `return_items` DISABLE KEYS */;
INSERT INTO `return_items` VALUES (1,1,1,5,150.00,750.00,100.00);
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
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sales_returns`
--

LOCK TABLES `sales_returns` WRITE;
/*!40000 ALTER TABLE `sales_returns` DISABLE KEYS */;
INSERT INTO `sales_returns` VALUES (1,'1',4,5,13,'2026-02-25 03:19:48',750.00,'','2026-02-25 03:19:48',1);
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
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stores`
--

LOCK TABLES `stores` WRITE;
/*!40000 ALTER TABLE `stores` DISABLE KEYS */;
INSERT INTO `stores` VALUES (1,'المخزن الرئيسي','Main','القاهرة','شارع النيل','0201234567',NULL,'أحمد محمد',1,'2026-01-19 18:28:58','2026-02-12 06:41:12','192.168.3.0','192.168.3.255',1),(4,'مدير عام','GM','القاهرة','المقر الرئيسي','01070276578',NULL,'عبدالقادر طارق',0,'2026-01-22 00:11:50','2026-02-08 10:19:42',NULL,NULL,0),(5,'جمال الدين','Branch',NULL,NULL,NULL,NULL,NULL,1,'2026-02-16 14:58:37','2026-02-16 14:58:37',NULL,NULL,1);
/*!40000 ALTER TABLE `stores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `suppliers`
--

DROP TABLE IF EXISTS `suppliers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `suppliers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address` text COLLATE utf8mb4_unicode_ci,
  `tax_number` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `opening_balance` decimal(10,2) DEFAULT '0.00',
  `current_balance` decimal(10,2) DEFAULT '0.00',
  `notes` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `is_active` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `suppliers`
--

LOCK TABLES `suppliers` WRITE;
/*!40000 ALTER TABLE `suppliers` DISABLE KEYS */;
INSERT INTO `suppliers` VALUES (1,'عصام عبدالدايم','0123456790','القلج','102030405060708090',0.00,0.00,NULL,'2026-02-25 04:24:38',1);
/*!40000 ALTER TABLE `suppliers` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `system_license`
--

LOCK TABLES `system_license` WRITE;
/*!40000 ALTER TABLE `system_license` DISABLE KEYS */;
INSERT INTO `system_license` VALUES (1,'2C32-A7F6-7749-E863','CA63-1FCC-B0B0-99F3','2026-02-09 08:09:03',NULL,'active'),(2,'9D32-5512-9535-0751','61E4-D65E-2A7F-C490','2026-03-02 01:55:46',NULL,'active');
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
INSERT INTO `system_settings` VALUES ('backup_path','E:/InventoryPOS_Release'),('receipt_footer','شكراً لزيارتكم'),('store_address','القلج ش - مدرسة محمد نجيب'),('store_name','طارق هلال'),('store_phone','0123456789');
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transfer_items`
--

LOCK TABLES `transfer_items` WRITE;
/*!40000 ALTER TABLE `transfer_items` DISABLE KEYS */;
/*!40000 ALTER TABLE `transfer_items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `treasury`
--

DROP TABLE IF EXISTS `treasury`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `treasury` (
  `id` int NOT NULL AUTO_INCREMENT,
  `store_id` int DEFAULT NULL,
  `transaction_type` enum('In','Out') COLLATE utf8mb4_unicode_ci NOT NULL,
  `amount` decimal(12,2) NOT NULL,
  `source_type` enum('Sale','Purchase','Expense','Settlement','Adjustment','Return') COLLATE utf8mb4_unicode_ci NOT NULL,
  `reference_id` int DEFAULT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `created_by` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `store_id` (`store_id`),
  KEY `created_by` (`created_by`),
  CONSTRAINT `treasury_ibfk_1` FOREIGN KEY (`store_id`) REFERENCES `stores` (`id`),
  CONSTRAINT `treasury_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `treasury`
--

LOCK TABLES `treasury` WRITE;
/*!40000 ALTER TABLE `treasury` DISABLE KEYS */;
INSERT INTO `treasury` VALUES (1,NULL,'In',1000.00,'Settlement',2,' (Customer #1)',13,'2026-02-25 02:28:09'),(2,5,'In',2250.00,'Adjustment',NULL,'',13,'2026-02-25 02:40:31'),(3,5,'In',1250.00,'Adjustment',NULL,'',13,'2026-02-25 02:40:46'),(4,5,'Out',3000.00,'Adjustment',NULL,'حساب عصام عبدالدايم المورد ',13,'2026-02-25 02:41:51'),(5,5,'In',1500.00,'Sale',3,'مبيعات نقدية: فاتورة رقم 3',13,'2026-02-25 02:42:49'),(6,5,'In',750.00,'Sale',4,'مبيعات نقدية: فاتورة رقم 4',13,'2026-02-25 02:44:55'),(7,NULL,'In',750.00,'Settlement',4,' (Customer #1)',13,'2026-02-25 02:45:53'),(8,5,'Out',2000.00,'Adjustment',NULL,'',13,'2026-02-25 02:48:59'),(9,5,'In',2250.00,'Sale',1,'مبيعات نقدية: فاتورة رقم 1',13,'2026-02-25 02:25:59'),(10,5,'In',1250.00,'Sale',2,'مبيعات نقدية: فاتورة رقم 2',13,'2026-02-25 02:26:47'),(11,5,'Out',750.00,'Return',1,'مرتجع مبيعات - رقم 1',13,'2026-02-25 03:19:48');
/*!40000 ALTER TABLE `treasury` ENABLE KEYS */;
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
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (13,'المطور','dev@admin.com','$2b$12$hCgCr5DXy4r84MpNW8r71.geWV/0ya3sYwZ1BIq0ATV2NSRVoxm8G','',99,NULL,1,'2026-03-02 02:12:34',1,'2026-02-09 08:13:56','2026-03-02 02:12:34');
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `warehouse_transfers`
--

LOCK TABLES `warehouse_transfers` WRITE;
/*!40000 ALTER TABLE `warehouse_transfers` DISABLE KEYS */;
/*!40000 ALTER TABLE `warehouse_transfers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'stocks'
--

--
-- Dumping routines for database 'stocks'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-02  5:01:07
