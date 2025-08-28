# Requirements Document

## Introduction

This document outlines the requirements for an offline-first, dockerized, multi-language interview coding platform. The system provides a VS Code-based environment for solving coding problems with support for multiple programming languages, automated testing, explanation generation, and GitHub synchronization. The platform is designed to be completely self-contained, running in Docker with no external dependencies during problem-solving sessions.

## Requirements

### Requirement 1: Clean Web Interface

**User Story:** As a developer, I want a clean, focused web interface similar to coding interview platforms, so that I can practice problems without distractions in a familiar interview-style environment.

#### Acceptance Criteria

1. WHEN the application loads THEN the system SHALL display a two-panel layout with problems on the left and editor on the right
2. WHEN a user browses problems THEN the system SHALL show a scrollable list organized by difficulty and tags with problem titles and metadata
3. WHEN a user clicks on a problem THEN the system SHALL load the problem description in the left panel and open the solution editor on the right
4. WHEN a user selects a language THEN the system SHALL switch the Monaco editor to that language with appropriate syntax highlighting and autocomplete
5. WHEN a user clicks Run or Debug THEN the system SHALL execute the solution and display results in a bottom panel with test cases, execution time, and memory usage
6. WHEN test results are available THEN the system SHALL show individual test case results with pass/fail status and expected vs actual output diffs

### Requirement 2: Multi-Language Code Execution

**User Story:** As a developer, I want to write and execute solutions in multiple programming languages with proper compilation and runtime support, so that I can practice problems in my preferred language or learn new languages.

#### Acceptance Criteria

1. WHEN a user selects C language THEN the system SHALL compile using `gcc -O2 -std=c17 main.c -o app` and execute with proper resource limits
2. WHEN a user selects C++ language THEN the system SHALL compile using `g++ -O2 -std=c++17 main.cpp -o app` and execute with proper resource limits
3. WHEN a user selects Python 3 THEN the system SHALL execute using `python3 main.py` with PYTHONHASHSEED=0 for determinism
4. WHEN a user selects Node.js THEN the system SHALL execute using `node main.js` with memory limits
5. WHEN a user selects Java THEN the system SHALL compile using `javac Main.java` and execute using `java -Xmx256m Main`
6. WHEN compilation fails THEN the system SHALL return structured error information with captured stderr
7. WHEN execution occurs THEN the system SHALL enforce time limits (default 2000ms), memory limits (default 256MB), and file descriptor limits

### Requirement 3: Automated Testing Engine

**User Story:** As a developer, I want an automated testing system that can run sample tests, unit tests, and hidden tests with proper result comparison, so that I can validate my solutions thoroughly.

#### Acceptance Criteria

1. WHEN a user runs tests THEN the system SHALL support three test sets: sample, unit, and hidden
2. WHEN comparing outputs THEN the system SHALL support text_exact (trim whitespace), numeric (with tolerance), and JSON (canonicalized) comparison modes
3. WHEN tests execute THEN the system SHALL record execution time, memory usage, and pass/fail status for each test case
4. WHEN test results are available THEN the system SHALL return structured JSON with status, summary statistics, individual case results, and logs
5. WHEN tests fail THEN the system SHALL provide detailed diff information showing expected vs actual output
6. WHEN resource limits are exceeded THEN the system SHALL return appropriate status codes (TIMEOUT, MLE, etc.)

### Requirement 4: Problem Management System

**User Story:** As a problem creator, I want a standardized JSON schema for defining problems with metadata, constraints, and test specifications, so that problems can be consistently managed and validated.

#### Acceptance Criteria

1. WHEN a problem is created THEN the system SHALL require a problem.json file with schema_version, slug, title, difficulty, tags, and io specification
2. WHEN a problem defines constraints THEN the system SHALL validate input parameters against min/max bounds and data types
3. WHEN a problem includes test specifications THEN the system SHALL support deterministic test generation with configurable seeds and test set sizes
4. WHEN a problem is validated THEN the system SHALL check JSON schema compliance, directory structure, and required file existence
5. WHEN a problem supports multiple languages THEN the system SHALL maintain separate solution directories for each language
6. IF a problem uses function mode THEN the system SHALL support language-specific function signatures

### Requirement 5: Deterministic Test Generation

**User Story:** As a problem creator, I want to generate reproducible test cases using seeded random generators, so that test suites remain consistent across different environments and time periods.

#### Acceptance Criteria

1. WHEN generating tests THEN the system SHALL use deterministic generators with fixed seeds specified in problem.json
2. WHEN a generator runs THEN the system SHALL produce identical outputs given the same seed and parameters
3. WHEN test generation completes THEN the system SHALL create both input (.in) and expected output (.out) files by running reference solutions
4. WHEN multiple test sets are defined THEN the system SHALL generate small, medium, and large test cases according to specified constraints
5. WHEN tests are regenerated THEN the system SHALL validate each generated test pair by re-running the reference solution

### Requirement 6: Code Explanation System

**User Story:** As a learner, I want access to explanations of solution approaches and algorithms through community contributions and template-based generation, so that I can understand the reasoning behind correct solutions without requiring AI or internet connectivity.

#### Acceptance Criteria

1. WHEN a user requests explanation THEN the system SHALL first check for community-contributed explanation files (explanation.md) in the problem directory
2. WHEN no community explanation exists THEN the system SHALL generate basic explanations using offline templates based on algorithmic patterns from problem.json metadata
3. WHEN using templates THEN the system SHALL render sections for Algorithm Pattern, Time/Space Complexity, Key Insights, and Common Edge Cases
4. WHEN analyzing code structure THEN the system SHALL optionally extract basic algorithmic components using static analysis (AST for Python)
5. WHEN explanations are displayed THEN the system SHALL output markdown format suitable for VS Code panel display
6. IF community explanations exist THEN the system SHALL prioritize them over generated templates
7. WHEN problem packs are installed THEN the system SHALL include any bundled explanation files from the pack contributors

### Requirement 7: Progress Tracking and Analytics

**User Story:** As a developer, I want to track my problem-solving progress and performance metrics, so that I can monitor my improvement over time.

#### Acceptance Criteria

1. WHEN a solution is executed THEN the system SHALL record attempt details in SQLite database including timestamp, status, execution time, and memory usage
2. WHEN tracking problems THEN the system SHALL maintain metadata including first seen date, difficulty, tags, solved count, and last status
3. WHEN querying progress THEN the system SHALL support retrieval of statistics by problem, language, time period, and success rate
4. WHEN commits are made THEN the system SHALL optionally record commit SHA for correlation with code changes
5. IF analytics are requested THEN the system SHALL support generation of charts showing streaks, pass rates, and performance trends

### Requirement 8: Git Integration and Synchronization

**User Story:** As a developer, I want seamless Git integration with automated validation and synchronization, so that my solutions are properly versioned and validated before being committed.

#### Acceptance Criteria

1. WHEN committing changes THEN the system SHALL run pre-commit validation on all modified problems and solutions
2. WHEN validation runs THEN the system SHALL verify JSON schema compliance, test execution, and compilation for all supported languages
3. WHEN problems are versioned THEN the system SHALL create Git tags following the pattern problem/<slug>@<version>
4. WHEN syncing to GitHub THEN the system SHALL stage appropriate files while excluding tests/hidden and PRIVATE.md files
5. WHEN CI runs THEN GitHub Actions SHALL rebuild the Docker image and re-validate all problems and solutions
6. IF validation fails THEN the system SHALL prevent commits and provide detailed error information

### Requirement 9: Community Problem Packs

**User Story:** As a community member, I want to install and share problem packs with proper licensing and versioning, so that I can access curated problem sets and contribute to the community.

#### Acceptance Criteria

1. WHEN installing a problem pack THEN the system SHALL validate the pack.json manifest including pack name, version, license, and problem list
2. WHEN pack conflicts occur THEN the system SHALL rename problem slugs with pack suffix to avoid collisions
3. WHEN packs are installed THEN the system SHALL maintain a local packs_installed.json registry
4. WHEN contributing problems THEN the system SHALL require original content with appropriate licensing (no copied text)
5. WHEN pack versions change THEN the system SHALL support semantic versioning for problem updates
6. IF multiple packs contain similar problems THEN the system SHALL allow users to choose which version to use

### Requirement 10: Docker Containerization and Security

**User Story:** As a system administrator, I want the entire platform to run securely in Docker containers with proper resource isolation, so that code execution is safe and predictable.

#### Acceptance Criteria

1. WHEN the container starts THEN the system SHALL run a custom web application accessible via web browser on localhost
2. WHEN code executes THEN the system SHALL run as non-root user with restricted permissions
3. WHEN resource limits are enforced THEN the system SHALL use prlimit for CPU, memory, file descriptors, and process limits
4. WHEN network access is restricted THEN the system SHALL optionally disable networking using unshare -n or iptables
5. WHEN temporary files are created THEN the system SHALL use isolated working directories that are cleaned after execution
6. IF security violations are detected THEN the system SHALL terminate processes and log security events

### Requirement 11: Offline-First Architecture

**User Story:** As a developer, I want the platform to work completely offline without external dependencies, so that I can practice coding problems anywhere without internet connectivity.

#### Acceptance Criteria

1. WHEN the platform starts THEN the system SHALL function entirely within the Docker container without external API calls
2. WHEN problems are loaded THEN the system SHALL read all content from local filesystem
3. WHEN explanations are generated THEN the system SHALL use local templates and algorithms without LLM API calls
4. WHEN tests are executed THEN the system SHALL use local language runtimes and testing frameworks
5. WHEN progress is tracked THEN the system SHALL store all data in local SQLite database
6. IF internet connectivity is available THEN the system SHALL optionally sync with Git repositories but SHALL NOT require it for core functionality
