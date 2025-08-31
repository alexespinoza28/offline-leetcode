-- Database schema for interview coding platform progress tracking
-- SQLite database schema for storing user attempts, problem metadata, and analytics

-- Table for tracking individual solution attempts
CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL,                    -- Problem identifier
    lang TEXT NOT NULL,                    -- Programming language used
    timestamp INTEGER NOT NULL,            -- Unix timestamp of attempt
    status TEXT NOT NULL,                  -- OK/WA/RE/TLE/MLE/CE
    time_ms INTEGER,                       -- Execution time in milliseconds
    memory_mb INTEGER,                     -- Memory usage in megabytes
    test_cases_passed INTEGER DEFAULT 0,   -- Number of test cases passed
    test_cases_total INTEGER DEFAULT 0,    -- Total number of test cases
    commit_sha TEXT,                       -- Git commit SHA if available
    notes TEXT,                           -- Optional user notes
    created_at INTEGER DEFAULT (strftime('%s', 'now')),
    
    -- Indexes for common queries
    FOREIGN KEY (slug) REFERENCES problems_meta(slug)
);

-- Table for problem metadata and statistics
CREATE TABLE IF NOT EXISTS problems_meta (
    slug TEXT PRIMARY KEY,                 -- Problem identifier
    title TEXT,                           -- Problem title
    difficulty TEXT,                      -- Easy/Medium/Hard
    tags TEXT,                           -- Comma-separated tags
    first_seen INTEGER,                   -- When first attempted
    last_attempted INTEGER,               -- Last attempt timestamp
    solved_count INTEGER DEFAULT 0,       -- Number of successful solutions
    total_attempts INTEGER DEFAULT 0,     -- Total number of attempts
    best_time_ms INTEGER,                 -- Best execution time
    best_memory_mb INTEGER,               -- Best memory usage
    last_status TEXT,                     -- Status of most recent attempt
    languages_solved TEXT,               -- Comma-separated list of languages solved in
    created_at INTEGER DEFAULT (strftime('%s', 'now')),
    updated_at INTEGER DEFAULT (strftime('%s', 'now'))
);

-- Table for problem pack registry
CREATE TABLE IF NOT EXISTS pack_registry (
    pack_name TEXT PRIMARY KEY,           -- Unique pack identifier
    version TEXT NOT NULL,                -- Semantic version
    install_date INTEGER NOT NULL,        -- Installation timestamp
    source_url TEXT,                      -- Source URL or path
    problems_count INTEGER DEFAULT 0,     -- Number of problems in pack
    license TEXT,                         -- Pack license
    description TEXT,                     -- Pack description
    author TEXT,                          -- Pack author
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);

-- Table for tracking daily/weekly statistics
CREATE TABLE IF NOT EXISTS statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,                   -- Date in YYYY-MM-DD format
    problems_attempted INTEGER DEFAULT 0, -- Problems attempted on this date
    problems_solved INTEGER DEFAULT 0,    -- Problems solved on this date
    total_time_ms INTEGER DEFAULT 0,      -- Total execution time
    languages_used TEXT,                  -- Comma-separated languages used
    difficulty_breakdown TEXT,            -- JSON: {"Easy": 2, "Medium": 1, "Hard": 0}
    created_at INTEGER DEFAULT (strftime('%s', 'now')),
    
    UNIQUE(date)
);

-- Table for storing user preferences and settings
CREATE TABLE IF NOT EXISTS user_settings (
    key TEXT PRIMARY KEY,                 -- Setting key
    value TEXT NOT NULL,                  -- Setting value (JSON if complex)
    updated_at INTEGER DEFAULT (strftime('%s', 'now'))
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_attempts_slug ON attempts(slug);
CREATE INDEX IF NOT EXISTS idx_attempts_timestamp ON attempts(timestamp);
CREATE INDEX IF NOT EXISTS idx_attempts_status ON attempts(status);
CREATE INDEX IF NOT EXISTS idx_attempts_lang ON attempts(lang);
CREATE INDEX IF NOT EXISTS idx_attempts_slug_lang ON attempts(slug, lang);

CREATE INDEX IF NOT EXISTS idx_problems_difficulty ON problems_meta(difficulty);
CREATE INDEX IF NOT EXISTS idx_problems_last_attempted ON problems_meta(last_attempted);
CREATE INDEX IF NOT EXISTS idx_problems_solved_count ON problems_meta(solved_count);

CREATE INDEX IF NOT EXISTS idx_statistics_date ON statistics(date);

-- Views for common queries
CREATE VIEW IF NOT EXISTS recent_attempts AS
SELECT 
    a.id,
    a.slug,
    p.title,
    p.difficulty,
    a.lang,
    a.status,
    a.time_ms,
    a.memory_mb,
    a.test_cases_passed,
    a.test_cases_total,
    datetime(a.timestamp, 'unixepoch') as attempt_time
FROM attempts a
LEFT JOIN problems_meta p ON a.slug = p.slug
ORDER BY a.timestamp DESC;

CREATE VIEW IF NOT EXISTS problem_stats AS
SELECT 
    p.slug,
    p.title,
    p.difficulty,
    p.tags,
    p.solved_count,
    p.total_attempts,
    CASE 
        WHEN p.total_attempts > 0 
        THEN ROUND((p.solved_count * 100.0) / p.total_attempts, 2)
        ELSE 0 
    END as success_rate,
    p.best_time_ms,
    p.best_memory_mb,
    p.languages_solved,
    datetime(p.first_seen, 'unixepoch') as first_seen_date,
    datetime(p.last_attempted, 'unixepoch') as last_attempted_date
FROM problems_meta p
ORDER BY p.last_attempted DESC;

CREATE VIEW IF NOT EXISTS daily_progress AS
SELECT 
    date,
    problems_attempted,
    problems_solved,
    CASE 
        WHEN problems_attempted > 0 
        THEN ROUND((problems_solved * 100.0) / problems_attempted, 2)
        ELSE 0 
    END as daily_success_rate,
    total_time_ms,
    languages_used,
    difficulty_breakdown
FROM statistics
ORDER BY date DESC;

-- Triggers to maintain data consistency
CREATE TRIGGER IF NOT EXISTS update_problems_meta_on_attempt
AFTER INSERT ON attempts
BEGIN
    -- Try to insert a new problem meta if it doesn't exist
    INSERT OR IGNORE INTO problems_meta (slug, first_seen, last_attempted, total_attempts, solved_count, last_status, updated_at)
    VALUES (NEW.slug, NEW.timestamp, NEW.timestamp, 0, 0, NEW.status, strftime('%s', 'now'));

    -- Update existing problem meta
    UPDATE problems_meta
    SET
        last_attempted = NEW.timestamp,
        total_attempts = total_attempts + 1,
        solved_count = solved_count + (CASE WHEN NEW.status = 'OK' THEN 1 ELSE 0 END),
        last_status = NEW.status,
        best_time_ms = CASE
            WHEN NEW.status = 'OK' AND NEW.time_ms IS NOT NULL THEN
                MIN(NEW.time_ms, COALESCE(best_time_ms, NEW.time_ms))
            ELSE
                best_time_ms
        END,
        best_memory_mb = CASE
            WHEN NEW.status = 'OK' AND NEW.memory_mb IS NOT NULL THEN
                MIN(NEW.memory_mb, COALESCE(best_memory_mb, NEW.memory_mb))
            ELSE
                best_memory_mb
        END,
        updated_at = strftime('%s', 'now')
    WHERE slug = NEW.slug;
END;

CREATE TRIGGER IF NOT EXISTS update_daily_stats_on_attempt
AFTER INSERT ON attempts
BEGIN
    INSERT OR REPLACE INTO statistics (
        date,
        problems_attempted,
        problems_solved,
        total_time_ms,
        languages_used
    )
    VALUES (
        date(NEW.timestamp, 'unixepoch'),
        COALESCE((SELECT problems_attempted FROM statistics WHERE date = date(NEW.timestamp, 'unixepoch')), 0) + 1,
        COALESCE((SELECT problems_solved FROM statistics WHERE date = date(NEW.timestamp, 'unixepoch')), 0) + 
            CASE WHEN NEW.status = 'OK' THEN 1 ELSE 0 END,
        COALESCE((SELECT total_time_ms FROM statistics WHERE date = date(NEW.timestamp, 'unixepoch')), 0) + 
            COALESCE(NEW.time_ms, 0),
        -- Simple language tracking (could be improved)
        NEW.lang
    );
END;

-- Insert default user settings
INSERT OR IGNORE INTO user_settings (key, value) VALUES 
    ('theme', 'dark'),
    ('default_language', 'py'),
    ('auto_save', 'true'),
    ('show_hints', 'true'),
    ('time_format', '24h');

-- Insert some sample data for development (can be removed in production)
INSERT OR IGNORE INTO problems_meta (slug, title, difficulty, tags) VALUES
    ('two-sum', 'Two Sum', 'Easy', 'array,hash-table'),
    ('add-two-numbers', 'Add Two Numbers', 'Medium', 'linked-list,math'),
    ('longest-substring', 'Longest Substring Without Repeating Characters', 'Medium', 'hash-table,string,sliding-window'),
    ('median-sorted-arrays', 'Median of Two Sorted Arrays', 'Hard', 'array,binary-search,divide-conquer');