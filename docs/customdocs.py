from sphinxcontrib.autoanysrc import analyzers

class CustomAnalyzer(analyzers.BaseAnalyzer):
    """
    Simple class that takes arbitrary files, starts and ends blocks, and strips comment characters
    """

    start_block = '"""'  # String to start a comment block
    end_block = '"""'    # String to end a comment block
    strip_leading = 0    # Number of characters to strip from the beginning of the comments

    def process(self, content):

        in_comment_block = False

        for lineno, srcline in enumerate(content.split('\n')):

            line = srcline.rstrip()
            if in_comment_block:
                if line.startswith(self.end_block):
                    in_comment_block = False
                    continue

                if len(line) < self.strip_leading:
                    yield '', lineno
                else:
                    yield line[self.strip_leading:], lineno

            elif line.startswith(self.start_block):
                in_comment_block = True



class ShellScriptAnalyzer(CustomAnalyzer):
    """
    Processes shell scripts

    Comment blocks start and end with ##!.
    Assumes the comments start with # and a space, so
    it just returns the line with the first two characters stripped.
    """

    start_block = '##!'
    end_block = '##!'
    strip_leading = 2


class PODAnalyzer(CustomAnalyzer):
    """
    Processes perl scripts with POD comments

    Comment blocks start with =pod and end with =cut.
    """

    start_block = '=pod'
    end_block = '=cut'
