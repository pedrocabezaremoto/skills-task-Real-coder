#!/bin/bash
# run.sh - Entry point for the test suite

set -e

echo "Starting Test Execution..."

# 1. Prepare codebase (if it exists)
if [ -f "codebase.zip" ]; then
    echo "Unzipping codebase..."
    unzip -o codebase.zip -d .
fi

# 2. Prepare tests
if [ -f "tests.zip" ]; then
    echo "Unzipping tests..."
    unzip -o tests.zip -d .
fi

# 3. RUN TESTS
# For Kotlin/Gradle, we use the gradle test command.
# We use --continue to ensure all tests run even if some fail (TDD requirement).
echo "Running Gradle tests..."
./gradlew test --continue || true

# 4. Final log for parsing
echo "Test execution finished."
