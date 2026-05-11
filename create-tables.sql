CREATE TYPE user_roles AS ENUM ('applicant', 'employer', 'recruiter');
CREATE TYPE match_statuses AS ENUM ('created', 'approved', 'rejected', 'scheduled', 'completed');
CREATE TYPE notification_statuses AS ENUM ('send', 'read');
CREATE TYPE slot_statuses AS ENUM ('available', 'unavailable', 'selected');


CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    user_login VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    user_role user_roles NOT NULL DEFAULT 'applicant',
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL
);


CREATE TABLE resumes (
    resume_id SERIAL PRIMARY KEY,
    applicant_id INTEGER NOT NULL,
    desired_position VARCHAR(255) NOT NULL,
    desired_salary DECIMAL(10,2),
    experience_years INTEGER DEFAULT 0 CHECK (experience_years >= 0),
    skills TEXT,
    education TEXT,
    resume_status BOOLEAN NOT NULL DEFAULT TRUE,

    FOREIGN KEY (applicant_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);


CREATE TABLE vacancies(
    vacancy_id SERIAL PRIMARY KEY,
    employer_id INTEGER NOT NULL,
    title VARCHAR(100) NOT NULL,
    salary DECIMAL(10,2),
    requirements VARCHAR,
    responsibilities VARCHAR,
    vacancy_status BOOLEAN NOT NULL DEFAULT TRUE,

    FOREIGN KEY (employer_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);


CREATE TABLE matches(
    match_id SERIAL PRIMARY KEY,
    resume_id INTEGER,
    vacancy_id INTEGER,
    recruiter_id INTEGER NOT NULL,
    match_status match_statuses NOT NULL DEFAULT 'created',

    FOREIGN KEY (resume_id)
        REFERENCES resumes(resume_id)
        ON DELETE CASCADE,

    FOREIGN KEY (vacancy_id)
        REFERENCES vacancies(vacancy_id)
        ON DELETE CASCADE,

    FOREIGN KEY (recruiter_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    UNIQUE (resume_id, vacancy_id)
);


CREATE TABLE notifications(
    notification_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    notification_type VARCHAR(50),
    message VARCHAR,
    notification_status notification_statuses NOT NULL DEFAULT 'send',

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);


CREATE TABLE interview_slots(
    slot_id SERIAL PRIMARY KEY,
    employer_id INTEGER,
    slot_datetime TIMESTAMP NOT NULL,
    slot_status slot_statuses NOT NULL DEFAULT 'unavailable',

    FOREIGN KEY (employer_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);


CREATE TABLE interviews(
    interview_id SERIAL PRIMARY KEY,
    match_id INTEGER NOT NULL,
    slot_id INTEGER NOT NULL,
    feedback_applicant BOOLEAN NOT NULL DEFAULT FALSE,
    feedback_employer BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (match_id)
        REFERENCES matches(match_id)
        ON DELETE CASCADE,

    FOREIGN KEY (slot_id)
        REFERENCES interview_slots(slot_id)
        ON DELETE CASCADE
);