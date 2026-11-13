# Project presentation

[slides.pdf](slides.pdf) contains a title slide and 14 numbered content slides (15 PDF pages). Edit `slides.tex`; build with Tectonic
as described in [REPRODUCING.md](../REPRODUCING.md). The [speaker notes](speaker-notes.md)
allocate exactly ten minutes; rehearse and adjust before presenting.

## Build inside VS Code on this workstation

LaTeX Workshop is installed. The enclosing `GitHub Repos/.vscode/settings.json`
configures the local Tectonic compiler and PDF preview. With `slides.tex` active,
click **Build LaTeX project** (play icon) or press **Ctrl+Alt+B**. Saving a TeX
file also builds it. **Ctrl+Alt+V** opens the current PDF in a VS Code tab.
The live output is `presentation/build/slides.pdf`; each successful build also
updates `presentation/slides.pdf` automatically.
These workstation settings apply when `GitHub Repos` is the open workspace.
