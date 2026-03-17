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
    newsletterName VARCHAR(255) UNIQUE NOT NULL,
    publishDate VARCHAR(255) NOT NULL,
    recipientEmail VARCHAR(255) NOT NULL,
    FOREIGN KEY (schoolID) REFERENCES NewsLetterSchools (schoolID)
        ON UPDATE CASCADE,
        ON DELETE RESTRICT,
    PRIMARY KEY (schoolID, nlID)

);

DROP TABLE IF EXISS NWSLSubmission; 
CREATE TABLE NWSLSubmission(
    nlID INT NOT NULL, 
    submissionID INT NOT NULL, 
    submissionDate DATETIME NOT NULL, 
    memoText TEXT NOT NULL, 
    FOREIGN KEY (nlID) REFERENCES Newsletters (nlID)
        ON UPDATE RESTRICT
        ON DELETE RESTRICT
    PRIMARY KEY (nlID, submissionID)
); 
