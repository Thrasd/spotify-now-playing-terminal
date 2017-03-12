import curses


class TextLine:
    def __init__(self, text, screen_width):
        self.begin_index = 0
        self.text_width = screen_width - 2
        self.text = text
        self.out_of_bounds = len(self.text) - self.text_width
        self.direction = 1
        self.hover_time = 0
        self.is_hovering = False

    def get_scrolling_text(self):
        text = self.text[self.begin_index:self.begin_index + self.text_width]

        # If we are hovering, reduce the hover time
        if self.is_hovering:
            self.hover_time -= 1
        else:
            self.begin_index += self.direction

        # Change direction when we reach
        if self.begin_index >= self.out_of_bounds or self.begin_index < 1:
            if not self.is_hovering:
                self.is_hovering = True
                self.hover_time = 2
            elif self.hover_time < 0:
                self.is_hovering = False
                self.direction *= -1
        return text


class TextScrolling:
    def __init__(self, text: str, screen_width: int, is_multi_line: bool = False):
        self.text = text
        self.scroll_speed = 500  # Milliseconds
        self.screen_width = screen_width

        if is_multi_line:
            self.lines = [TextLine(x, screen_width) for x in text]
        else:
            self.lines = [TextLine(text, screen_width), ]

    def draw_text(self, stdscr: curses, start_line):
        # Draw each line
        line_index = start_line
        for line in self.lines:
            if len(line.text) < self.screen_width:
                # The text can be within the screen width, we do not need to scroll it
                x_pos = self.__get_center_position(line.text)
                stdscr.addnstr(line_index, x_pos, line.text, len(line.text))
            else:
                # Handle scrolling
                text = line.get_scrolling_text()
                stdscr.addnstr(line_index, 1, text, len(text))
            line_index += 1

        # Apparently we get an extra line if it is multiline, TODO fix this
        if len(self.lines) > 1:
            line_index -= 1

        # Return last line we drew on
        return line_index

    def __get_center_position(self, text):
        return int((self.screen_width / 2) - (len(text) / 2))
