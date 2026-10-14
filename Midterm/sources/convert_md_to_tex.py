"""Convert this study packet's Markdown to standalone pdfLaTeX documents."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def math_text(text):
    for symbol, command in {'×': r'\times ', '→': r'\to ', '−': '-', '≤': r'\le ', '≥': r'\ge '}.items():
        text = text.replace(symbol, command)
    return text

def escape(text):
    replacements = {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}', '→': r'\ensuremath{\rightarrow}', '×': r'\ensuremath{\times}', '²': r'\ensuremath{{}^2}', '−': '-', '±': r'\ensuremath{\pm}', 'ε': r'\ensuremath{\epsilon}', 'θ': r'\ensuremath{\theta}', 'σ': r'\ensuremath{\sigma}', 'λ': r'\ensuremath{\lambda}', 'μ': r'\ensuremath{\mu}', '•': r'\textbullet{}', '≤': r'\ensuremath{\le}', '≥': r'\ensuremath{\ge}'}
    return ''.join(r'/\allowbreak{}' if c == '/' else replacements.get(c, c) for c in text)

def inline(text):
    pattern = r'(\$[^$]+\$|`[^`]+`|\[[^\]]+\]\([^\)]+\)|\*\*.+?\*\*|(?<!\*)\*[^*]+\*(?!\*))'
    parts = re.split(pattern, text)
    out = []
    for p in parts:
        if p.startswith('$') and p.endswith('$'):
            out.append(math_text(p))
        elif p.startswith('`'):
            code = p[1:-1]
            if code.endswith('.md'):
                code = code[:-3] + '.tex'
            if '\\' in code or re.fullmatch(r'[\w./() -]+\.(?:tex|pdf|pptx|py)', code):
                out.append(r'\path{' + code + '}')
            else:
                out.append(r'\texttt{' + escape(code) + '}')
        elif p.startswith('[') and re.fullmatch(r'\[([^\]]+)\]\(([^)]+)\)', p):
            label, target = re.fullmatch(r'\[([^\]]+)\]\(([^)]+)\)', p).groups()
            if target.endswith('.md'):
                target = target[:-3] + '.pdf'
            out.append(r'\href{\detokenize{' + target + '}}{' + inline(label) + '}')
        elif p.startswith('**'):
            out.append(r'\textbf{' + inline(p[2:-2]) + '}')
        elif p.startswith('*'):
            out.append(r'\emph{' + inline(p[1:-1]) + '}')
        else:
            out.append(escape(p))
    return ''.join(out)

def cells(line):
    # Bars inside inline math (conditional probabilities) are not table separators.
    return re.split(r'\|(?=(?:[^$]*\$[^$]*\$)*[^$]*$)', line.strip().strip('|'))

PREAMBLE = r'''\documentclass[11pt]{article}
\usepackage[margin=0.75in]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{amsmath,amssymb,booktabs,longtable,array}
\usepackage{listings}
\usepackage[hidelinks]{hyperref}
\usepackage{enumitem}
\setlist{nosep,leftmargin=*}
\lstset{basicstyle=\ttfamily\small,breaklines=true,columns=fullflexible,keepspaces=true,showstringspaces=false,frame=single}
\setlength{\parindent}{0pt}
\setlength{\parskip}{6pt}
\setlength{\emergencystretch}{3em}
\begin{document}
'''

def convert(path):
    lines = path.read_text(encoding='utf-8-sig').splitlines()
    out = [PREAMBLE]
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('```'):
            out.append(r'\begin{lstlisting}')
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                out.append(lines[i]); i += 1
            out.append(r'\end{lstlisting}')
        elif line.startswith('$$'):
            math = line[2:]
            while not math.endswith('$$'):
                i += 1; math += '\n' + lines[i]
            out.append('\\[\n' + math_text(math[:-2]) + '\n\\]')
        elif line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                row = cells(lines[i])
                if not all(re.fullmatch(r'\s*:?-+:?\s*', c) for c in row):
                    rows.append(row)
                i += 1
            i -= 1
            n = len(rows[0])
            widths = {2: [0.29, 0.65], 3: [0.19, 0.38, 0.35]}.get(n, [0.94/n]*n)
            spec = ''.join(r'>{\raggedright\arraybackslash}p{' + str(w) + r'\linewidth}' for w in widths)
            out.append(r'{\small\setlength{\tabcolsep}{3pt}\renewcommand{\arraystretch}{1.25}')
            out.append(r'\begin{longtable}{' + spec + '}\n\\toprule')
            for r, row in enumerate(rows):
                assert len(row) == n, (path.name, row)
                out.append(' & '.join(inline(c.strip()) for c in row) + r' \\')
                if r == 0:
                    out.append(r'\midrule\endhead')
            out.append(r'\bottomrule\end{longtable}}')
        elif re.match(r'^#{1,3} ', line):
            level, title = line.split(' ', 1)
            command = {1: 'section', 2: 'subsection', 3: 'subsubsection'}[len(level)]
            out.append('\\' + command + '*{' + inline(title) + '}')
        elif line.startswith('- ') or re.match(r'^\d+\. ', line):
            numbered = not line.startswith('- ')
            env = 'enumerate' if numbered else 'itemize'
            out.append('\\begin{' + env + '}')
            while i < len(lines):
                match = re.match(r'^\d+\. (.*)', lines[i]) if numbered else re.match(r'^- (.*)', lines[i])
                if match:
                    content = match.group(1).replace('[ ] ', r'CHECKBOX ', 1)
                    rendered = inline(content).replace('CHECKBOX ', r'\(\square\) ')
                    out.append(r'\item ' + rendered); i += 1
                elif not lines[i].strip() and i+1 < len(lines) and (re.match(r'^\d+\. ', lines[i+1]) if numbered else lines[i+1].startswith('- ')):
                    i += 1
                else:
                    break
            i -= 1
            out.append('\\end{' + env + '}')
        elif line.strip() == '---':
            out.append(r'\par\noindent\rule{\linewidth}{0.4pt}\par')
        else:
            out.append(inline(line))
        i += 1
    out.append(r'\end{document}')
    target = path.with_suffix('.tex')
    target.write_text('\n'.join(out) + '\n', encoding='utf-8')
    print(target.name)

if __name__ == '__main__':
    for source in sorted(ROOT.glob('*.md')):
        convert(source)
