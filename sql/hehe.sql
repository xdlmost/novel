CREATE TABLE `novel_info` (
  `id` varchar(100) NOT NULL,
  `url` varchar(100) NOT NULL,
  `type` enum('玄幻','仙侠','都市','言情','历史','网游','科幻','恐怖') DEFAULT NULL,
  `title` varchar(100) DEFAULT NULL,
  `author` varchar(100) DEFAULT NULL,
  `frequency` int(11) DEFAULT NULL,
  `last_update_date` datetime DEFAULT NULL,
  `create_date` datetime DEFAULT NULL,
  `hotness` int(11) DEFAULT NULL,
  `last_chapter_id` varchar(100) DEFAULT NULL,
  `last_chapter_title` varchar(100) DEFAULT NULL,
  `last_chapter_date` datetime DEFAULT NULL,
  `last_chapter_index` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8

CREATE TABLE `novel_content` (
  `id` varchar(100) NOT NULL,
  `novelid` varchar(100) NOT NULL,
  `index` int(11) NOT NULL,
  `url` varchar(100) NOT NULL,
  `create_date` datetime DEFAULT NULL,
  `title` varchar(100) DEFAULT NULL,
  `isover` tinyint(1) NOT NULL DEFAULT '0',
  `pid` varchar(100) DEFAULT NULL,
  `nid` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`,`novelid`),
  KEY `novel_content_fk` (`novelid`),
  CONSTRAINT `novel_content_fk` FOREIGN KEY (`novelid`) REFERENCES `novel_info` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8