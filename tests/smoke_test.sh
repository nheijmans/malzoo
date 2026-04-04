#!/bin/bash
#
# MalZoo Smoke Test
# ==================
# Builds the dev Docker image, starts MalZoo, generates test samples,
# submits them via the API, and checks for analysis output.
#
# Usage: ./tests/smoke_test.sh
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
API_URL="http://localhost:1338"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.dev.yml"
CONTAINER_NAME="malzoo-smoke-test"
PASS=0
FAIL=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${YELLOW}[*]${NC} $1"; }
pass() { echo -e "${GREEN}[PASS]${NC} $1"; PASS=$((PASS + 1)); }
fail() { echo -e "${RED}[FAIL]${NC} $1"; FAIL=$((FAIL + 1)); }

cleanup() {
    log "Cleaning up..."
    docker compose -f "$COMPOSE_FILE" -p malzoo-test down -v --remove-orphans 2>/dev/null || true
}
trap cleanup EXIT

# ─── Step 1: Generate test samples ──────────────────────────────────────────
log "Generating test samples..."
python3 "$SCRIPT_DIR/generate_samples.py"
SAMPLE_DIR="$SCRIPT_DIR/samples"

if [ ! -d "$SAMPLE_DIR" ] || [ -z "$(ls -A "$SAMPLE_DIR")" ]; then
    fail "Sample generation failed"
    exit 1
fi
pass "Test samples generated"

# ─── Step 2: Build the dev image ────────────────────────────────────────────
log "Building dev Docker image (this may take a few minutes on first run)..."
docker compose -f "$COMPOSE_FILE" -p malzoo-test build

if [ $? -eq 0 ]; then
    pass "Docker image built"
else
    fail "Docker build failed"
    exit 1
fi

# ─── Step 3: Start MalZoo ───────────────────────────────────────────────────
log "Starting MalZoo..."
docker compose -f "$COMPOSE_FILE" -p malzoo-test up -d

# Wait for API to become ready
log "Waiting for API to come up..."
RETRIES=30
for i in $(seq 1 $RETRIES); do
    if curl -sf "$API_URL/test" > /dev/null 2>&1; then
        break
    fi
    if [ "$i" -eq "$RETRIES" ]; then
        fail "API did not start within ${RETRIES}s"
        log "Container logs:"
        docker compose -f "$COMPOSE_FILE" -p malzoo-test logs
        exit 1
    fi
    sleep 1
done
pass "API is responding"

# ─── Step 4: Health check ───────────────────────────────────────────────────
HEALTH=$(curl -sf "$API_URL/test")
if [ "$HEALTH" = "Test successful!" ]; then
    pass "Health check endpoint"
else
    fail "Health check returned unexpected: $HEALTH"
fi

# ─── Step 5: Submit test samples ────────────────────────────────────────────
log "Submitting test samples..."

submit_sample() {
    local file="$1"
    local tag="$2"
    local basename=$(basename "$file")

    RESPONSE=$(curl -sf -X POST "$API_URL/file/add" \
        -F "file=@$file" \
        -F "tag=$tag" 2>&1) || true

    if echo "$RESPONSE" | grep -q "File submitted for analysis"; then
        pass "Submitted: $basename (tag: $tag)"
    elif echo "$RESPONSE" | grep -q "Sample already"; then
        pass "Submitted (duplicate): $basename"
    else
        fail "Submit failed for $basename: $RESPONSE"
    fi
}

submit_sample "$SAMPLE_DIR/test_executable.exe"  "test-pe"
submit_sample "$SAMPLE_DIR/test_document.doc"     "test-office"
submit_sample "$SAMPLE_DIR/test_archive.zip"      "test-zip"
submit_sample "$SAMPLE_DIR/test_generic.bin"       "test-generic"
submit_sample "$SAMPLE_DIR/eicar.com"              "test-eicar"

# Note: .eml files would normally come through the IMAP supplier,
# but we can still submit via API to test the OtherWorker path
submit_sample "$SAMPLE_DIR/test_email.eml"         "test-email"

# ─── Step 6: Wait for processing ────────────────────────────────────────────
log "Waiting 15s for workers to process samples..."
sleep 15

# ─── Step 7: Check analysis output ──────────────────────────────────────────
log "Checking analysis results..."

# Get the log file from the container
CONTAINER_ID=$(docker compose -f "$COMPOSE_FILE" -p malzoo-test ps -q malzoo)
LOG_CONTENT=$(docker exec "$CONTAINER_ID" bash -c 'cat logs/analysis_results.log.* 2>/dev/null || echo ""')
DEBUG_CONTENT=$(docker exec "$CONTAINER_ID" bash -c 'cat logs/debug.log.* 2>/dev/null || echo ""')

if [ -n "$LOG_CONTENT" ]; then
    pass "Analysis log contains output"

    # Count how many samples produced results
    RESULT_COUNT=$(echo "$LOG_CONTENT" | grep -c "md5" || true)
    log "Found $RESULT_COUNT analysis result(s) in log"

    # Check for specific indicators
    if echo "$LOG_CONTENT" | grep -q "test_executable"; then
        pass "PE analysis result found"
    else
        fail "PE analysis result missing"
    fi

    if echo "$LOG_CONTENT" | grep -q "test_document\|test_generic\|eicar\|test_archive"; then
        pass "Additional analysis results found"
    else
        fail "Other analysis results missing"
    fi
else
    fail "Analysis log is empty — no samples were processed"
fi

# Check debug log for errors
if [ -n "$DEBUG_CONTENT" ]; then
    log "Debug log contents:"
    echo "$DEBUG_CONTENT" | head -20
fi

# Check stored samples
STORED=$(docker exec "$CONTAINER_ID" bash -c 'find storage/ -type f 2>/dev/null | wc -l' | tr -d ' ')
if [ "$STORED" -gt 0 ]; then
    pass "Samples stored in repository ($STORED files)"
else
    fail "No samples in repository"
fi

# ─── Step 8: Show container logs for debugging ──────────────────────────────
log "Container stdout/stderr:"
docker compose -f "$COMPOSE_FILE" -p malzoo-test logs --tail=30

# ─── Summary ────────────────────────────────────────────────────────────────
echo ""
echo "========================================="
echo -e "  Results: ${GREEN}$PASS passed${NC}, ${RED}$FAIL failed${NC}"
echo "========================================="

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
