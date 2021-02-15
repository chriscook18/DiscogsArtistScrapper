-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Feb 15, 2021 at 11:49 PM
-- Server version: 10.4.13-MariaDB
-- PHP Version: 7.4.7

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `discogs`
--
CREATE DATABASE IF NOT EXISTS `discogs` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `discogs`;

-- --------------------------------------------------------

--
-- Table structure for table `releases`
--

CREATE TABLE `releases` (
  `ID` int(11) NOT NULL,
  `PERSON` int(11) NOT NULL,
  `TITLE` varchar(150) NOT NULL,
  `ARTIST` varchar(100) NOT NULL,
  `YEAR` int(11) NOT NULL,
  `MASTERID` int(11) NOT NULL,
  `COUNTRY` varchar(50) NOT NULL,
  `ADDEDTODB` timestamp NOT NULL DEFAULT current_timestamp(),
  `LASTUPDATEDB` timestamp NOT NULL DEFAULT current_timestamp(),
  `ADDEDTODISCOGS` timestamp NOT NULL DEFAULT current_timestamp(),
  `LASTUPDATEDISCOGS` timestamp NOT NULL DEFAULT current_timestamp(),
  `ROLE` varchar(50) NOT NULL,
  `LABEL` varchar(100) NOT NULL,
  `CATALOGNO` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `songs`
--

CREATE TABLE `songs` (
  `RELEASEID` int(11) NOT NULL,
  `SONGTITLE` varchar(150) NOT NULL,
  `SONGARTIST` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `releases`
--
ALTER TABLE `releases`
  ADD UNIQUE KEY `ID` (`ID`,`PERSON`) USING BTREE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
