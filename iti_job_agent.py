"""Thin launcher for the organized ITI Lucknow placement agent package.

Keep this file at the repo root so the project stays easy to run with a single
command, while the real logic lives in the package below.
"""

from iti_placement_agent.app import main


if __name__ == "__main__":
    main()