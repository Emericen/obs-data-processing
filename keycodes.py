from pynput.mouse import Button
from pynput.keyboard import Key

KEY_CODE_MAP = {
    # Special keys
    0x002A: Key.shift_l,      # Left shift
    0x0036: Key.shift_r,      # Right shift
    0x001D: Key.ctrl_l,       # Left control
    0x0E1D: Key.ctrl_r,       # Right control
    0x0038: Key.alt_l,        # Left alt
    0x0E38: Key.alt_r,        # Right alt
    0x0E5B: Key.cmd,          # Left meta/Windows key
    0x0E5C: Key.cmd_r,        # Right meta/Windows key
    0x0E5D: Key.menu,         # Context/Menu key
    
    # Letters
    0x001E: 'a',
    0x0030: 'b',
    0x002E: 'c',
    0x0020: 'd',
    0x0012: 'e',
    0x0021: 'f',
    0x0022: 'g',
    0x0023: 'h',
    0x0017: 'i',
    0x0024: 'j',
    0x0025: 'k',
    0x0026: 'l',
    0x0032: 'm',
    0x0031: 'n',
    0x0018: 'o',
    0x0019: 'p',
    0x0010: 'q',
    0x0013: 'r',
    0x001F: 's',
    0x0014: 't',
    0x0016: 'u',
    0x002F: 'v',
    0x0011: 'w',
    0x002D: 'x',
    0x0015: 'y',
    0x002C: 'z',
    
    # Numbers
    0x0002: '1',
    0x0003: '2',
    0x0004: '3',
    0x0005: '4',
    0x0006: '5',
    0x0007: '6',
    0x0008: '7',
    0x0009: '8',
    0x000A: '9',
    0x000B: '0',
    
    # Function keys
    0x003B: Key.f1,
    0x003C: Key.f2,
    0x003D: Key.f3,
    0x003E: Key.f4,
    0x003F: Key.f5,
    0x0040: Key.f6,
    0x0041: Key.f7,
    0x0042: Key.f8,
    0x0043: Key.f9,
    0x0044: Key.f10,
    0x0057: Key.f11,
    0x0058: Key.f12,
    0x005B: Key.f13,
    0x005C: Key.f14,
    0x005D: Key.f15,
    0x0063: Key.f16,
    0x0064: Key.f17,
    0x0065: Key.f18,
    0x0066: Key.f19,
    0x0067: Key.f20,
    0x0068: Key.f21,
    0x0069: Key.f22,
    0x006A: Key.f23,
    0x006B: Key.f24,
    
    # Special characters and control keys
    0x0001: Key.esc,
    0x000C: '-',
    0x000D: '=',
    0x000E: Key.backspace,
    0x000F: Key.tab,
    0x003A: Key.caps_lock,
    0x001A: ']',
    0x001B: '[',
    0x002B: '\\',
    0x0027: ';',
    0x0028: "'",
    0x001C: Key.enter,
    0x0033: ',',
    0x0034: '.',
    0x0035: '/',
    0x0039: Key.space,
    
    # Navigation and system keys
    0x0E37: Key.print_screen,
    0x0046: Key.scroll_lock,
    0x0E45: Key.pause,
    0x0E52: Key.insert,
    0x0E53: Key.delete,
    0x0E47: Key.home,
    0x0E4F: Key.end,
    0x0E49: Key.page_up,
    0x0E51: Key.page_down,
    0xE048: Key.up,
    0xE04B: Key.left,
    0xE04D: Key.right,
    0xE050: Key.down,
}


MOUSE_BUTTON_MAP = {
    1: Button.left,       # Left click
    2: Button.right,      # Right click
    3: Button.middle,     # Middle click
    4: Button.x1,        # Mouse button 4
    5: Button.x2         # Mouse button 5
}