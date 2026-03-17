DROP TABLE IF EXISTS NewsLetterSchools; 
CREATE TABLE NewsLetterSchools
(
    schoolID INT PRIMARY KEY AUTO_INCREMENT, 
    schoolName VARCHAR(255) NOT NULL, 
    town VARCHAR(255) NOT NULL, 


);

DROP TABLE IF EXISTS Newsletters; 
CREATE TABLE Newsletters
(
    schoolID INT,
    nlID INT NOT NULL AUTO_INCREMENT, 
    newsletterName VARCHAR(255) NOT NULL, 
    FOREIGN KEY (schoolID) REFERENCES NewsLetterSchools (schoolID)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
    PRIMARY KEY (schoolID, nlID)

);
