-- phpMyAdmin SQL Dump
-- version 5.1.0
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Nov 25, 2022 at 11:38 AM
-- Server version: 10.4.18-MariaDB
-- PHP Version: 8.0.3

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `login_register_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `tbl_user`
--

CREATE TABLE `tbl_user` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `tbl_user`
--
ALTER TABLE `tbl_user`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `tbl_user`
--
ALTER TABLE `tbl_user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;
COMMIT;

------

ALTER TABLE `tbl_user`
ADD `client_number` varchar(100) NOT NULL,;
------

CREATE TABLE `client_request` (
  `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `client_id` INT ,
  `latitude` DECIMAL(9,7) NOT NULL,
  `longitude` DECIMAL(8,7) NOT NULL,
  `destination` VARCHAR(255) NOT NULL,
  `num_places` INT NOT NULL,
  `status` VARCHAR(20) DEFAULT 'pending',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`client_id`) REFERENCES `tbl_user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
);

--
-- Table structure for table `tbl_driver`
--

--
-- Table structure for table `tbl_driver`
--

CREATE TABLE `tbl_driver` (
  `idd` int(11) NOT NULL,
  `firstname` varchar(100) NOT NULL,
  `lastname` varchar(100) NOT NULL,
  `username` varchar(100) NOT NULL,
  `phone_number` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  `registration_number` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `tbl_driver`
--
ALTER TABLE `tbl_driver`
  ADD PRIMARY KEY (`idd`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `tbl_driver`
--
ALTER TABLE `tbl_driver`
  MODIFY `idd` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;
COMMIT;

--------------

INSERT INTO tbl_driver (firstname, lastname, username, phone_number, password, registration_number)
VALUES
    ('d1', 'Doe', 'john@sec', '555-123-4567', 'sec', 'ABC123'),
    ('d2', 'Smith', 'janes@str', '555-987-6543', 'str', 'XYZ789'),
    ('d3', 'Johnson', 'alicej@mypa', '555-555-5555', 'mypa', 'DEF456'),
    ('d4', 'Brown', 'bobb@secre', '555-111-2222', 'secre', 'GHI789'),
    ('d5', 'Lee', 'evelee@letmein', '555-444-3333', 'letmein', 'JKL012');

------------

ALTER TABLE `tbl_driver`
ADD `available` TINYINT(1) DEFAULT 1;


--------------
--
-- Table structure for table `driver_location`
--

CREATE TABLE `driver_location` (
  `id` int(11) NOT NULL,
  `time_date` varchar(20) DEFAULT NULL,
  `latitude` decimal(9,7) DEFAULT NULL,
  `longitude` decimal(8,7) DEFAULT NULL,
  `driver` varchar(3) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `driver_location`
--
ALTER TABLE `driver_location`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `driver_location`
--
ALTER TABLE `driver_location`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;
COMMIT;
--
-- Dumping data for table `driver_location`
--

--------

ALTER TABLE `driver_location`
ADD `driver_id` INT NULL,
ADD CONSTRAINT `fk_driver_id`
    FOREIGN KEY (`driver_id`)
    REFERENCES `tbl_driver`(`idd`)
    ON DELETE SET NULL
    ON UPDATE CASCADE;

--------


UPDATE `driver_location`
SET `driver_id` = (
    SELECT `idd` FROM `tbl_driver`
    WHERE `firstname` = 'd1'
)
WHERE `driver` = 'd1';
----

UPDATE `driver_location`
SET `driver_id` = (
    SELECT `idd` FROM `tbl_driver`
    WHERE `firstname` = 'd2'
)
WHERE `driver` = 'd2';

------

UPDATE `driver_location`
SET `driver_id` = (
    SELECT `idd` FROM `tbl_driver`
    WHERE `firstname` = 'd3'
)
WHERE `driver` = 'd3';


------
UPDATE `driver_location`
SET `driver_id` = (
    SELECT `idd` FROM `tbl_driver`
    WHERE `firstname` = 'd4'
)
WHERE `driver` = 'd4';

------


UPDATE `driver_location`
SET `driver_id` = (
    SELECT `idd` FROM `tbl_driver`
    WHERE `firstname` = 'd5'
)
WHERE `driver` = 'd5';


/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
