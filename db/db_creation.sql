CREATE DATABASE stockdb;

USE stockdb;

-- Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stocks table
CREATE TABLE stocks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(100),
    sector VARCHAR(100),
    industry VARCHAR(100)
);

-- Stock Prices table
CREATE TABLE stock_prices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    date DATE NOT NULL,
    open_price DECIMAL(10, 2),
    high_price DECIMAL(10, 2),
    low_price DECIMAL(10, 2),
    close_price DECIMAL(10, 2),
    volume BIGINT,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE,
    UNIQUE(stock_id, date)
);

-- API Request Logs table
CREATE TABLE api_request_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    endpoint VARCHAR(255) NOT NULL,
    request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status_code INT,
    response_time_ms INT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);
