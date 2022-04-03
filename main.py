import sys


def arg_parser(args: list[str]) -> int:
    if len(args) != 2:
        print(f"Usage: {args[0]} number_of_processes.\nExample: $ {args[0]} 2.", file=sys.stderr)
        exit(1)
    try:
        num_of_processes = int(args[1])
        if num_of_processes < 1:
            print(f"Number of processes should be >= 1. Got: {num_of_processes}", file=sys.stderr)
            exit(1)
        return num_of_processes
    except:
        print(f"Number of processes should be positive integer. Got: {args[1]}", file=sys.stderr)
        exit(1)


def main(argv):
    num_processes = arg_parser(argv)


if __name__ == "__main__":
    main(sys.argv)
