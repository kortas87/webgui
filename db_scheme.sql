--
-- Table structure for table `type`
--

CREATE TABLE IF NOT EXISTS `type` (
  `tid` integer primary key autoincrement,
  `name` varchar(64) NOT NULL
);

-- --------------------------------------------------------

--
-- Table structure for table `values`
--

CREATE TABLE IF NOT EXISTS `values` (
  `vid` integer primary key autoincrement,
  `type` integer NOT NULL,
  `index` integer NOT NULL DEFAULT '0',
  `value` float NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO `type` (`tid`, `name`) VALUES
(1, 'voltage cell'),
(2, 'voltage stack'),
(3, 'temperature cell'),
(4, 'current stack'),
(5, 'SOC'),
(6, 'PEC'),
(7, 'voltage cell MIN'),
(8, 'voltage cell MAX'),
(9, 'temperature cell MIN'),
(10, 'temperature cell MAX');
