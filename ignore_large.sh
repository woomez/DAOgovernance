#!/bin/bash

# Set the size limit in bytes (50 MB)
size_limit=$((50 * 1024 * 1024))

# Find files larger than the size limit and add them to .gitignore
find . -type f -size +${size_limit}c -not -path "./.git/*" -exec echo {} >> .gitignore \;

