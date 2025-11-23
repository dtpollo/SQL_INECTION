CREATE DATABASE testdb;
USE testdb;

-- Users table for login bypass attack
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(50)
);

INSERT INTO users (username, password) VALUES
('admin', 'ADmin#12$'),
('juan', 'Google$'),
('maria', 'MariaTheGrace');

-- Products table for UNION-based SQLi
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10,2)
);

INSERT INTO products (name, price) VALUES
('Laptop', 800.00),
('Mouse', 15.00),
('Keyboard', 30.00);

