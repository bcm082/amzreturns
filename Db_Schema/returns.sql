-- -------------------------------------------------------------
-- TablePlus 6.2.1(577)
--
-- https://tableplus.com/
--
-- Database: returns_db
-- Generation Time: 2024-12-27 10:52:17.0590
-- -------------------------------------------------------------


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


CREATE TABLE `returns` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Order ID` text,
  `Order date` text,
  `Return request date` text,
  `Return request status` text,
  `Amazon RMA ID` text,
  `Merchant RMA ID` text,
  `Label type` text,
  `Label cost` text,
  `Currency code` text,
  `Return carrier` text,
  `Tracking ID` text,
  `Label to be paid by` text,
  `A-to-Z Claim` text,
  `Is prime` text,
  `ASIN` text,
  `Merchant SKU` text,
  `Item Name` text,
  `Return quantity` int DEFAULT NULL,
  `Return Reason` text,
  `In policy` text,
  `Return type` text,
  `Resolution` text,
  `Invoice number` text,
  `Return delivery date` text,
  `Order Amount` text,
  `Order quantity` int DEFAULT NULL,
  `SafeT Action reason` text,
  `SafeT claim id` text,
  `SafeT claim state` text,
  `SafeT claim creation time` text,
  `SafeT claim reimbursement amount` text,
  `Refunded Amount` text,
  `month` varchar(50) DEFAULT NULL,
  `year` int DEFAULT NULL,
  `last_updated` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=103582 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;