CREATE TABLE ids_all (id varchar(10) PRIMARY KEY);
CREATE TABLE ids_likes (id varchar(10) PRIMARY KEY);
CREATE TABLE ids_dislikes (id varchar(10) PRIMARY KEY);

CREATE TABLE medium (
    -- picture or video
    id varchar(10) PRIMARY KEY,
    uploaderlink varchar(255), -- user.link
    title varchar(255),
    views int DEFAULT 0,
    favourited int DEFAULT 0,
    time timestamp
);

CREATE TABLE users (
    --userid SERIAL,
    link varchar(255) PRIMARY KEY,
    name varchar(255)
);

CREATE TABLE tags (
    id varchar(10),
    name varchar(255),
    link varchar(255),
    CONSTRAINT c_tags PRIMARY KEY (id,link)
);

CREATE TABLE groups (
    id varchar(10),
    name varchar(255),
    link varchar(255),
    CONSTRAINT c_groups PRIMARY KEY (id,link)
);

CREATE TABLE comments (
    id varchar(10),
    authorlink varchar(255), -- user.link
    time timestamp,
    content varchar(2000)
    --CONSTRAINT c_comments PRIMARY KEY (id,authorlink,time,content)
);

CREATE TABLE also_favourited (
    id varchar(10),
    id_also varchar(10),
    CONSTRAINT c_also_fav PRIMARY KEY (id,id_also)
);

CREATE TABLE predictions (
    id varchar(10) PRIMARY KEY,
    cls int
);

CREATE TABLE file_system (
    id varchar(10),
    path varchar(1023),
    fav bool
);

