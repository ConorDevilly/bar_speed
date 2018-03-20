CREATE TABLE User(
	uid INTEGER AUTO_INCREMENT,
	username VARCHAR(16) UNIQUE NOT NULL,
	password VARCHAR(64) NOT NULL,
	email VARCHAR(64) UNIQUE NOT NULL,
	PRIMARY KEY(uid)
);

CREATE TABLE Video(
	vid INTEGER AUTO_INCREMENT,
	uid INTEGER NOT NULL,
	rpe INTEGER,
	weight FLOAT,
	s3_path TEXT,
	fps FLOAT NOT NULL,
	cm_multiplier FLOAT NOT NULL,
	PRIMARY KEY(vid),
	FOREIGN KEY(uid) REFERENCES User(uid)
);

CREATE TABLE BarDistance(
	vid INT,
	vid_frame INT,
	distance FLOAT,
	FOREIGN KEY (vid) REFERENCES Video(vid),
	PRIMARY KEY(vid, vid_frame)
);

CREATE TABLE VelocityPercentChart(
	reps INTEGER,
	velocity FLOAT(3,2),
	percent INTEGER,
	PRIMARY KEY(reps, velocity),
	CHECK (reps BETWEEN 1 AND 12)
);
