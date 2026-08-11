import difflib
import html

def render_side_by_side_diff(prompt_a: str, prompt_b: str, label_a: str = "Parent Generation", label_b: str = "Mutated Generation") -> str:
    """
    Renders a line-by-line HTML diff viewer with syntax highlighting for additions and deletions.
    """
    lines_a = prompt_a.splitlines()
    lines_b = prompt_b.splitlines()

    matcher = difflib.SequenceMatcher(None, lines_a, lines_b)
    
    table_rows = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            for line_a, line_b in zip(lines_a[i1:i2], lines_b[j1:j2]):
                esc_a = html.escape(line_a)
                esc_b = html.escape(line_b)
                table_rows.append(f"""
                <tr>
                    <td class="diff-line-num">{i1+1}</td>
                    <td class="diff-content diff-equal">{esc_a}</td>
                    <td class="diff-line-num">{j1+1}</td>
                    <td class="diff-content diff-equal">{esc_b}</td>
                </tr>
                """)
        elif tag == 'replace':
            max_len = max(i2 - i1, j2 - j1)
            for k in range(max_len):
                la = html.escape(lines_a[i1 + k]) if (i1 + k) < i2 else ""
                lb = html.escape(lines_b[j1 + k]) if (j1 + k) < j2 else ""
                
                cell_a = f'<td class="diff-content diff-del">{la}</td>' if la else '<td class="diff-content diff-empty"></td>'
                cell_b = f'<td class="diff-content diff-add">{lb}</td>' if lb else '<td class="diff-content diff-empty"></td>'
                
                table_rows.append(f"""
                <tr>
                    <td class="diff-line-num">{i1+k+1 if la else ""}</td>
                    {cell_a}
                    <td class="diff-line-num">{j1+k+1 if lb else ""}</td>
                    {cell_b}
                </tr>
                """)
        elif tag == 'delete':
            for k in range(i2 - i1):
                la = html.escape(lines_a[i1 + k])
                table_rows.append(f"""
                <tr>
                    <td class="diff-line-num">{i1+k+1}</td>
                    <td class="diff-content diff-del">{la}</td>
                    <td class="diff-line-num"></td>
                    <td class="diff-content diff-empty"></td>
                </tr>
                """)
        elif tag == 'insert':
            for k in range(j2 - j1):
                lb = html.escape(lines_b[j1 + k])
                table_rows.append(f"""
                <tr>
                    <td class="diff-line-num"></td>
                    <td class="diff-content diff-empty"></td>
                    <td class="diff-line-num">{j1+k+1}</td>
                    <td class="diff-content diff-add">{lb}</td>
                </tr>
                """)

    html_code = f"""
    <style>
        .diff-container {{
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 13px;
            width: 100%;
            border-collapse: collapse;
            background-color: #0F172A;
            color: #E2E8F0;
            border: 1px solid #334155;
            border-radius: 8px;
            overflow: hidden;
        }}
        .diff-header {{
            background-color: #1E293B;
            font-weight: bold;
            padding: 10px;
            text-align: center;
            border-bottom: 2px solid #334155;
            color: #38BDF8;
        }}
        .diff-container td {{
            padding: 4px 8px;
            vertical-align: top;
            white-space: pre-wrap;
            word-break: break-all;
        }}
        .diff-line-num {{
            width: 40px;
            text-align: right;
            color: #64748B;
            user-select: none;
            border-right: 1px solid #334155;
            background-color: #1E293B;
        }}
        .diff-equal {{ background-color: #0F172A; }}
        .diff-add {{ background-color: rgba(16, 185, 129, 0.2); color: #6EE7B7; border-left: 3px solid #10B981; }}
        .diff-del {{ background-color: rgba(239, 68, 68, 0.2); color: #FCA5A5; border-left: 3px solid #EF4444; }}
        .diff-empty {{ background-color: #1E293B; }}
    </style>
    
    <table class="diff-container">
        <thead>
            <tr>
                <th colspan="2" class="diff-header">{label_a}</th>
                <th colspan="2" class="diff-header">{label_b}</th>
            </tr>
        </thead>
        <tbody>
            {''.join(table_rows)}
        </tbody>
    </table>
    """
    return html_code
