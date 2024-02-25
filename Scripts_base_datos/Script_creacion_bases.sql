USE estancia;

CREATE TABLE usuarios(
	id_usuario int AUTO_INCREMENT PRIMARY KEY,
    nombre varchar(20) NOT NULL,
    email varchar(20),
    telefono varchar(25),
    contraseña varchar(100) NOT NULL
);

CREATE TABLE roles(
	id_rol int AUTO_INCREMENT PRIMARY KEY,
	nombre_rol VARCHAR(25) NOT NULL,
    descripcion varchar(255)
);

CREATE TABLE permisos(
	id_permiso INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion VARCHAR(255)
);

CREATE TABLE usuario_rol(
	id_usuario int,
    id_rol int,
    foreign key (id_usuario) references usuarios(id_usuario),
    foreign key (id_rol) references roles(id_rol),
    PRIMARY KEY (id_usuario, id_rol)
);

CREATE TABLE rol_permisos(
	id_rol INT,
    id_permiso INT,
    FOREIGN KEY (id_rol) REFERENCES roles(id_rol),
    FOREIGN KEY (id_permiso) REFERENCES permisos(id_permiso),
    PRIMARY KEY (id_rol, id_permiso)
);

