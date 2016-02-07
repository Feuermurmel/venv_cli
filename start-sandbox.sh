#! /usr/bin/env bash

script_dir=$(dirname "$(readlink -f "$BASH_SOURCE")")
sandbox_dir="$script_dir/sandbox"

export PATH="$script_dir/venv/bin:$PATH"

mkdir -p "$sandbox_dir"

cd "$sandbox_dir"

exec bash
