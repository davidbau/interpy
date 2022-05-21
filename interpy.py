from bottle import route, run
from baukit import show
import html, sys, ast, tokenize, re, token

_line_start_re = re.compile(r'^', re.M)

class TokenWrapper:
    def __init__(self, token):
        self.token = token
        self.lineno, self.col_offset = token.start
        self.end_lineno, self.end_col_offset = token.end
    def __repr__(self):
        return token.tok_name[self.token.type]

class ParsedPythonFile:
    def __init__(self, filename):
        self.filename = filename
        with tokenize.open(filename) as f:
            self.tokens = list(tokenize.generate_tokens(f.readline))
        self.source = tokenize.untokenize(self.tokens)
        self.tree = ast.parse(self.source)

        # Make a sequence of top-level nodes and tokens in the file
        sequence = []
        def add_token(i):
            if (self.tokens[i].type not in [
                    token.NEWLINE, token.ENDMARKER, token.NL,
                    token.INDENT, token.DEDENT]):
                sequence.append(TokenWrapper(self.tokens[i]))
        i = 0
        for b in self.tree.body:
            if isinstance(b, ast.Expr):
                b = b.value
            while self.tokens[i].end <= (b.lineno, b.col_offset):
                add_token(i)
                i += 1
            sequence.append(b)
            while self.tokens[i].end <= (b.end_lineno, b.end_col_offset):
                i += 1
        for i in range(i, len(self.tokens)):
            add_token(i)
        self.sequence = sequence

        # Now go through top-level nodes and divide the file into segments
        # There are three types of segments
        #
        # Function definitions - includes preceding comments
        # Class definitions - includes preceding coments
        # Immediate code - may be comment-only
        # Top-level docstrings

class LineOffsetMap:
    def __init__(self, source):
        self.source = source
        self.line_offsets = [m.start(0) for m in _line_start_re.finditer(self.source)]

    def line_to_offset(self, line, column):
        # type: (int, int) -> int
        """
        Converts 1-based line number and 0-based column to 0-based character offset into text.
        """
        line -= 1
        if line >= len(self.line_offsets):
            return len(self.source)
        elif line < 0:
            return 0
        else:
            return min(self.line_offsets[line] + max(0, column), len(self.source))

    def offset_to_line(self, offset):
        # type: (int) -> Tuple[int, int]
        """
        Converts 0-based character offset to pair (line, col) of 1-based line and 0-based column
        numbers.
        """
        offset = max(0, min(len(self.source), offset))
        line_index = bisect.bisect_right(self.line_offsets, offset) - 1
        return (line_index + 1, offset - self.line_offsets[line_index])

        
ppf = ParsedPythonFile(sys.argv[1])
for node in ppf.sequence:
    print(node)

@route('/')
def hello():
    return '<pre>' + html.escape(file_content) + '</pre>'

run(host='localhost', port=8080, debug=True)
