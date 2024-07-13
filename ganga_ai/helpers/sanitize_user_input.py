def sanitize_user_input(line: str, cell: str) -> str:
    line_txt = line.strip()
    cell_txt = cell.strip()
    return line_txt + cell_txt
