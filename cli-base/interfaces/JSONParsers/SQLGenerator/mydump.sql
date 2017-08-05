-- RFIA Database Population
/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


--Organization Table Data;
LOCK TABLES `Organization` WRITE;
/*!40000 ALTER TABLE `Organization` DISABLE KEYS */;
INSERT INTO `Organization` VALUES (4,'Panoptesec-DAM','');
/*!40000 ALTER TABLE `Organization` ENABLE KEYS */;
UNLOCK TABLES;


--Equipment Table Data;
LOCK TABLES `Equipment` WRITE;
/*!40000 ALTER TABLE `Equipment` DISABLE KEYS */;
INSERT INTO `Equipment` VALUES (25,'E1','PEPs_2','Wireless Sensor Networks'),(26,'E2','PEPs_4','IDSs and IPSs'),(27,'E3','PEPs_5','Firewalls'),(28,'E4','PEPs_7','Access Control Mechanisms'),(29,'E5','PEPs_8','System Behavior Monitors'),(30,'E6','PEPs_9','Communication Protocols'),(31,'pppp','PEPs_1','Cryptosystems'),(32,'rrr','PEPs_3','Backup Power Suppliers'),(33,'sss','PEPs_6','Antivirus and Antimalware');
/*!40000 ALTER TABLE `Equipment` ENABLE KEYS */;
UNLOCK TABLES;


--AEV Table Data;
LOCK TABLES `AEV` WRITE;
/*!40000 ALTER TABLE `AEV` DISABLE KEYS */;
INSERT INTO `AEV` VALUES (22,0.0,0.0,0.0,0.0,0.0,1,1000,4,25),(23,0.0,0.0,0.0,0.0,0.0,1,2500,4,26),(24,0.0,0.0,0.0,0.0,0.0,1,2000,4,27),(25,0.0,0.0,0.0,0.0,0.0,1,1500,4,28),(26,0.0,0.0,0.0,0.0,0.0,1,1200,4,29),(27,0.0,0.0,0.0,0.0,0.0,1,500,4,30);
/*!40000 ALTER TABLE `AEV` ENABLE KEYS */;
UNLOCK TABLES;


--Countermeasure Table Data;
LOCK TABLES `Countermeasure` WRITE;
/*!40000 ALTER TABLE `Countermeasure` DISABLE KEYS */;
INSERT INTO `Countermeasure` VALUES (109,'C2','Privilege Separation','Enforce separation of privileges is useful by preventing users to perform actions they are not allowed',0,28),(110,'C10','Active Alert Mode','This countermeasure fires an alert indicating that the control station is suspected to be under attack',0,26),(111,'C1','Disable Remote Connections','Allow only local connections to the control station to authorized users (Switch from \'remote\' to \'not-remote\')',0,27),(112,'C3','Enable Multiple Monitoring','This countermeasure activates two or more monitoring systems to verify the water level indication obtained by the sensors\')',0,29),(113,'C5','Restart Sensor Settings','It erases the current sensor values and request for new thresholds\')',0,30),(114,'C4','Activate Back-up Sensors','Switch \'off\' current sensors and switch \'on\' back-up sensors\')',0,26),(115,'C9','Received Signal Strength','Depending on the position of the attacker, this alternative can be useful to indicate an abnormal behaviour on the system',0,29),(116,'C6','Sensor Tamper Resistance','Activate tamper resistance on each sensor improves effectiveness to prevent hydroelectric power plant hacking attacks',0,25),(117,'C7','Activate Protocol Analysis','Analyse the packets that go in/out the network, verify if the parameters are correct according to specific protocol norms, and stop them if they are classified as suspicious',0,27),(118,'C8','Activate Block-All options','Block all unknown requests if the application is closed',0,27),(119,'C11','Sensor Tampering','',0,25),(120,'C12','Disable Remote Connection','',0,27),(121,'C13','Signal Strength','',0,29),(122,'C14','Clear Sensor','',0,30);
/*!40000 ALTER TABLE `Countermeasure` ENABLE KEYS */;
UNLOCK TABLES;


--ARC Table Data;
LOCK TABLES `ARC` WRITE;
/*!40000 ALTER TABLE `ARC` DISABLE KEYS */;
INSERT INTO `ARC` VALUES (108,0.0,0.0,0.0,0.0,200.0,109),(109,0.0,0.0,0.0,0.0,300.0,110),(110,0.0,0.0,0.0,0.0,500.0,111),(111,0.0,0.0,0.0,0.0,700.0,112),(112,0.0,0.0,0.0,0.0,200.0,113),(113,0.0,0.0,0.0,0.0,400.0,114),(114,0.0,0.0,0.0,0.0,500.0,115),(115,0.0,0.0,0.0,0.0,200.0,116),(116,0.0,0.0,0.0,0.0,200.0,117),(117,0.0,0.0,0.0,0.0,300.0,118),(118,0.0,0.0,0.0,0.0,800.0,119),(119,0.0,0.0,0.0,0.0,500.0,120),(120,0.0,0.0,0.0,0.0,400.0,121),(121,0.0,0.0,0.0,0.0,700.0,122);
/*!40000 ALTER TABLE `ARC` ENABLE KEYS */;
UNLOCK TABLES;


--Incident Table Data;
LOCK TABLES `Incident` WRITE;
/*!40000 ALTER TABLE `Incident` DISABLE KEYS */;
INSERT INTO `Countermeasure` VALUES (27,'A7','Control Station Hacking Threat','A machine succeds in controlling remotely an important asset in the Control Station central','H'),(28,'A5','Hydroelectric Power Plant Hacking Threat','An attacker may intercept and hide the request to the dam control station (using for instance a man-in-the-middle attack to counterfeit and/or delete the request messages). As a result, the dam gates remain open and continue to feed the hydroelectric turbines with water, causing their failure','M'),(29,'A1','Water Level Sensor Compromise Threat','A machine succeds in controlling remotely an important asset in the Control Station central','M');
/*!40000 ALTER TABLE `Incident` ENABLE KEYS */;
UNLOCK TABLES;


--Incident_has_Countermeasure Table Data;
LOCK TABLES `Incident_has_Countermeasure` WRITE;
/*!40000 ALTER TABLE `Incident_has_Countermeasure` DISABLE KEYS */;
INSERT INTO `Incident_has_Countermeasure` VALUES (27,109),(27,111),(27,112),(27,113),(27,114),(28,114),(28,115),(28,116),(28,117),(28,118),(29,119),(29,120),(29,121),(29,122);
/*!40000 ALTER TABLE `Incident_has_Countermeasure` ENABLE KEYS */;
UNLOCK TABLES;


--RM Table Data;
LOCK TABLES `RM` WRITE;
/*!40000 ALTER TABLE `RM` DISABLE KEYS */;
INSERT INTO `RM` VALUES (126,0.7,0.85,0.595,111),(127,0.85,0.75,0.6375,112),(128,0.7,0.55,0.385,113),(129,0.9,0.7,0.63,114),(130,0.75,0.4,0.3,115),(131,0.7,0.75,0.525,116),(132,0.85,0.75,0.6375,117),(133,0.8,0.8,0.64,118),(134,0,0,0.8,119),(135,0,0,0.65,120),(136,0,0,0.4,121),(137,0,0,0.85,122),(138,0.6,0.45,0.27,110),(139,0.8,0.6,0.48,109);
/*!40000 ALTER TABLE `RM` ENABLE KEYS */;
UNLOCK TABLES;


--ALE Table Data;
LOCK TABLES `ALE` WRITE;
/*!40000 ALTER TABLE `ALE` DISABLE KEYS */;
INSERT INTO `ALE` VALUES (27,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1,50000,27,4),(28,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1,50000,28,4);
/*!40000 ALTER TABLE `ALE` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
