# Used for step-parsing strings
class Cursor: 
    def __init__(self, source_string):
        self.source_string = source_string
        self.cursor_index = 0

    def is_done(self):
        return self.cursor_index > len(self.source_string) - 1

    def next(self):
        self.cursor_index += 1

    def peek(self):
        index = self.cursor_index + 1 
        if index <= len(self.source_string) - 1:
            return self.source_string[index]
        else:
            return "" 

    def get(self):
        return self.source_string[self.cursor_index]

    def get_remaining(self):
        return "".join(self.source_string[self.cursor_index:])

    # Place cursor on index after next occurrence of any of the mentioned symbols
    def move_past_next(self, symbols):

        while True: 
            if self.is_done():
                break 
            else:
                current = self.get()
                self.next()
                if current in symbols:
                    break 
        return  

    # Returns characters up until, but not including, any of the mentioned symbols
    # Leaves cursor before the found symbol
    def get_until(self, symbols):
        scan = ""

        if self.is_done():
            return ""

        while True:

            
            current = self.get()
            ahead = self.peek() 

            if current in symbols:
                break 
            else: 
                scan += current
                if ahead in symbols or ahead == "":
                    break 
                self.next() 

        return scan
