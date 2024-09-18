-- Create a NAMESPACE if it does not already exist
DEFINE NAMESPACE IF NOT EXISTS test;

-- use NAMESPACE
USE NS test;

-- Create a DATABASE if it does not already exist
DEFINE DATABASE IF NOT EXISTS test;

-- Define the tables
DEFINE TABLE page SCHEMALESS;
DEFINE TABLE command SCHEMALESS;
