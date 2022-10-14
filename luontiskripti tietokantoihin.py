CREATE table pahis (
ID int NOT NULL auto_increment,
name varchar(20),
location varchar(20),
primary key (id),
foreign key (location) references airport (ident)
);

CREATE table userinfo (
ID int NOT NULL auto_increment,
user_name varchar(20),
points int(20),
location varchar(20),
primary key (ID),
foreign key (location) references airport (ident)
);
