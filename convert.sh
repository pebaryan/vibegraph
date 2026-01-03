#!/usr/bin/env bash
# This script copies all markdown files from the project root into the report\n# template’s sections directory and then compiles the LaTeX document.

set -euo pipefail

# Ensure the sections directory exists
mkdir -p report/sections

# Convert all .md files from the markdown/ directory to .tex files in report/sections
for md in markdown/*.md; do
  # Skip if no markdown files found
  [ -e "$md" ] || continue
  base=$(basename "$md" .md)
  target="report/sections/${base}.tex"
  # Use pandoc to convert markdown to LaTeX
  pandoc "$md" -o "$target"
  echo "Converted $md to $target"
done

# Compile the LaTeX document into PDF
# Note: The template uses \input{sections/*.md}. LaTeX does not natively read Markdown,
# so you’ll need a package such as markdown or markdown2latex to handle that, or
# you can run pandoc to convert the markdown files to LaTeX first.

# Example using pandoc to convert each markdown file to a .tex file and then
# include them.  Uncomment the following lines if you prefer pandoc.

# for md in report/sections/*.md; do
#   tex=${md%.md}.tex
#   pandoc "$md" -o "$tex"
#   echo "Converted $md to $tex"
# done

# Build the final PDF
pdflatex -interaction=nonstopmode report/report.tex
pdflatex -interaction=nonstopmode report/report.tex

echo "PDF generated: report/report.pdf"
