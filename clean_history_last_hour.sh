#!/bin/zsh

# Calculate the timestamp for two hours ago using BSD date
two_hours_ago=$(date -v-1H +%s)
if [ $? -ne 0 ]; then
  echo "Error: Failed to calculate timestamp." >&2
  exit 1
fi

# Create a temporary file for filtered history
temp_file=$(mktemp)
if [ $? -ne 0 ]; then
  echo "Error: Failed to create a temporary file." >&2
  exit 1
fi

# Process the history file
awk -v threshold="$two_hours_ago" '
  BEGIN { delete_entry = 0 }
  /^#([0-9]+)$/ {
    if ($1 ~ /^#[0-9]+$/) {
      timestamp = substr($1, 2)
      if (timestamp >= threshold) {
        delete_entry = 1
      } else {
        delete_entry = 0
      }
    }
  }
  !delete_entry
' ~/.zsh_history > "$temp_file"
if [ $? -ne 0 ]; then
  echo "Error: Failed to process history file." >&2
  rm -f "$temp_file"
  exit 1
fi

# Replace the history file
mv "$temp_file" ~/.zsh_history
if [ $? -ne 0 ]; then
  echo "Error: Failed to replace history file." >&2
  exit 1
fi

# Reload history into the current session
fc -R
if [ $? -ne 0 ]; then
  echo "Error: Failed to reload history." >&2
  exit 1
fi