#!/bin/bash

input_file="routeviews-rv2-20230820-1200.pfx2as"
output_file="routeviews-rv2-20230820-1200.pfx2as.csv"

# Perform space-to-comma replacement
# Remove lines with more than 3 elements (comma-separated)
# Add line number at the beginning of the line (will be used as PK)
sed  -e 's/\s\+/,/g' "$input_file" | awk -F, 'NF <= 3 {print}' | nl -w1 -s',' > "$output_file"
