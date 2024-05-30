import time
import serial

# Constants for colors
DEEP_BLUE = 0x00008B00  # 0xRRGGBBWW, no white component for deep blue
PALE_BLUE = 0x87CEEBA0
ORANGE = 0xFFA50000
YELLOW = 0xFFFF0000
WHITE = 0xFFFFFF00

def hex_to_rgbw(hex_value):
    return (
        (hex_value >> 24) & 0xFF,  # Red
        (hex_value >> 16) & 0xFF,  # Green
        (hex_value >> 8) & 0xFF,   # Blue
        hex_value & 0xFF           # White
    )

def rgbw_to_hex(r, g, b, w):
    return (r << 24) | (g << 16) | (b << 8) | w

def setLeds(leds):
    with serial.Serial('COM5', 115200, timeout=1) as ser:
        for led in leds:
            r, g, b, w = hex_to_rgbw(led)
            command = f'0x{r:02X}{g:02X}{b:02X}{w:02X}'
            print(command)
            ser.write(command.encode('utf-8'))

def interpolate_color(color1, color2, factor):
    """ Interpolate between two colors """
    r1, g1, b1, w1 = hex_to_rgbw(color1)
    r2, g2, b2, w2 = hex_to_rgbw(color2)
    r = int(r1 + (r2 - r1) * factor)
    g = int(g1 + (g2 - g1) * factor)
    b = int(b1 + (b2 - b1) * factor)
    w = int(w1 + (w2 - w1) * factor)
    return rgbw_to_hex(r, g, b, w)

def generate_sunrise_effect(center, numLED, step, total_steps):
    leds = [DEEP_BLUE] * numLED
    max_distance = max(center, numLED - center)
    
    for i in range(numLED):
        distance = abs(center - i)
        factor = distance / max_distance
        transition_factor = step / total_steps
        
        if factor < 0.33:  # Closest to the center
            color = interpolate_color(DEEP_BLUE, WHITE, transition_factor * (1 - factor / 0.33))
        elif factor < 0.66:  # Middle range
            color = interpolate_color(DEEP_BLUE, ORANGE, transition_factor * (1 - (factor - 0.33) / 0.33))
        else:  # Farthest from the center
            color = interpolate_color(DEEP_BLUE, PALE_BLUE, transition_factor * (1 - (factor - 0.66) / 0.34))
        
        leds[i] = color

    setLeds(leds)

def sunrise_effect(center, numLED, night_steps=50, sunrise_steps=100, delay=0.1):
    # Night phase: all LEDs deep blue
    for step in range(night_steps):
        setLeds([DEEP_BLUE] * numLED)
        time.sleep(delay)

    # Sunrise phase: transition to sunrise colors
    for step in range(sunrise_steps):
        generate_sunrise_effect(center, numLED, step, sunrise_steps)
        time.sleep(delay)

# Example usage:
if __name__ == "__main__":
    numLED = 60
    center = 30
    sunrise_effect(center, numLED)
