import sys

from .runner import available_examples, run_example


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"-h", "--help"}:
        available = ", ".join(available_examples())
        print("Usage: python -m st_components.examples <example> [streamlit args...]")
        print(f"Available examples: {available}")
        return 0

    if argv[0] in {"--list", "list"}:
        for name in available_examples():
            print(name)
        return 0

    name, extra_args = argv[0], argv[1:]
    try:
        return run_example(name, extra_args)
    except (RuntimeError, ValueError) as err:
        print(err, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
