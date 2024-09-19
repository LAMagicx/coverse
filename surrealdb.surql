-- Create a NAMESPACE if it does not already exist
DEFINE NAMESPACE IF NOT EXISTS test;

-- use NAMESPACE
USE NS test;

-- Create a DATABASE if it does not already exist
DEFINE DATABASE IF NOT EXISTS test;

-- Define the tables
DEFINE TABLE IF NOT EXISTS page SCHEMALESS;
DEFINE TABLE IF NOT EXISTS command SCHEMALESS;

-- Define INDEXES
DEFINE ANALYZER IF NOT EXISTS page_analyzer TOKENIZERS blank,class,camel,punct FILTERS snowball(english);
DEFINE INDEX IF NOT EXISTS page_title ON page FIELDS title SEARCH ANALYZER page_analyzer BM25(1.2,0.75);
DEFINE INDEX IF NOT EXISTS page_text ON page FIELDS text SEARCH ANALYZER page_analyzer BM25(1.2,0.75) HIGHLIGHTS;
DEFINE INDEX IF NOT EXISTS page_id ON TABLE page COLUMNS id UNIQUE;
DEFINE INDEX IF NOT EXISTS command_id ON TABLE command COLUMNS id UNIQUE;
