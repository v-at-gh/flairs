#!/usr/bin/env bash

if [[ $# -ne 1 ]]; then
	>&2 echo "Error: Invalid number of arguments. Please provide an IP address."
	exit 1
fi

DIR="$(realpath ${0%/*/*})/data/cache/whois/ipv4"

if [ ! -d "$DIR" ]; then
	mkdir -p "$DIR"
fi

validate_ipv4() {
	local address="$1"
	local IFS='.'
	local -a octets
	read -r -a octets <<< "$address"

	if [[ ${#octets[@]} -ne 4 ]]; then
		>&2 echo "Error: Invalid IPv4 address provided: $address"
		exit 2
	fi

	for octet in "${octets[@]}"; do
		if ! [[ $octet =~ ^[0-9]+$ ]] || ((octet < 0 || octet > 255)); then
			>&2 echo "Error: Invalid IPv4 address provided: $address"
			exit 2
		fi
	done
}

whoisthis() {
	local address="$1"
	validate_ipv4 "$address"
	local file_path="${DIR}/${address}.whois.txt"
	if [[ -e "$file_path" ]]; then
		local DATE
		DATE="$(date -r "$file_path" '+%Y-%m-%d %H:%M:%S')"
		echo "-------- Report Start --------"
		cat "$file_path"
		echo "-------- Report End --------"
		echo "Whois report for IP address: $address"
		echo "Report requested on: $DATE"
	else
		if output=$(whois "$address" 2>&1); then
			echo "$output" | tee "$file_path"
		else
			>&2 echo "Error: Failed to perform whois lookup for $address."
			>&2 echo "Error message: $output"
			exit 3
		fi
	fi
}

whoisthis "$1"
