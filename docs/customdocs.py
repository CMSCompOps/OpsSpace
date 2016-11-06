from sphinxcontrib.autoanysrc import analyzers

class CustomAnalyzer(analyzers.BaseAnalyzer):
    """
    Simple class that takes arbitrary files, starts and ends blocks, and strips comment characters
    """

    comment_starts_with = '"""'  # String to start a comment block
    comment_ends_with = '"""'    # String to end a comment block
    strip_leading = 0            # Number of characters to strip from the beginning of the comments

    def process_line(self, line):
        yield line

    def process(self, content):

        in_comment_block = False

        for lineno, srcline in enumerate(content.split('\n')):

            line = srcline.rstrip()
            if in_comment_block:
                if line.startswith(self.comment_ends_with):
                    in_comment_block = False
                    yield '', lineno
                    continue

                if len(line) < self.strip_leading:
                    yield '', lineno
                else:
                    for parsed in self.process_line(line[self.strip_leading:]):
                        yield parsed, lineno

            elif line.startswith(self.comment_starts_with):
                in_comment_block = True


class ShellScriptAnalyzer(CustomAnalyzer):
    """
    Processes shell scripts

    Comment blocks start and end with ##!.
    Assumes the comments start with # and a space, so
    it just returns the line with the first two characters stripped.
    """

    comment_starts_with = '##!'
    comment_ends_with = '##!'
    strip_leading = 2


class PODAnalyzer(CustomAnalyzer):
    """
    Processes perl scripts with POD comments

    Comment blocks start with =pod and end with =cut.
    """

    comment_starts_with = '=pod'
    comment_ends_with = '=cut'

    headers = ['=', '~', '+', '^', '*', '-', '#']

    def process_line(self, line):
        if line.startswith('=head'):
            output = ' '.join(line.split()[1:])
            for final in [output, self.headers[int(line[5]) - 1] * len(output)]:
                yield final
        else:
            yield line
