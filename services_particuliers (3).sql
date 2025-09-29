-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1:3306
-- Généré le : lun. 29 sep. 2025 à 22:58
-- Version du serveur : 9.1.0
-- Version de PHP : 8.3.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données : `services_particuliers`
--

-- --------------------------------------------------------

--
-- Structure de la table `categories`
--

DROP TABLE IF EXISTS `categories`;
CREATE TABLE IF NOT EXISTS `categories` (
  `id_categorie` int NOT NULL AUTO_INCREMENT,
  `nom_categorie` varchar(100) NOT NULL,
  `description` text,
  PRIMARY KEY (`id_categorie`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Déchargement des données de la table `categories`
--

INSERT INTO `categories` (`id_categorie`, `nom_categorie`, `description`) VALUES
(1, 'Maison et Bricolage', 'Services liés au bricolage, réparations et entretien de la maison.'),
(2, 'Éducation et apprentissage', 'Cours particuliers, formations et aide scolaire.'),
(3, 'Transport et déplacements', 'Covoiturage, aide au déménagement, livraisons.'),
(4, 'Animaux', 'Services de promenade, garde et soins pour animaux.'),
(5, 'Jardinage', 'Entretien de jardin, tonte de pelouse, plantation.'),
(6, 'Informatique et technologie', 'Dépannage, installation de logiciels, assistance technique.'),
(7, 'Enfance et garde', 'Baby-sitting et garde d’enfants.'),
(8, 'Autres', 'Services divers ne rentrant pas dans les autres catégories.');

-- --------------------------------------------------------

--
-- Structure de la table `services`
--

DROP TABLE IF EXISTS `services`;
CREATE TABLE IF NOT EXISTS `services` (
  `id_service` int NOT NULL AUTO_INCREMENT,
  `id_categorie` int NOT NULL,
  `titre` varchar(50) NOT NULL,
  `description` varchar(2000) NOT NULL,
  `localisation` varchar(50) NOT NULL,
  `date_creation` datetime DEFAULT CURRENT_TIMESTAMP,
  `actif` tinyint(1) DEFAULT '1',
  `cout` decimal(8,2) DEFAULT '0.00',
  `photo` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id_service`),
  KEY `id_categorie` (`id_categorie`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Déchargement des données de la table `services`
--

INSERT INTO `services` (`id_service`, `id_categorie`, `titre`, `description`, `localisation`, `date_creation`, `actif`, `cout`, `photo`) VALUES
(1, 1, 'Montage de meubles IKEA', 'Je monte vos meubles rapidement et proprement.', 'alberta', '2025-09-24 16:35:42', 1, 35.00, 'meubles.jpg'),
(2, 2, 'Cours de piano', 'Cours pour débutants/intermédiaires avec un professeur passionné.', 'Québec', '2025-09-24 16:35:42', 1, 35.00, 'piano.jpg'),
(3, 3, 'Covoiturage Laval-Montréal', 'Trajet régulier chaque matin en semaine.', 'Laval', '2025-09-24 16:35:42', 1, 10.00, 'covoiturage.jpg'),
(4, 4, 'Promenade de chien', 'Promenade de votre chien en soirée et week-end.', 'Sherbrooke', '2025-09-24 16:35:42', 0, 15.01, 'chien.jpg'),
(5, 5, 'Tonte de pelouse', 'Je propose mes services pour entretenir vos espaces verts.', 'Trois-Rivières', '2025-09-24 16:35:42', 1, 20.00, 'pelouse.jpg'),
(6, 6, 'Réparation ordinateur portable', 'Diagnostic et réparation (logiciel et matériel).', 'Gatineau', '2025-09-24 16:35:42', 1, 40.00, 'ordinateur.jpg'),
(7, 7, 'Baby-sitting', 'Disponible le soir et week-end pour garde d’enfants.', 'Montréal', '2025-09-24 16:35:42', 1, 18.00, 'babysitting.jpg'),
(18, 1, 'simons', 'hgvbnjm', 'alberta', '2025-09-29 18:12:47', 0, 9.00, 'wep.jpg');

--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `services`
--
ALTER TABLE `services`
  ADD CONSTRAINT `services_ibfk_1` FOREIGN KEY (`id_categorie`) REFERENCES `categories` (`id_categorie`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
