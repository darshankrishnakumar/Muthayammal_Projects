-- Migration V10: Make description and category nullable in requirements
ALTER TABLE `requirements` MODIFY COLUMN `description` TEXT NULL;
