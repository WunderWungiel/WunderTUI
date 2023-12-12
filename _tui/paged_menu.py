from ..small_libs import passer, clean, reset, cyan_background, isodd, iseven
from .term import get_key, get_raw_string
from .menu import split_item
from icecream import ic

class _PagedMenu:
    def __init__(self, items=None, text=None, custom_text=None, width=38, items_on_page=3, space_left=9, repeat=False):

        if not items:
            items = []

        self.text, self.custom_text = text, custom_text
        self.items = items
        self.width, self.items_on_page, self.space_left = width, items_on_page, space_left

        options_names = []
        options_actions = []
        options_integers = []
        options_args = []

        # The first selected item is first one.
        self.current_chosen = 1

        self.options_names, self.options_actions = options_names, options_actions
        self.options_integers, self.options_args = options_integers, options_args

        if repeat:
            self.repeat = repeat if repeat > 0 else len(items) - abs(repeat) + 1

        self.current_page = 0

        self.commit()

    def commit(self):
        i = 1

        self.options_names = []
        self.options_actions = []
        self.options_integers = []
        self.options_args = []

        # Let's make the real index of items properties.
        # We will retrieve:
        # - names of items
        # - actions to do in case of selecting items
        # - integer of each account, starting with 0
        # - optional arguments to actions.
        # If name of item is empty, or None, it will be replaced with a break between items.
        for name in self.items:
            if not name:
                self.options_names.append('')
                self.options_actions.append(passer)
                self.options_integers.append(None)
                self.options_args.append([])
                # In this case we omit adding 1 to i, because this is just a break between items.
            else:
                self.options_names.append(name[0])
                self.options_actions.append(name[1])
                # If there are arguments...
                if len(name) > 2:
                    args = name[2]
                    # If it's one argument...
                    if (
                        not isinstance(args, list) and
                        not isinstance(args, tuple) and
                        not isinstance(args, set)
                    ):
                        self.options_args.append([args])
                    # Elif it's list / tuple / set and has more than ONE argument...
                    else:
                        self.options_args.append(args)
                else:
                    self.options_args.append([])
                self.options_integers.append(i)
                i += 1
            # Do pages split

        # if self.repeat:
        #     self.options_integers.pop(self.repeat-1)
        #     self.options_names.pop(self.repeat-1)
        #     self.options_args.pop(self.repeat-1)
        #     self.options_actions.pop(self.repeat-1)

        self.pages = self.split_by_pages()
        self.current_options_integers = self.pages[0]

    def split_by_pages(self):
        
        pages = {}

        items_on_page = self.items_on_page if not self.repeat else self.items_on_page - 1

        normal_parts_lenght = len(self.options_integers) // items_on_page
        items_left = len(self.options_integers) - normal_parts_lenght * items_on_page
        
        start_index = 0
        
        for i in range(normal_parts_lenght):
            end_index = start_index + items_on_page
            pages[i] = self.options_integers[start_index:end_index]
            start_index += items_on_page

        pages[normal_parts_lenght] = self.options_integers[-items_left:]

        return pages

    def show(self):


        clean()
            
        print(" ┌{}┐".format(self.width * "─"))
        print(" │{}│".format(self.width * " "))
            
        #
        # Below is true if the text is selected to be proceeded automatically.
        # I.e. in case of text = "Welcome", we will get:
        # ╔═══════════╗
        # ║  Welcome  ║
        # ╚═══════════╝
        # With │ on left and right.
        #
        if self.text:
            # Split text into lines, and strip each line.
            lines = self.text.splitlines()
            lines = [line.strip() for line in lines]

            # Get biggest line, using length as key.
            biggest_line = max(lines, key=len)

            # Here is first bigger counting.
            # width = the available space between two │ characters.
            # len(get_raw_string(biggest_line)) = length of biggest line with removed ANSI sequences.
            # 6 = 2 free spaces on each side - 4, and two characters (╔ & ╗).
            # And we devide entire result with 2.
            spaces_count = (self.width - len(get_raw_string(biggest_line)) - 6) // 2
            spaces = " " * spaces_count
            gora_count = self.width - (spaces_count * 2) - 2
            gora_spacje = "═" * gora_count
            gora_ramki = f" │{spaces}╔{gora_spacje}╗{spaces}│"
            print(gora_ramki)

            for line in lines:

                raw_line = get_raw_string(line)

                if isodd(raw_line):
                    if list(raw_line)[0].isalpha():
                        line += " "
                    else:
                        line = " " + line

                spacje_w_srodku_count = (self.width - len(raw_line) - (spaces_count * 2) - 2) // 2
                spacje_w_srodku = " " * spacje_w_srodku_count

                srodek_ramki = f" │{spaces}║{spacje_w_srodku}{line}{spacje_w_srodku}║{spaces}│"
                print(srodek_ramki)

                # Print current page title.
                
                page_text = f"Page: {self.current_page+1}"
                if isodd(page_text):
                    page_text += " "
                spacje_w_srodku_count = (self.width - len(page_text) - (spaces_count * 2) - 2) // 2
                spacje_w_srodku = " " * spacje_w_srodku_count

                srodek_ramki = f" │{spaces}║{spacje_w_srodku}{page_text}{spacje_w_srodku}║{spaces}│"
                print(srodek_ramki)

            gora_ramki = f" │{spaces}╚{gora_spacje}╝{spaces}│"
            print(gora_ramki)        

            print(" │{}│".format(self.width * " "))
        # If it's custom text provided, just print it, nothing else ;).
        elif self.custom_text:
            print(self.custom_text)

        # Finished printing title, now printing items names.

        self.current_options_integers = self.pages[self.current_page]

        if self.repeat and self.current_options_integers[-1] != self.repeat:
            self.current_options_integers.append(self.repeat)

        for i in self.current_options_integers:

            if self.current_chosen < self.current_options_integers[0]:
                self.current_chosen = self.current_options_integers[-1]

            elif self.current_chosen > self.current_options_integers[-2] if self.repeat and len(self.current_options_integers) > 1 else self.repeat:

                if not self.repeat:
                    self.current_chosen = self.current_options_integers[0]
                else:

                    if self.current_chosen > self.repeat:
                        self.current_chosen == self.current_options_integers[0]
                    else:
                        self.current_chosen = self.repeat

            name = self.options_names[i-1]

            available = self.width - 2 - self.space_left

            if not name:
                spaces = self.width * " "
                print(f" │{spaces}│")
                continue

            visible_i = i if i != self.repeat else 0

            raw_name = get_raw_string(name)
            if iseven(len(str(visible_i))):
                if isodd(raw_name):
                    name += " "

            spaces_count = (available - len(raw_name) - len(str(i)))
            spaces = " " * spaces_count

            parts = split_item(name, i = visible_i)

            for part_index, part in enumerate(parts):

                if i == self.repeat:
                    spaces = self.width * " "
                    print(f" │{spaces}│")

                if part_index == 0:
                    if self.current_chosen == i:
                        print(f" │         {cyan_background}{visible_i}. {part[0]}{reset}{part[1] * ' '}  │")
                    else:
                        print(f" │         {visible_i}. {part[0]}{part[1] * ' '}  │")
        
                elif part_index == (len(parts) - 1):
                    if self.current_chosen == i:
                        print(f" │  {cyan_background}{part[0]}{reset}{part[1] * ' '}│")
                    else:
                        print(f" │  {part[0]}{part[1] * ' '}│")
                else:
                    if self.current_chosen == i:
                        print(f" │  {cyan_background}{part[0]}{reset}  │")
                    else:
                        print(f" │  {part[0]}  │")

        print(" │{}│".format(self.width * " "))
        print(" └{}┘".format(self.width * "─"))

        key = get_key()

        if key == "down":

            self.current_chosen += 1

            if self.repeat and self.current_chosen > self.repeat:

                self.current_chosen = self.current_options_integers[0]

        elif key == "up":
            if self.current_chosen == self.repeat:
                self.current_chosen = self.current_options_integers[-2] if len(self.current_options_integers) > 1 else self.current_options_integers[-1]
            else:
                self.current_chosen -= 1

        elif key == "right":
            self.current_page += 1
            if self.current_page < 0:
                self.current_page = len(self.pages) - 1
            elif self.current_page > len(self.pages) - 1:
                self.current_page = 0
            self.current_chosen = self.pages[self.current_page][0]
        elif key == "left":
            self.current_page -= 1
            if self.current_page < 0:
                self.current_page = len(self.pages) - 1
            elif self.current_page > len(self.pages) - 1:
                self.current_page = 0
            self.current_chosen = self.pages[self.current_page][0]
        elif key.isnumeric() or key == "enter":
            if key == "enter":
                user_choose = self.current_chosen
            elif key.isnumeric():
                key = int(key)
                if key not in self.options_integers:
                    return
                self.current_chosen = key
                user_choose = key
            args = self.options_args[self.options_integers.index(user_choose)]
            if len(args) == 0:
                result = self.options_actions[self.options_integers.index(user_choose)]()
            elif len(args) == 1:
                result = self.options_actions[self.options_integers.index(user_choose)](args[0])
            else:
                result = self.options_actions[self.options_integers.index(user_choose)](*args)
            if result:
                return result
        elif key == "end":
            self.current_chosen = self.current_options_integers[-1]
        elif key == "home":
            self.current_chosen = self.current_options_integers[0]