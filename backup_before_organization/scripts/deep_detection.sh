#!/bin/bash

# Deep Technology Detection Script
# Provides multiple command combinations for comprehensive technology detection

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to run deep detection
run_deep_detection() {
    local url="$1"
    local output_file="$2"
    local user_agents="${3:-15}"
    local min_confidence="${4:-5}"
    local max_results="${5:-300}"
    
    print_status "Starting deep detection for: $url"
    print_status "Output file: $output_file"
    print_status "User agents: $user_agents"
    print_status "Min confidence: $min_confidence"
    print_status "Max results: $max_results"
    
    python main.py "$url" \
        --use-dataset --use-whatweb --use-wappalyzer \
        --user-agents "$user_agents" \
        --preferred-browser random \
        --preferred-os windows \
        --min-confidence "$min_confidence" \
        --max-results "$max_results" \
        --timeout 60 \
        --follow-redirects \
        --output csv \
        --save-report "$output_file" \
        --verbose --debug --dump \
        --whatweb-aggression 4 \
        --workers 1 \
        --delay 1.0
    
    if [ $? -eq 0 ]; then
        print_success "Deep detection completed successfully"
        print_status "Results saved to: $output_file"
    else
        print_error "Deep detection failed"
        return 1
    fi
}

# Function to run batch detection
run_batch_detection() {
    local urls_file="$1"
    local output_file="$2"
    local workers="${3:-5}"
    
    print_status "Starting batch detection for: $urls_file"
    print_status "Output file: $output_file"
    print_status "Workers: $workers"
    
    python main.py --batch "$urls_file" \
        --use-dataset --use-whatweb --use-wappalyzer \
        --user-agents 8 \
        --preferred-browser random \
        --min-confidence 10 \
        --max-results 150 \
        --timeout 45 \
        --follow-redirects \
        --output csv \
        --save-report "$output_file" \
        --verbose --debug \
        --whatweb-aggression 4 \
        --workers "$workers" \
        --delay 1.0
    
    if [ $? -eq 0 ]; then
        print_success "Batch detection completed successfully"
        print_status "Results saved to: $output_file"
    else
        print_error "Batch detection failed"
        return 1
    fi
}

# Function to run aggressive detection
run_aggressive_detection() {
    local url="$1"
    local output_file="$2"
    
    print_status "Starting aggressive detection for: $url"
    print_status "Output file: $output_file"
    
    python main.py "$url" \
        --use-dataset --use-whatweb --use-wappalyzer \
        --user-agents 20 \
        --preferred-browser random \
        --preferred-os windows \
        --min-confidence 1 \
        --max-results 500 \
        --timeout 90 \
        --follow-redirects \
        --output csv \
        --save-report "$output_file" \
        --verbose --debug --dump \
        --whatweb-aggression 4 \
        --whatweb-path ./WhatWeb/whatweb \
        --workers 1 \
        --delay 0.2
    
    if [ $? -eq 0 ]; then
        print_success "Aggressive detection completed successfully"
        print_status "Results saved to: $output_file"
    else
        print_error "Aggressive detection failed"
        return 1
    fi
}

# Function to run stealth detection
run_stealth_detection() {
    local url="$1"
    local output_file="$2"
    
    print_status "Starting stealth detection for: $url"
    print_status "Output file: $output_file"
    
    python main.py "$url" \
        --use-dataset --use-whatweb --use-wappalyzer \
        --user-agents 25 \
        --preferred-browser random \
        --preferred-os windows \
        --min-confidence 10 \
        --max-results 150 \
        --timeout 30 \
        --follow-redirects \
        --output csv \
        --save-report "$output_file" \
        --verbose --debug \
        --whatweb-aggression 3 \
        --workers 1 \
        --delay 2.0
    
    if [ $? -eq 0 ]; then
        print_success "Stealth detection completed successfully"
        print_status "Results saved to: $output_file"
    else
        print_error "Stealth detection failed"
        return 1
    fi
}

# Function to run high-confidence detection
run_high_confidence_detection() {
    local url="$1"
    local output_file="$2"
    
    print_status "Starting high-confidence detection for: $url"
    print_status "Output file: $output_file"
    
    python main.py "$url" \
        --use-dataset --use-whatweb --use-wappalyzer \
        --user-agents 5 \
        --preferred-browser chrome \
        --min-confidence 50 \
        --max-results 50 \
        --timeout 30 \
        --follow-redirects \
        --output csv \
        --save-report "$output_file" \
        --verbose \
        --whatweb-aggression 3 \
        --workers 1 \
        --delay 0.5
    
    if [ $? -eq 0 ]; then
        print_success "High-confidence detection completed successfully"
        print_status "Results saved to: $output_file"
    else
        print_error "High-confidence detection failed"
        return 1
    fi
}

# Main function
main() {
    local command="$1"
    local input="$2"
    local output_file="$3"
    
    # Generate timestamp for output files
    local timestamp=$(date +%Y%m%d_%H%M%S)
    
    case "$command" in
        "deep")
            if [ -z "$input" ]; then
                print_error "URL required for deep detection"
                echo "Usage: $0 deep <URL> [output_file]"
                exit 1
            fi
            output_file="${output_file:-deep_detection_${timestamp}.csv}"
            run_deep_detection "$input" "$output_file"
            ;;
        "batch")
            if [ -z "$input" ]; then
                print_error "URLs file required for batch detection"
                echo "Usage: $0 batch <urls_file> [output_file]"
                exit 1
            fi
            output_file="${output_file:-batch_detection_${timestamp}.csv}"
            run_batch_detection "$input" "$output_file"
            ;;
        "aggressive")
            if [ -z "$input" ]; then
                print_error "URL required for aggressive detection"
                echo "Usage: $0 aggressive <URL> [output_file]"
                exit 1
            fi
            output_file="${output_file:-aggressive_detection_${timestamp}.csv}"
            run_aggressive_detection "$input" "$output_file"
            ;;
        "stealth")
            if [ -z "$input" ]; then
                print_error "URL required for stealth detection"
                echo "Usage: $0 stealth <URL> [output_file]"
                exit 1
            fi
            output_file="${output_file:-stealth_detection_${timestamp}.csv}"
            run_stealth_detection "$input" "$output_file"
            ;;
        "high-confidence")
            if [ -z "$input" ]; then
                print_error "URL required for high-confidence detection"
                echo "Usage: $0 high-confidence <URL> [output_file]"
                exit 1
            fi
            output_file="${output_file:-high_confidence_detection_${timestamp}.csv}"
            run_high_confidence_detection "$input" "$output_file"
            ;;
        *)
            echo "Deep Technology Detection Script"
            echo ""
            echo "Usage: $0 <command> <input> [output_file]"
            echo ""
            echo "Commands:"
            echo "  deep <URL>              - Deep detection with maximum fallbacks"
            echo "  batch <urls_file>       - Batch processing with multiple URLs"
            echo "  aggressive <URL>        - Aggressive detection with maximum settings"
            echo "  stealth <URL>           - Stealth detection with high user agent count"
            echo "  high-confidence <URL>   - High-confidence detection (50%+ threshold)"
            echo ""
            echo "Examples:"
            echo "  $0 deep https://example.com"
            echo "  $0 batch urls.txt"
            echo "  $0 aggressive https://example.com aggressive_results.csv"
            echo "  $0 stealth https://example.com stealth_results.csv"
            echo "  $0 high-confidence https://example.com high_conf_results.csv"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
