#!/bin/bash

# MongoDB Migration Script using mongodump/mongorestore
# This script migrates data from local MongoDB to cloud MongoDB using official tools

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DEFAULT_SOURCE_URI=mongodb://admin:secret@localhost:27017
DEFAULT_SOURCE_DB=newsletter-generation-service
DEFAULT_DUMP_DIR=./mongodb_dump
DEFAULT_AUTH_DB=admin

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to show usage
show_usage() {
    echo "MongoDB Migration Script (using mongodump/mongorestore)"
    echo ""
    echo "Usage:"
    echo "  $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  dump <target-dir>                    Dump local database to directory"
    echo "  restore <source-dir> <target-uri>    Restore dump to cloud MongoDB"
    echo "  migrate <target-uri> <target-db>     Dump and restore in one step"
    echo "  help                                 Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 dump ./backup"
    echo "  $0 restore ./backup mongodb+srv://user:pass@cluster.mongodb.net"
    echo "  $0 migrate mongodb+srv://user:pass@cluster.mongodb.net newsletter_prod"
    echo ""
    echo "Environment Variables:"
    echo "  SOURCE_URI     Source MongoDB URI (default: mongodb://localhost:27017)"
    echo "  SOURCE_DB      Source database name (default: newsletter_agent)"
    echo "  DUMP_DIR       Default dump directory (default: ./mongodb_dump)"
    echo ""
    echo "Prerequisites:"
    echo "  - mongodump and mongorestore must be installed"
    echo "  - For macOS: brew install mongodb/brew/mongodb-database-tools"
    echo "  - For Ubuntu: sudo apt-get install mongodb-database-tools"
}

# Function to check if mongodump/mongorestore are available
check_tools() {
    if ! command -v mongodump &> /dev/null; then
        print_error "mongodump is not installed"
        echo "Install MongoDB Database Tools:"
        echo "  macOS: brew install mongodb/brew/mongodb-database-tools"
        echo "  Ubuntu: sudo apt-get install mongodb-database-tools"
        exit 1
    fi
    
    if ! command -v mongorestore &> /dev/null; then
        print_error "mongorestore is not installed"
        echo "Install MongoDB Database Tools:"
        echo "  macOS: brew install mongodb/brew/mongodb-database-tools"
        echo "  Ubuntu: sudo apt-get install mongodb-database-tools"
        exit 1
    fi
    
    print_success "MongoDB tools are available"
}

# Function to dump database
dump_database() {
    local target_dir="$1"
    local source_uri="${SOURCE_URI:-$DEFAULT_SOURCE_URI}"
    local source_db="${SOURCE_DB:-$DEFAULT_SOURCE_DB}"
    
    print_info "Dumping database from $source_uri/$source_db to $target_dir"
    
    # Create dump directory if it doesn't exist
    mkdir -p "$target_dir"
    
    # Run mongodump
    local auth_db="${AUTH_DB:-$DEFAULT_AUTH_DB}"
    mongodump \
        --uri="$source_uri" \
        --db="$source_db" \
        --authenticationDatabase="$auth_db" \
        --out="$target_dir" \
        --verbose
    
    if [ $? -eq 0 ]; then
        print_success "Database dumped successfully to $target_dir"
        
        # Show dump statistics
        local dump_path="$target_dir/$source_db"
        if [ -d "$dump_path" ]; then
            print_info "Dump contents:"
            ls -la "$dump_path"
            echo ""
            print_info "Collection files:"
            find "$dump_path" -name "*.bson" -exec basename {} \;
        fi
    else
        print_error "Database dump failed"
        exit 1
    fi
}

# Function to restore database
restore_database() {
    local source_dir="$1"
    local target_uri="$2"
    local target_db="${3:-$DEFAULT_SOURCE_DB}"
    
    print_info "Restoring database from $source_dir to $target_uri/$target_db"
    
    # Check if dump directory exists
    local dump_path="$source_dir/$DEFAULT_SOURCE_DB"
    if [ ! -d "$dump_path" ]; then
        print_error "Dump directory not found: $dump_path"
        exit 1
    fi
    
    # Run mongorestore
    # For cloud MongoDB, don't specify authentication database unless needed
    if [[ "$target_uri" == *"mongodb+srv://"* ]] || [[ "$target_uri" == *"mongodb://"* && "$target_uri" != *"localhost"* ]]; then
        # Cloud MongoDB - don't specify auth database
        mongorestore \
            --uri="$target_uri" \
            --db="$target_db" \
            --dir="$dump_path" \
            --verbose
    else
        # Local MongoDB - use auth database
        local auth_db="${AUTH_DB:-$DEFAULT_AUTH_DB}"
        mongorestore \
            --uri="$target_uri" \
            --db="$target_db" \
            --authenticationDatabase="$auth_db" \
            --dir="$dump_path" \
            --verbose
    fi
    
    if [ $? -eq 0 ]; then
        print_success "Database restored successfully to $target_uri/$target_db"
    else
        print_error "Database restore failed"
        exit 1
    fi
}

# Function to migrate (dump and restore in one step)
migrate_database() {
    echo "Migrating database from local to cloud MongoDB"
    echo "Target: $1/$2"
    echo "Temporary dump directory: $3"
    echo "Source URI: $SOURCE_URI"
    echo "Source DB: $SOURCE_DB"
    echo "Dump directory: $DUMP_DIR"
    echo "--------------------------------"

    local target_uri="$1"
    local target_db="$2"
    local dump_dir="${DUMP_DIR:-$DEFAULT_DUMP_DIR}"
    
    print_info "Starting migration from local to cloud MongoDB"
    print_info "Target: $target_uri/$target_db"
    print_info "Temporary dump directory: $dump_dir"
    
    # Dump the database
    dump_database "$dump_dir"
    
    # Restore to target
    restore_database "$dump_dir" "$target_uri" "$target_db"
    
    # Clean up dump directory
    if [ "$dump_dir" = "$DEFAULT_DUMP_DIR" ]; then
        print_info "Cleaning up temporary dump directory..."
        rm -rf "$dump_dir"
        print_success "Cleanup completed"
    else
        print_info "Dump directory preserved at: $dump_dir"
    fi
    
    print_success "Migration completed successfully!"
}

# Main script logic
case "${1:-help}" in
    "dump")
        if [ $# -lt 2 ]; then
            print_error "Missing target directory for dump command"
            echo ""
            show_usage
            exit 1
        fi
        check_tools
        dump_database "$2"
        ;;
    "restore")
        if [ $# -lt 3 ]; then
            print_error "Missing arguments for restore command"
            echo ""
            show_usage
            exit 1
        fi
        check_tools
        restore_database "$2" "$3" "${4:-}"
        ;;
    "migrate")
        if [ $# -lt 3 ]; then
            print_error "Missing arguments for migrate command"
            echo ""
            show_usage
            exit 1
        fi
        check_tools
        migrate_database "$2" "$3"
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac 