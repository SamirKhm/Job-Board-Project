CREATE DATABASE job_board;
USE job_board;

select * from users;
select * from jobs;
select * from resumes;
select * from applications;


-- ---------------- USERS ----------------
CREATE TABLE users (
    user_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    role ENUM('candidate', 'employer'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------------- RESUMES ----------------
CREATE TABLE resumes (
    user_id VARCHAR(50) PRIMARY KEY,
    skills TEXT,
    experience TEXT,
    education TEXT,
    summary TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ---------------- JOBS ----------------
CREATE TABLE jobs (
    job_id VARCHAR(50) PRIMARY KEY,
    employer_id VARCHAR(50),
    title VARCHAR(100),
    description TEXT,
    required_skills TEXT,
    experience_required VARCHAR(50),
    location VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

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
);