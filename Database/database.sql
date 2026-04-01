<<<<<<< HEAD
CREATE DATABASE job_board;
USE job_board;

-- ---------------- USERS ----------------
CREATE TABLE users (
    user_id VARCHAR(50) PRIMARY KEY,
=======
create database job_board;
use job_board;

CREATE TABLE Users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
>>>>>>> ab5973e3bb7c12e213dabda389050c17ea384afc
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    role ENUM('candidate', 'employer'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

<<<<<<< HEAD
-- ---------------- RESUMES ----------------
CREATE TABLE resumes (
    user_id VARCHAR(50) PRIMARY KEY,
=======
CREATE TABLE Resumes (
    resume_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    file_path VARCHAR(255),
    extracted_text TEXT,
>>>>>>> ab5973e3bb7c12e213dabda389050c17ea384afc
    skills TEXT,
    experience TEXT,
    education TEXT,
    summary TEXT,
<<<<<<< HEAD
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ---------------- JOBS ----------------
CREATE TABLE jobs (
    job_id VARCHAR(50) PRIMARY KEY,
    employer_id VARCHAR(50),
=======
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Jobs (
    job_id INT PRIMARY KEY AUTO_INCREMENT,
    employer_id INT,
>>>>>>> ab5973e3bb7c12e213dabda389050c17ea384afc
    title VARCHAR(100),
    description TEXT,
    required_skills TEXT,
    experience_required VARCHAR(50),
    location VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

<<<<<<< HEAD
    FOREIGN KEY (employer_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ---------------- APPLICATIONS ----------------
CREATE TABLE applications (
    application_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50),
    job_id VARCHAR(50),
    status ENUM('applied', 'shortlisted', 'rejected') DEFAULT 'applied',
    match_score FLOAT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
=======
    FOREIGN KEY (employer_id) REFERENCES Users(user_id)
);

CREATE TABLE Applications (
    application_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    job_id INT,
    status ENUM('applied', 'shortlisted', 'rejected'),
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (job_id) REFERENCES Jobs(job_id)
);

CREATE TABLE Matches (
    match_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    job_id INT,
    match_score INT,
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (job_id) REFERENCES Jobs(job_id)
>>>>>>> ab5973e3bb7c12e213dabda389050c17ea384afc
);