-- phpMyAdmin SQL Dump
-- version 4.8.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 30, 2019 at 09:26 PM
-- Server version: 10.1.37-MariaDB
-- PHP Version: 7.3.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `shopfooddb`
--

-- --------------------------------------------------------

--
-- Table structure for table `account`
--

CREATE TABLE `account` (
  `id` int(11) NOT NULL,
  `name` varchar(30) NOT NULL,
  `email` varchar(30) NOT NULL,
  `username` varchar(20) NOT NULL,
  `password` varchar(100) NOT NULL,
  `status` enum('admin','member') NOT NULL DEFAULT 'member',
  `phone` varchar(10) NOT NULL,
  `city` text NOT NULL,
  `register_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `account`
--

INSERT INTO `account` (`id`, `name`, `email`, `username`, `password`, `status`, `phone`, `city`, `register_date`) VALUES
(1, 'DDoS', 'tankhim541@gmail.com', 'admin', '$5$rounds=535000$evqWjRUheq844jYZ$9x/2ICvmpVdRx.7hKh0NuWR07tfwXG0lvvGr9NddVV6', 'admin', '0611138083', '255/55 ม.18 อ.เมือง ต.ข้ามใหญ่ อ.เมือง จ.อุบล', '2019-03-19 14:01:25'),
(2, 'Suphamongkhon Khotasit', 'tankhim541@gmail.com', 'DDoS', '$5$rounds=535000$gAYzjLdkxr3WeRBq$ofKaFUSpQTsjHyHtYg3VEy1Qa2xIWmiHKocLFm7s0C5', 'member', '0611138083', '-', '2019-03-19 19:09:17'),
(3, 'fah', 'fafafa@gmail.com', 'fafafa', '$5$rounds=535000$kE5umvuTe3TyUQ/9$DfR6.8wDG0w.96pZZ0J6qWkNaAQmVPRfy4Y7V51WkS7', 'member', '0888888888', '-', '2019-03-26 08:11:45'),
(4, 'James', 'James@gmail.com', 'James', '$5$rounds=535000$atc4ADhE350WYonJ$Vgf70xpb4HjQ2qSv77TPbgjgK8D2AnOQEbaGS2g.vgD', 'member', '0123456789', '255/55 ม.18 อ.เมือง ต.ข้ามใหญ่ อ.เมือง จ.อุบล', '2019-03-30 05:50:28'),
(5, 'gg', 'gg@gg.com', 'greathoo', '$5$rounds=535000$J5EUEzEMqw3kELVw$ubHnNrY0tkdmaaYeEAbBhkSBI10Uk6Pkt8mxdYDilZ6', 'member', '0123456789', 'my home na ja', '2019-03-30 07:44:03');

-- --------------------------------------------------------

--
-- Table structure for table `data_mess`
--

CREATE TABLE `data_mess` (
  `id` int(11) NOT NULL,
  `status` enum('review','support','recommended') NOT NULL,
  `status_r` enum('unread','read') NOT NULL DEFAULT 'unread',
  `star` enum('1','2','3','4','5') NOT NULL,
  `user` varchar(100) NOT NULL,
  `email` varchar(50) NOT NULL,
  `title` varchar(100) NOT NULL,
  `menu` enum('สเต็กหมู','สเต็กปลา','สเต็กไก่','สเต็กซี่โครงหมู') NOT NULL,
  `messages` text NOT NULL,
  `comments_datetime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `orderdb`
--

CREATE TABLE `orderdb` (
  `id` int(20) NOT NULL,
  `customer` varchar(100) NOT NULL,
  `menu` varchar(30) NOT NULL,
  `price` int(10) NOT NULL,
  `status` enum('Wait','Accept','Sending','completed') NOT NULL DEFAULT 'Wait',
  `city` varchar(50) NOT NULL,
  `order_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `orderdb`
--

INSERT INTO `orderdb` (`id`, `customer`, `menu`, `price`, `status`, `city`, `order_date`) VALUES
(1, 'greathoo', 'สเต็กหมู', 79, 'Sending', 'my home na ja', '2019-03-30 07:44:21');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `account`
--
ALTER TABLE `account`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `data_mess`
--
ALTER TABLE `data_mess`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `orderdb`
--
ALTER TABLE `orderdb`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `account`
--
ALTER TABLE `account`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `data_mess`
--
ALTER TABLE `data_mess`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `orderdb`
--
ALTER TABLE `orderdb`
  MODIFY `id` int(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
