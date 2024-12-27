-- -------------------------------------------------------------
-- TablePlus 6.2.1(577)
--
-- https://tableplus.com/
--
-- Database: returns_db
-- Generation Time: 2024-12-27 10:52:55.9390
-- -------------------------------------------------------------


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


CREATE TABLE `sales` (
  `id` int NOT NULL AUTO_INCREMENT,
  `amazon_order_id` text,
  `merchant_order_id` text,
  `purchase_date` text,
  `last_updated_date` text,
  `order_status` text,
  `fulfillment_channel` text,
  `sales_channel` text,
  `order_channel` text,
  `url` text,
  `ship_service_level` text,
  `product_name` text,
  `sku` text,
  `asin` text,
  `number_of_items` float DEFAULT NULL,
  `item_status` text,
  `tax_collection_model` text,
  `tax_collection_responsible_party` text,
  `quantity` int DEFAULT NULL,
  `currency` text,
  `item_price` float DEFAULT NULL,
  `item_tax` float DEFAULT NULL,
  `shipping_price` float DEFAULT NULL,
  `shipping_tax` float DEFAULT NULL,
  `gift_wrap_price` float DEFAULT NULL,
  `gift_wrap_tax` float DEFAULT NULL,
  `item_promotion_discount` float DEFAULT NULL,
  `ship_promotion_discount` float DEFAULT NULL,
  `ship_city` text,
  `ship_state` text,
  `ship_postal_code` text,
  `ship_country` text,
  `promotion_ids` text,
  `payment_method_details` text,
  `is_business_order` tinyint(1) DEFAULT NULL,
  `purchase_order_number` text,
  `price_designation` text,
  `customized_url` text,
  `customized_page` text,
  `signature_confirmation_recommended` tinyint(1) DEFAULT NULL,
  `month` varchar(50) DEFAULT NULL,
  `year` int DEFAULT NULL,
  `last_updated` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1060670 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;