from sphinxcontrib.autoanysrc import analyzers

class ShellScriptAnalyzer(analyzers.BaseAnalyzer):
    """
    Processes shell scripts

    Comment blocks start and end with ##!.
    Assumes the comments start with # and a space, so
    it just returns the line with the first two characters stripped.
    """

    def process(self, content):

        in_comment_block = False

        for lineno, srcline in enumerate(content.split('\n')):

            line = srcline.rstrip()
            if line.startswith('##!'):
                if in_comment_block:
                    in_comment_block = False
                else:
                    in_comment_block = True
                continue

            if not in_comment_block:
                continue

            if len(line) < 3:
                yield '', lineno

            else:
                yield line[2:], lineno
