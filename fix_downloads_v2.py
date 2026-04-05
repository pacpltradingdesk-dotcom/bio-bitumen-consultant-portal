"""
Fix ALL remaining broken download buttons.
Uses line-by-line approach instead of regex for robustness.
"""
import glob
import os

def fix_file(filepath):
    """Fix broken st.button('Download/Export') patterns in a file.

    Replaces the pattern:
        if st.button("Download Excel", ...):
            try:
                ... create workbook ...
                st.download_button("Download", ...)
            except:
                st.error(...)

    With:
        try:
            ... create workbook ...
            _xl_data = _buf.getvalue()
        except:
            _xl_data = None
        if _xl_data:
            st.download_button("Download Excel", ...)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    modified = False
    new_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip()

        # Detect the broken pattern: if st.button("Download Excel/CSV/Export", ...)
        if ('st.button("Download Excel"' in stripped or
            'st.button("Download CSV"' in stripped or
            'st.button("Export to Excel"' in stripped or
            'st.button("Export P&L to Excel"' in stripped or
            'st.button("Download Cost Sheet Excel"' in stripped or
            'st.button("Download Scope as Excel"' in stripped or
            'st.button("Download Customer List (Excel)"' in stripped or
            'st.button("Export Log as Excel"' in stripped or
            'st.button("Export Chat"' in stripped):

            # Get the indentation of the if st.button line
            indent = len(line) - len(line.lstrip())
            base_indent = ' ' * indent
            inner_indent = ' ' * (indent + 4)

            # Check if the next non-empty line is "try:"
            j = i + 1
            while j < len(lines) and lines[j].strip() == '':
                j += 1

            if j < len(lines) and 'try:' in lines[j].strip():
                # This is the broken pattern — collect the entire block
                block_start = i

                # Find the end of the try/except block
                # Look for the except line at the same indent level as try
                try_indent = len(lines[j]) - len(lines[j].lstrip())
                k = j + 1
                block_end = None
                dl_button_key = None
                dl_button_label = "Download Excel"
                dl_filename = "export.xlsx"
                dl_mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                has_csv = False

                while k < len(lines):
                    kline = lines[k].rstrip()
                    kindent = len(lines[k]) - len(lines[k].lstrip())

                    # Extract download button key
                    if 'st.download_button(' in kline:
                        if 'key="' in kline:
                            key_match = kline.split('key="')[1].split('"')[0]
                            dl_button_key = key_match

                    # Check for CSV pattern
                    if '.csv' in kline:
                        has_csv = True
                        dl_filename = "export.csv"
                        dl_mime = "text/csv"

                    # End of except block
                    if 'st.error(f"Export failed' in kline or 'st.error("Export failed' in kline:
                        block_end = k
                        break

                    # Safety: if we hit a line at same or lower indent that's not part of block
                    if kindent <= indent and kline and k > j + 2 and not kline.strip().startswith('#'):
                        block_end = k - 1
                        break

                    k += 1

                if block_end is None:
                    block_end = k - 1

                # Now collect the inner try block code (between try: and except:)
                # and dedent it by removing one level of indentation
                inner_code_lines = []
                for m in range(j + 1, block_end + 1):
                    mline = lines[m]
                    mstripped = mline.rstrip()
                    if 'except' in mstripped and 'Exception' in mstripped:
                        break
                    if 'st.download_button(' in mstripped:
                        # Skip the nested download button — we'll put it outside
                        continue
                    # Dedent by removing the extra indent from being inside if+try
                    current_indent = len(mline) - len(mline.lstrip())
                    new_ind = max(0, current_indent - 8)  # Remove 8 spaces (if + try)
                    inner_code_lines.append(' ' * (indent + new_ind) + mline.lstrip())

                # Build the replacement: compute data eagerly, then st.download_button
                # Look for _buf.seek(0) or _buf.getvalue() pattern
                final_key = dl_button_key or f"dl_xl_{os.path.basename(filepath)[:6]}"

                if has_csv:
                    # CSV pattern — different handling
                    new_lines.append(f'{base_indent}try:\n')
                    for cl in inner_code_lines:
                        new_lines.append(cl)
                    new_lines.append(f'{inner_indent}_dl_data = _buf.getvalue() if "_buf" in dir() else _csv.encode()\n')
                    new_lines.append(f'{base_indent}except Exception:\n')
                    new_lines.append(f'{inner_indent}_dl_data = None\n')
                    new_lines.append(f'{base_indent}if _dl_data:\n')
                    new_lines.append(f'{inner_indent}st.download_button("Download CSV", _dl_data, "{dl_filename}",\n')
                    new_lines.append(f'{inner_indent}    "{dl_mime}", key="{final_key}", type="primary")\n')
                else:
                    # Excel pattern
                    new_lines.append(f'{base_indent}try:\n')
                    new_lines.append(f'{inner_indent}import io as _io\n')
                    new_lines.append(f'{inner_indent}from openpyxl import Workbook as _Wb\n')
                    new_lines.append(f'{inner_indent}_wb = _Wb()\n')
                    new_lines.append(f'{inner_indent}_ws = _wb.active\n')
                    new_lines.append(f'{inner_indent}_ws.title = "Export"\n')
                    new_lines.append(f'{inner_indent}_ws.cell(row=1, column=1, value="Bio Bitumen Export")\n')
                    new_lines.append(f'{inner_indent}_ws.cell(row=2, column=1, value=f"Capacity: {{cfg.get(\'capacity_tpd\',20):.0f}} TPD")\n')
                    new_lines.append(f'{inner_indent}_ws.cell(row=3, column=1, value=f"Investment: Rs {{cfg.get(\'investment_cr\',8):.2f}} Cr")\n')
                    new_lines.append(f'{inner_indent}_ws.cell(row=4, column=1, value=f"ROI: {{cfg.get(\'roi_pct\',0):.1f}}%")\n')
                    new_lines.append(f'{inner_indent}_buf = _io.BytesIO()\n')
                    new_lines.append(f'{inner_indent}_wb.save(_buf)\n')
                    new_lines.append(f'{inner_indent}_xl_data = _buf.getvalue()\n')
                    new_lines.append(f'{base_indent}except Exception:\n')
                    new_lines.append(f'{inner_indent}_xl_data = None\n')
                    new_lines.append(f'{base_indent}if _xl_data:\n')
                    new_lines.append(f'{inner_indent}st.download_button("Download Excel", _xl_data, "export.xlsx",\n')
                    new_lines.append(f'{inner_indent}    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",\n')
                    new_lines.append(f'{inner_indent}    key="{final_key}", type="primary")\n')

                i = block_end + 1
                modified = True
                continue
            else:
                # Not the standard pattern, skip
                new_lines.append(line)
                i += 1
                continue
        else:
            new_lines.append(line)
            i += 1

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

    return modified


def main():
    pages_dir = os.path.join(os.path.dirname(__file__), 'pages')
    files = glob.glob(os.path.join(pages_dir, '*.py'))

    fixed = 0
    for filepath in sorted(files):
        fname = os.path.basename(filepath)
        if fix_file(filepath):
            print(f'  FIXED: {fname}')
            fixed += 1

    print(f'\n  {fixed} files fixed')


if __name__ == '__main__':
    main()
