
##### Bookkeeping for passing args #####
declare -A args
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --*=*) # If the argument is in the form --key=value, process it
            key="${1%%=*}" # Extract the key by removing everything after the first '='
            key="${key/--/}" # Remove the leading '--' from the key
            value="${1#*=}" # Extract the value by removing everything before the first '='
            args[$key]="$value" # Assign the extracted value to the key in the array
            ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift # Shift once to get to the next argument
done
for key in "${!args[@]}"; do
    echo "$key: ${args[$key]}"
done

echo "Script arguments:"
for arg in "$@"; do
  echo "$arg"
done

########################################

# activate conda
. /work/awilf/anaconda3/etc/profile.d/conda.sh
conda activate example_env

cmd="python example.py --arg1 ${args[arg1]} --arg2 ${args[arg2]}"
echo "$cmd"
eval "$cmd"

cmd2="python example2.py --arg2 ${args[arg2]} --arg3 ${args[arg3]}"
echo "$cmd2"
eval "$cmd2"
