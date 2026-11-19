"""GUI entry point for source and PyInstaller builds."""
import sys

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--smoke-test":
        from pathlib import Path
        from wedding_organizer.smoke import smoke_test
        sys.exit(smoke_test(Path(sys.argv[2])))
    else:
        from wedding_organizer.gui import main
        sys.exit(main())
