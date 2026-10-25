# Install invo-assignment

Keep three locations separate: this public development checkout, the installed reusable skill, and each personal assignment repository. This repository contains synthetic examples and tests only.

Copy the complete `skill/invo-assignment` directory from this source checkout to your agent's personal skills directory, for example `C:\Users\<you>\.agents\skills\invo-assignment`. Install Python 3.10+ and Git and make them available on PATH. The installed directory includes `SKILL.md`, `VERSION`, references and scripts; no package installation is required.

Text-only packets and separate attachments use the standard library. If a packet needs PDF merging to fit its upload budget, install `pypdf` in the helper's Python environment; combining images into a PDF also requires `Pillow` (`python -m pip install pypdf Pillow`). The helper reports a missing dependency before changing the active packet or mailbox. Review merged visual context before handing it to the student.

Open a new folder outside both locations and outside any existing Git repository for your assignment. Invoke `$invo-assignment` in that project and provide its explicit directory. The initialization command is documented in the installed skill's `references/operations.md`. Local Git history needs no remote or hosting account.

For updates, replace only the installed skill directory with a newer complete copy. Keep assignment repositories where they are; installation and updates never run workspace operations against them. Each initialized assignment records the installed skill version and state-format version. Updating tooling does not overwrite that recorded provenance.

Developers run `python -m unittest discover -v` from this source checkout. Tests create synthetic repositories in the operating system temporary directory, outside this repository and installed tooling.
