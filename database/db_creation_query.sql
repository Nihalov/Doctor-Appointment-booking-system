create table doctors(
	id serial primary key,
	name varchar(100) not null,
	availability jsonb,
	speciality varchar(100) not null
	);

select * from doctors;
ALTER SEQUENCE doctors_id_seq RESTART WITH 1;--to start the doctor's id from 1 


create table patients(
	id serial primary key,
	name varchar(200) not null,
	age varchar(50) not null,
	contact int not null
	);

select * from patients;


create table appointments(
	id serial primary key,
	patient_id int references patients(id) on delete cascade,
	doctor_id int references doctors(id) on delete cascade,
	date date not null,
	time time without time zone,
	unique(doctor_id, date, time);--prevents double booking
)

select * from appointments;


