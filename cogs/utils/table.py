from typing import List


def make_table(*columns: List[str], padding=1, first_row_headers=False, header_separator='-'):
    """
    Makes a monospace table from provided columns
        Note: may be horribly (not) optimized.
    Args:
        *columns: One or more lists of strings that make up the columns of the table.
            Note: all columns must be the same length
        padding: The number of spaces to put in between each column.
        first_row_headers: If the first item in each column is a header.
        header_separator: The one-length string to use as the character to use as the separator between the header
            and the data.

    Returns:
        A monospace table.
    """
    sizes = [len(max(column, key=len)) for column in columns]

    resized_columns = []
    for column, size in zip(columns, sizes):
        resized_column = []
        for item in column:
            resized = '{0: <{1}}'.format(item, size)
            resized_column.append(resized)
        resized_columns.append(resized_column)

    rows = [[column[i] for column in resized_columns] for i in range(len(resized_columns[0]))]

    if first_row_headers:
        header = (' ' * padding).join(rows[0])
        header += '\n' + (header_separator[0] * len(header)) + '\n'
    else:
        header = ''

    table = '\n'.join((' ' * padding).join(row) for row in (rows[1:] if first_row_headers else rows))

    return header + table

if __name__ == '__main__':
    print(make_table(['a', 'as', 'asd', 'asdf'], ['asdffff', 'asdg', 'aff', 'a'], first_row_headers=True, header_separator='*'))
