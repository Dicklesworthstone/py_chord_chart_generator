import re
import os
import base64
import time
from typing import List, Tuple, Dict, Optional
import xml.etree.ElementTree as ET
import xml.dom.minidom

class ChordChartGenerator:
    def __init__(self):
        self.frets = 10
        self.strings = 6
        self.width = 250
        self.height = 400
        self.chord_shapes = self._initialize_chord_shapes()
        self.color_schemes = {
            'default': {'background': '#f5f5f5', 'fretboard': '#8a4b08', 'text': '#333', 'finger': '#4CAF50', 'open': '#1e88e5', 'muted': '#e53935'},
            'neon': {'background': '#000000', 'fretboard': '#ffffff', 'text': '#ffffff', 'finger': '#00ff00', 'open': '#00ffff', 'muted': '#ff00ff'}
        }
        self.fonts = {
            'roboto': 'data:font/truetype;charset=utf-8;base64,{}'.format(base64.b64encode(open('Roboto-Regular.ttf', 'rb').read()).decode('utf-8')),
            'noto_music': 'data:font/truetype;charset=utf-8;base64,{}'.format(base64.b64encode(open('NotoMusic-Regular.ttf', 'rb').read()).decode('utf-8'))
        }

    def _initialize_chord_shapes(self) -> Dict[str, List[int]]:
        base_chord_shapes = {
            'major': [0, 2, 2, 1, 0, 0],
            'maj7': [0, 2, 1, 1, 0, 0],
            'maj9': [0, 2, 1, 1, 2, 2],
            'maj13': [0, 2, 1, 1, 2, 3],
            'minor': [0, 1, 2, 2, 0, 0],
            'm7': [0, 1, 0, 0, 0, 0],
            'm9': [0, 1, 0, 0, 2, 0],
            'm11': [0, 1, 0, 0, 0, 1],
            'm13': [0, 1, 0, 0, 2, 3],
            '7': [0, 2, 0, 1, 0, 0],
            '9': [0, 2, 0, 1, 0, 2],
            '11': [0, 2, 0, 1, 0, 3],
            '13': [0, 2, 0, 1, 2, 2],
            'dim': [0, 1, 2, 0, 2, 0],
            'dim7': [0, 1, 2, 0, 2, 3],
            'aug': [0, 3, 2, 1, 1, 0],
            'sus2': [0, 2, 2, 0, 0, 0],
            'sus4': [0, 2, 2, 2, 0, 0],
            '7sus4': [0, 2, 0, 2, 0, 0],
            'add9': [0, 2, 2, 1, 0, 2],
            '6': [0, 2, 2, 1, 2, 0],
            '6/9': [0, 2, 2, 1, 2, 2],
            '5': [0, 3, 2, 0, 0, 0],
            '7b9': [0, 2, 0, 1, 3, 2],
            '7#9': [0, 2, 0, 1, 3, 3],
            '7b5': [0, 2, 0, 1, 5, 3],
            '7#5': [0, 2, 0, 1, 1, 4],
            '9b5': [0, 2, 1, 1, 3, 2],
            '13b9': [0, 2, 1, 3, 3, 4],
            '7#11': [0, 2, 0, 1, 1, 1],
            '7b13': [0, 2, 0, 1, 4, 4],
            'm7b5': [0, 1, 0, 1, 2, 0],
            'm9b5': [0, 1, 0, 1, 2, 2],
            'aug7': [0, 3, 2, 3, 1, 0],
            'aug9': [0, 3, 2, 3, 3, 4],
            '9#11': [0, 2, 1, 1, 1, 2],
            '13#11': [0, 2, 1, 1, 3, 3],
            'm6': [0, 1, 2, 0, 2, 0],
            'm6/9': [0, 1, 2, 2, 2, 2],
            '7#5b9': [0, 3, 2, 3, 2, 0],
            '7#9#5': [0, 3, 2, 3, 3, 0],
            'maj11': [0, 0, 1, 1, 2, 2],
            '13sus4': [0, 2, 0, 2, 2, 2],
            '7b9b13': [0, 2, 0, 1, 3, 4],
            '7#9b13': [0, 2, 0, 1, 3, 4],
            '7#11b13': [0, 2, 0, 1, 1, 4],
            '9#5': [0, 3, 2, 3, 3, 2],
            '9b13': [0, 2, 0, 1, 2, 3],
            'm13b9': [0, 1, 0, 1, 3, 3],
            'maj13#11': [0, 2, 1, 1, 3, 3],
            '13b5': [0, 2, 3, 3, 2, 4],
            '13#9': [0, 2, 0, 1, 3, 2],
            '7alt': [0, 2, 0, 1, 3, 4],
        }

        expanded_chord_shapes = base_chord_shapes.copy()

        # Programmatically add redundant entries
        for chord_name, positions in base_chord_shapes.items():
            if 'major' in chord_name:
                expanded_chord_shapes[chord_name.replace('major', 'maj')] = positions
            if 'minor' in chord_name:
                expanded_chord_shapes[chord_name.replace('minor', 'm')] = positions
            if chord_name.startswith('m'):
                expanded_chord_shapes[chord_name.replace('m', 'min', 1)] = positions

        return expanded_chord_shapes
        
    def parse_chord(self, chord_notation: str) -> Tuple[str, str, List[int], Optional[str]]:
        use_verbose = 1

        if use_verbose:
            print(f"\n🎼 Starting to parse chord notation: '{chord_notation}'")
            print("   This function will analyze the notation, identify the root note, chord quality, and any bass note,")
            print("   and then adjust the finger positions based on the chord structure and the root note.")

        # Step 1: Determine the correct regex pattern based on the chord notation
        if "/" in chord_notation:
            if "m6/9" in chord_notation:
                regex_pattern = r'^([A-G][b#]?)m6/9(?:/([A-G][b#]?))?$'
                if use_verbose:
                    print(f"🔍 Detected 'm6/9' pattern in chord. Using specific regex for 'm6/9' chords: {regex_pattern}")
                    print("\n🎵 **Explanation for Musicians:**")
                    print("   **What is a Regex?**")
                    print("   A 'regex' (short for regular expression) is a special sequence of characters that helps us find patterns in text.")
                    print("   Think of it like a checklist that goes through a piece of text (in this case, a chord notation) and picks out certain parts")
                    print("   based on the rules we set up. For example, it might look for a specific combination of letters and numbers that match")
                    print("   a chord like 'Cmaj7' or 'Am7/G'.")
                    print("")
                    print("   **How This Regex Works:**")
                    print("   This regex pattern is designed to capture a special type of chord known as 'm6/9'.")
                    print("   The pattern '^([A-G][b#]?)m6/9(?:/([A-G][b#]?))?$' does the following:")
                    print("   - ^([A-G][b#]?) identifies the root note (e.g., 'C', 'G#', or 'Bb').")
                    print("   - 'm6/9' looks for this exact chord quality, indicating a minor chord with an added 6th and 9th.")
                    print("   - (?:/([A-G][b#]?))?$ checks for an optional bass note after a slash (e.g., 'C#m6/9/B').")
            else:
                regex_pattern = r'^([A-G][b#]?)([^\s/]+)?(?:/([A-G][b#]?))?$'
                if use_verbose:
                    print(f"🔍 Detected '/' in chord notation. Using general regex for slash chords: {regex_pattern}")
                    print("\n🎵 **Explanation for Musicians:**")
                    print("   **What is a Regex?**")
                    print("   A regex (short for regular expression) is like a pattern-matching tool. It's a way for the program to look at text (like a chord name)")
                    print("   and figure out what parts are what. It's similar to how you might scan a chord chart to pick out certain notes or symbols.")
                    print("")
                    print("   **How This Regex Works:**")
                    print("   This regex pattern handles chords that include a bass note, indicated by a '/' symbol.")
                    print("   The pattern '^([A-G][b#]?)([^\s/]+)?(?:/([A-G][b#]?))?$' works as follows:")
                    print("   - ^([A-G][b#]?) identifies the root note, just like before.")
                    print("   - ([^\s/]+)? captures the chord quality, such as 'maj7', 'm7', or 'dim', which comes after the root note.")
                    print("   - (?:/([A-G][b#]?))?$ looks for a bass note that might be specified after a slash,")
                    print("     for example, the 'G' in 'Cmaj7/G'.")
        else:
            regex_pattern = r'^([A-G][b#]?)([^\s/]*)?$'
            if use_verbose:
                print(f"🔍 No '/' detected. Using regex for standard chords without a bass note: {regex_pattern}")
                print("\n🎵 **Explanation for Musicians:**")
                print("   **What is a Regex?**")
                print("   A regex, or regular expression, is a way to search for specific patterns in text. It's like a set of rules that tells the program")
                print("   how to break down and understand the different parts of a chord name. Think of it as a tool that helps the program")
                print("   'read' the chord name and figure out which part is the root note, which part is the chord quality, and so on.")
                print("")
                print("   **How This Regex Works:**")
                print("   This regex pattern is for simpler chords that don't include a bass note, such as 'Cmaj7' or 'Am'.")
                print("   The pattern '^([A-G][b#]?)([^\s/]*)?$' does the following:")
                print("   - ^([A-G][b#]?) identifies the root note, checking for a sharp or flat as needed.")
                print("   - ([^\s/]*)?$ captures the chord quality that follows the root note, like 'maj7', 'm', or 'dim'.")
                print("     It stops if it sees a space or slash, making sure it only picks up the part of the chord notation")
                print("     that actually describes the chord itself.")

        match = re.match(regex_pattern, chord_notation)

        if not match:
            raise ValueError(f"❌ Error: The chord notation '{chord_notation}' is invalid. Please check your input.")

        if use_verbose:
            print(f"\n🔍 Regex successfully matched the chord components.")
            print(f"   - Root note: {match.group(1)}")
            print(f"   - Chord quality: {match.group(2) or 'None (defaulting to major)'}")
            if len(match.groups()) >= 3:
                print(f"   - Bass note: {match.group(3) or 'None'}")
            else:
                print(f"   - Bass note: None")

        root = match.group(1)
        quality = match.group(2) or ""
        bass = match.group(3) if len(match.groups()) >= 3 else None

        if use_verbose:
            print(f"\n🎯 Extracted root note: '{root}'")
            print(f"🎼 Extracted chord quality: '{quality or 'None'}'")
            print(f"🎸 Extracted bass note: '{bass or 'None'}'")
            print("\n🎵 **Explanation for Musicians:**")
            print("   - **Root Note:** The root note is the fundamental note on which the chord is built. It's the note that gives the chord its name.")
            print("     For example, in a 'Cmaj7' chord, 'C' is the root note. The root note is the most stable note in the chord, and it is usually")
            print("     played as the lowest note in the chord. The root is what the rest of the chord's notes are built around.")
            print("     Understanding the root note is essential because it determines the key and overall tonal center of the chord.")
            print("")
            print("   - **Chord Quality:** The chord quality describes the specific characteristics of the chord, like whether it’s major, minor,")
            print("     diminished, or augmented. It also includes additional tones like sevenths, ninths, and other extensions.")
            print("     For example, in 'Cmaj7', 'maj7' is the quality. The chord quality changes the mood or color of the chord,")
            print("     making it sound happy, sad, tense, or relaxed. Knowing the chord quality helps you understand the chord's function in a song.")
            print("     It tells you what kind of sound to expect from the chord and how it fits within a progression.")
            print("")
            print("   - **Bass Note:** The bass note is the lowest note that is played in a chord. Sometimes the bass note is the same as the root,")
            print("     but it can also be a different note. For example, in the chord 'C/G', 'C' is the root, but 'G' is the bass note.")
            print("     The bass note is important because it anchors the chord and gives it a strong foundation. The choice of bass note can")
            print("     significantly alter the sound of the chord, even if the other notes stay the same. It can create a different feeling or")
            print("     harmonic texture, especially in bass-heavy music like jazz or classical music.")
            print("     Understanding the bass note helps you play the chord correctly, especially if the composer or arranger has specified a particular")
            print("     bass note for a specific effect.")

        # Step 2: Default to 'major' if no quality is provided
        if quality == "":
            quality = "major"
            if use_verbose:
                print(f"ℹ️ No chord quality provided, assuming 'major'.")
                print("   In music theory, a chord symbol like 'C' is shorthand for a major chord ('C major').")

        # Step 3: Analyze and match chord quality
        base_quality = None
        alterations = []

        if use_verbose:
            print(f"\n🔧 Beginning analysis of the chord quality '{quality}'.")
            print("   The function will try to match the longest possible substring of the quality in the known chord shapes.")
            print("   This process helps in identifying the base chord structure (e.g., 'maj7', 'm7', etc.) and any additional alterations (e.g., '#5', 'b9').")
            print("\n🎵 **Explanation for Musicians:**")
            print("   In music, the 'quality' of a chord describes its overall sound or character. This includes whether the chord is major, minor, diminished,")
            print("   augmented, or has added tones like sevenths, ninths, or other extensions.")
            print("   For example, in the chord 'Cmaj7', the 'C' is the root note, and 'maj7' is the quality. The quality tells us that it's a major chord with")
            print("   an added major seventh. Different qualities create different moods or feelings in music, which is why they are so important.")
            print("   This program needs to recognize the quality of a chord to know which notes to play or display in a chord diagram.")
            print("   Here's how the code works:")
            print("   - It starts by looking at the full chord quality to see if it matches any known patterns.")
            print("   - If it doesn't find an exact match, it starts shortening the quality, letter by letter, until it finds a match.")
            print("   - For example, with 'maj7', the code first checks if 'maj7' is recognized. If not, it would try 'maj', and so on.")
            print("   - This helps the code determine the base structure of the chord (like 'maj' for major, 'm' for minor) and then see if there are any additional")
            print("     alterations (like adding a '7', '#5', or 'b9') that modify the basic chord.")
            print("   Understanding the quality of a chord is crucial because it determines the specific notes that make up the chord,")
            print("   and thus how it will sound when played.")

        for length in range(len(quality), 0, -1):
            potential_quality = quality[:length]
            if potential_quality in self.chord_shapes:
                base_quality = potential_quality
                alterations = [quality[length:]] if length < len(quality) else []
                if use_verbose:
                    print(f"   ✅ Matched base quality: '{base_quality}'")
                    if alterations:
                        print(f"   ➕ Detected alterations after base quality: '{alterations}'")
                break

        if base_quality is None:
            raise ValueError(f"🚫 Chord quality '{quality}' not recognized. Ensure the chord is defined in the chord shapes dictionary.")

        # Step 4: Retrieve and display the base finger positions
        finger_positions = self.chord_shapes[base_quality]
        if use_verbose:
            print(f"\n🎶 Retrieved finger positions for the '{base_quality}' chord: {finger_positions}")
            print("   These positions represent the standard way to play this chord quality on the guitar, without any alterations.")

        # Step 5: Apply alterations to the chord
        if alterations:
            print(f"\n🛠 Applying alterations to the base chord '{base_quality}'.")
            print("   Alterations modify the chord by sharpening or flattening specific notes, or adding extra notes.")
        for alteration in alterations:
            if alteration == "#5":
                if use_verbose:
                    print(f"   ⚙️ Applying '#5' alteration: Raising the fifth by one semitone.")
                    print(f"   - The fifth in a '{root}{base_quality}' chord is currently at fret {finger_positions[2]}. Raising it by one semitone.")
                finger_positions[2] = (finger_positions[2] + 1) % 12
            elif alteration == "b5":
                if use_verbose:
                    print(f"   ⚙️ Applying 'b5' alteration: Lowering the fifth by one semitone.")
                    print(f"   - The fifth in a '{root}{base_quality}' chord is currently at fret {finger_positions[2]}. Lowering it by one semitone.")
                finger_positions[2] = (finger_positions[2] - 1) % 12
            elif alteration == "#9":
                if use_verbose:
                    print(f"   ⚙️ Applying '#9' alteration: Raising the ninth by one semitone.")
                    print(f"   - The ninth (second scale degree) is typically the note two steps above the root. Raising it by one semitone.")
                finger_positions[1] = (finger_positions[1] + 1) % 12
            elif alteration == "b9":
                if use_verbose:
                    print(f"   ⚙️ Applying 'b9' alteration: Lowering the ninth by one semitone.")
                    print(f"   - The ninth is the note two steps above the root. Lowering it by one semitone.")
                finger_positions[1] = (finger_positions[1] - 1) % 12
            elif alteration == "add9":
                if use_verbose:
                    print(f"   ➕ Applying 'add9' alteration: Adding the ninth to the chord.")
                    print(f"   - The ninth is an additional note, not part of the original chord structure. Adding it to the chord diagram.")
                finger_positions.append(2)  # Example, add the ninth
            elif alteration == "#11":
                if use_verbose:
                    print(f"   ⚙️ Applying '#11' alteration: Raising the eleventh by one semitone.")
                    print(f"   - The eleventh is typically the note four steps above the root. Raising it by one semitone.")
                finger_positions.append(6)  # Example, add the sharp eleventh
            elif alteration == "b13":
                if use_verbose:
                    print(f"   ⚙️ Applying 'b13' alteration: Lowering the thirteenth by one semitone.")
                    print(f"   - The thirteenth is often an extended note in the chord. Lowering it by one semitone.")
                finger_positions.append(8)  # Example, add the flat thirteenth
            else:
                raise ValueError(f"🚫 Alteration '{alteration}' not recognized. No rule defined for this alteration.")

        # Step 6: Adjust the chord based on the root note
        if use_verbose:
            print(f"\n🔧 Preparing to adjust the finger positions according to the root note '{root}'.")
            print("   This adjustment shifts the entire chord diagram to align with the correct root note on the fretboard.")
            print("   Each note in the chord is transposed to start from the specified root note.")

        root_adjustment = {
            'A': 0, 'A#': 1, 'Bb': 1, 'B': 2, 'C': 3, 'C#': 4, 'Db': 4,
            'D': 5, 'D#': 6, 'Eb': 6, 'E': 7, 'F': 8, 'F#': 9, 'Gb': 9,
            'G': 10, 'G#': 11, 'Ab': 11
        }
        
        adjustment = root_adjustment[root]
        if use_verbose:
            print(f"   ➡️ Calculated root adjustment value for '{root}': {adjustment}")
            print("   This adjustment value represents the number of semitones to shift all finger positions.")
            print("   This ensures the chord is correctly rooted on the specified note.")
            print("\n🎵 **Explanation for Musicians:**")
            print("   In music, the 'root' of a chord is the note that gives the chord its name, like the 'C' in a C major chord.")
            print("   When you play a chord on the guitar, you can move the whole shape up or down the neck to start on a different root note.")
            print("   For example, if you move a C major shape up two frets, you’re now playing a D major chord.")
            print("   This movement is known as transposing, and it involves shifting all the notes in the chord by a certain number of semitones.")
            print("   In this code, the 'root adjustment' is how we figure out how many semitones (half-steps) to move the chord shape so that it starts on the right root note.")
            print("   Here’s how it works:")
            print("   - First, the program identifies the root note you want to start on (like 'F#' or 'Bb').")
            print("   - It then calculates how far you need to move the chord shape to align with this root note.")
            print("   - This calculation is crucial because it ensures that no matter what chord shape you're starting with,")
            print("     you’ll end up playing the correct chord in the correct key.")
            print("   Without this adjustment, the chord would start on the wrong note, and it wouldn’t sound right.")

        finger_positions = [(pos + adjustment) % 12 if pos != 0 else 0 for pos in finger_positions]

        if use_verbose:
            print(f"\n🎸 Final adjusted finger positions after applying root note adjustment: {finger_positions}")
            print(f"   The positions now reflect the chord as it should be played with the root note '{root}'.")

        # Final output
        if use_verbose:
            print(f"\n📋 Final parsed chord details:")
            print(f"   - Root: {root}")
            print(f"   - Quality: {quality}")
            print(f"   - Finger positions: {finger_positions}")
            print(f"   - Bass note: {bass}")
            print(f"   - Full chord notation: {root}{quality}{'/' + bass if bass else ''}")
            print(f"\nℹ️ The chord diagram for '{root}{quality}{'/' + bass if bass else ''}' is now ready for rendering.")
            print("\n____________________________________________________________________________________________________________________________\n")

        return root, quality, finger_positions, bass



    def _add_fonts(self, svg: ET.Element):
        defs = ET.SubElement(svg, 'defs')
        for font_name, font_data in self.fonts.items():
            ET.SubElement(defs, 'style', {'type': 'text/css'}).text = f"""
                @font-face {{
                    font-family: '{font_name}';
                    src: url('{font_data}');
                }}
            """

    def _add_gradients(self, svg: ET.Element, colors: Dict[str, str]):
        defs = svg.find('defs')
        if defs is None:
            defs = ET.SubElement(svg, 'defs')
        
        gradient = ET.SubElement(defs, 'linearGradient', {'id': 'fretboardGradient', 'x1': '0%', 'y1': '0%', 'x2': '100%', 'y2': '100%'})
        ET.SubElement(gradient, 'stop', {'offset': '0%', 'style': f'stop-color:{colors["fretboard"]};stop-opacity:1'})
        ET.SubElement(gradient, 'stop', {'offset': '100%', 'style': f'stop-color:{self._darken_color(colors["fretboard"], 0.2)};stop-opacity:1'})

    def _add_background(self, svg: ET.Element, colors: Dict[str, str]):
        ET.SubElement(svg, 'rect', {
            'width': '100%',
            'height': '100%',
            'fill': colors['background'],
            'rx': '10',
            'ry': '10'
        })

    def _draw_fretboard(self, svg: ET.Element, colors: Dict[str, str]):
        fretboard = ET.SubElement(svg, 'g', {'transform': 'translate(25, 60)'})
        fretboard_width = self.width - 50
        fretboard_height = self.height - 180
        ET.SubElement(fretboard, 'rect', {
            'width': str(fretboard_width),
            'height': str(fretboard_height),
            'fill': f'url(#fretboardGradient)',
            'rx': '5',
            'ry': '5'
        })
        
        # Draw frets
        for i in range(self.frets + 1):
            y = i * (fretboard_height / self.frets)
            ET.SubElement(fretboard, 'line', {
                'x1': '0', 'y1': str(y),
                'x2': str(fretboard_width), 'y2': str(y),
                'stroke': self._lighten_color(colors['fretboard'], 0.3),
                'stroke-width': '2'
            })
        
        # Draw strings
        for i in range(self.strings):
            x = i * (fretboard_width / (self.strings - 1))
            ET.SubElement(fretboard, 'line', {
                'x1': str(x), 'y1': '0',
                'x2': str(x), 'y2': str(fretboard_height),
                'stroke': self._lighten_color(colors['fretboard'], 0.5),
                'stroke-width': '1'
            })
        
        # Add fret numbers
        for i in range(1, self.frets + 1):
            y = (i - 0.5) * (fretboard_height / self.frets)
            ET.SubElement(svg, 'text', {
                'x': '10',
                'y': str(60 + y),
                'font-size': '12',
                'font-family': 'roboto',
                'fill': colors['text'],
                'text-anchor': 'middle'
            }).text = str(i)

    def _add_finger_positions(self, svg: ET.Element, finger_positions: List[int], colors: Dict[str, str]):
        fretboard_width = self.width - 50
        fretboard_height = self.height - 180
        string_spacing = fretboard_width / (self.strings - 1)
        fret_spacing = fretboard_height / self.frets
        for i, pos in enumerate(finger_positions):
            x = 25 + (self.strings - 1 - i) * string_spacing
            if pos > 0:
                y = 60 + (pos - 0.5) * fret_spacing
                self._add_finger_circle(svg, x, y, colors['finger'], colors['text'], str(pos))
            elif pos == 0:
                y = 50
                self._add_open_string(svg, x, y, colors['open'])
            else:  # Muted string
                y = 50
                self._add_muted_string(svg, x, y, colors['muted'])

    def _svg_to_string(self, svg: ET.Element) -> str:
        xml_string = ET.tostring(svg, encoding='unicode')
        pretty_xml_string = xml.dom.minidom.parseString(xml_string).toprettyxml()
        return pretty_xml_string    
    
    def generate_svg(self, chord_notation: str, color_scheme: str = 'default', show_notation: bool = True) -> Tuple[str, str]:
        root, quality, finger_positions, bass = self.parse_chord(chord_notation)
        colors = self.color_schemes[color_scheme]
        
        # Generate guitar diagram SVG
        guitar_svg = self._generate_guitar_svg(root, quality, finger_positions, bass, colors)
        
        # Generate musical notation SVG if requested
        notation_svg = self._generate_notation_svg(root, quality, colors) if show_notation else None
        
        return guitar_svg, notation_svg

    def _generate_guitar_svg(self, root: str, quality: str, finger_positions: List[int], bass: Optional[str], colors: Dict[str, str]) -> str:
        svg = ET.Element('svg', {
            'width': str(self.width),
            'height': str(self.height),
            'xmlns': 'http://www.w3.org/2000/svg'
        })
        
        self._add_fonts(svg)
        self._add_gradients(svg, colors)
        self._add_background(svg, colors)
        self._draw_fretboard(svg, colors)
        self._add_finger_positions(svg, finger_positions, colors)
        self._add_chord_name(svg, root, quality, bass, colors)
        
        return self._svg_to_string(svg)
    
    def _generate_notation_svg(self, root: str, quality: str, colors: Dict[str, str]) -> str:
        svg = ET.Element('svg', {
            'width': str(self.width),
            'height': '150',
            'xmlns': 'http://www.w3.org/2000/svg'
        })
        
        self._add_fonts(svg)
        self._add_background(svg, colors)
        self._add_musical_notation(svg, root, quality, colors)
        
        return self._svg_to_string(svg)

    def _add_musical_notation(self, svg: ET.Element, root: str, quality: str, colors: Dict[str, str]):
        staff_group = ET.SubElement(svg, 'g', {'transform': 'translate(25, 50)'})
        
        # Draw staff lines
        for i in range(5):
            y = i * 10
            ET.SubElement(staff_group, 'line', {
                'x1': '0', 'y1': str(y),
                'x2': str(self.width - 50), 'y2': str(y),
                'stroke': colors['text'], 'stroke-width': '1'
            })
        
        # Add clef
        ET.SubElement(staff_group, 'text', {
            'x': '5', 'y': '35',
            'font-size': '60',
            'font-family': 'noto_music',
            'fill': colors['text']
        }).text = '\uE050'  # Treble clef in Noto Music font
        
        # Add key signature
        key_signature = self._get_key_signature(root)
        self._add_key_signature(staff_group, key_signature, colors['text'])
        
        # Add notes
        note_positions = self._get_note_positions(root, quality)
        x_offset = 70 + len(key_signature) * 10
        for i, (note, octave) in enumerate(note_positions):
            x = x_offset + i * 30
            y = 40 - (note - 1) * 5 - (octave - 4) * 35
            self._add_note(staff_group, x, y, colors['text'])

    def _get_note_positions(self, root: str, quality: str) -> List[Tuple[int, int]]:
        base_notes = {
            'C': 1, 'D': 2, 'E': 3, 'F': 4, 'G': 5, 'A': 6, 'B': 7
        }
        base_note = base_notes[root[0]]
        octave = 4

        if 'b' in root:
            base_note -= 1
        elif '#' in root:
            base_note += 1

        if base_note < 1:
            base_note += 7
            octave -= 1
        elif base_note > 7:
            base_note -= 7
            octave += 1

        if 'minor' in quality or quality.startswith('m'):
            return [(base_note, octave), ((base_note + 2) % 7 or 7, octave), ((base_note + 4) % 7 or 7, octave)]
        else:
            return [(base_note, octave), ((base_note + 2) % 7 or 7, octave), ((base_note + 4) % 7 or 7, octave)]

    def _get_key_signature(self, root: str) -> List[str]:
        sharp_keys = ['G', 'D', 'A', 'E', 'B', 'F#', 'C#']
        flat_keys = ['F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb', 'Cb']
        
        if root in sharp_keys:
            return ['F', 'C', 'G', 'D', 'A', 'E', 'B'][:sharp_keys.index(root) + 1]
        elif root in flat_keys:
            return ['B', 'E', 'A', 'D', 'G', 'C', 'F'][:flat_keys.index(root) + 1]
        else:
            return []

    def _add_key_signature(self, staff_group: ET.Element, key_signature: List[str], color: str):
        x_offset = 50
        y_positions = {'F': 35, 'C': 38, 'G': 31, 'D': 34, 'A': 37, 'E': 30, 'B': 33}
        
        for i, note in enumerate(key_signature):
            x = x_offset + i * 12
            y = y_positions[note]
            if 'F' in key_signature:  # Flat key signature
                self._add_flat(staff_group, x, y, color)
            else:  # Sharp key signature
                self._add_sharp(staff_group, x, y, color)

    def _add_note(self, staff_group: ET.Element, x: float, y: float, color: str):
        # Draw note head
        ET.SubElement(staff_group, 'text', {
            'x': str(x),
            'y': str(y),
            'font-size': '40',
            'font-family': 'noto_music',
            'fill': color,
            'text-anchor': 'middle'
        }).text = '\uE0A4'  # Quarter note head in Noto Music font
        
        # Draw stem
        ET.SubElement(staff_group, 'line', {
            'x1': str(x + 8), 'y1': str(y),
            'x2': str(x + 8), 'y2': str(y - 35),
            'stroke': color, 'stroke-width': '1'
        })

    def _add_flat(self, staff_group: ET.Element, x: float, y: float, color: str):
        ET.SubElement(staff_group, 'text', {
            'x': str(x), 'y': str(y),
            'font-size': '32',
            'font-family': 'noto_music',
            'fill': color
        }).text = '\uE260'  # Flat symbol in Noto Music font

    def _add_sharp(self, staff_group: ET.Element, x: float, y: float, color: str):
        ET.SubElement(staff_group, 'text', {
            'x': str(x), 'y': str(y),
            'font-size': '32',
            'font-family': 'noto_music',
            'fill': color
        }).text = '\uE262'  # Sharp symbol in Noto Music font
    
    def _add_finger_circle(self, svg: ET.Element, x: float, y: float, fill_color: str, text_color: str, label: str):
        ET.SubElement(svg, 'circle', {
            'cx': str(x), 'cy': str(y), 'r': '12',
            'fill': fill_color,
            'stroke': self._darken_color(fill_color, 0.2),
            'stroke-width': '2'
        })
        ET.SubElement(svg, 'text', {
            'x': str(x), 'y': str(y + 5),
            'text-anchor': 'middle',
            'font-size': '14',
            'font-family': 'roboto',
            'font-weight': 'bold',
            'fill': text_color
        }).text = label

    def _add_open_string(self, svg: ET.Element, x: float, y: float, color: str):
        ET.SubElement(svg, 'circle', {
            'cx': str(x), 'cy': str(y), 'r': '8',
            'fill': 'none',
            'stroke': color,
            'stroke-width': '2'
        })

    def _add_muted_string(self, svg: ET.Element, x: float, y: float, color: str):
        size = 8
        ET.SubElement(svg, 'line', {
            'x1': str(x - size), 'y1': str(y - size),
            'x2': str(x + size), 'y2': str(y + size),
            'stroke': color,
            'stroke-width': '2'
        })
        ET.SubElement(svg, 'line', {
            'x1': str(x - size), 'y1': str(y + size),
            'x2': str(x + size), 'y2': str(y - size),
            'stroke': color,
            'stroke-width': '2'
        })

    def _add_chord_name(self, svg: ET.Element, root: str, quality: str, bass: Optional[str], colors: Dict[str, str]):
        chord_name = f"{root}{quality}"
        if bass:
            chord_name += f"/{bass}"

        text_element = ET.SubElement(svg, 'text', {
            'x': str(self.width // 2),
            'y': '30',
            'text-anchor': 'middle',
            'font-size': '24',
            'font-family': 'roboto',
            'font-weight': 'bold',
            'fill': colors['text']
        })

        # Add a subtle text shadow
        shadow = ET.SubElement(text_element, 'tspan', {
            'dx': '1',
            'dy': '1',
            'fill': self._lighten_color(colors['background'], 0.2)
        })
        shadow.text = chord_name

        # Main text
        main_text = ET.SubElement(text_element, 'tspan', {
            'dx': '-1',
            'dy': '-1'
        })
        main_text.text = chord_name

    @staticmethod
    def _lighten_color(color: str, factor: float = 0.1) -> str:
        # Convert hex to RGB
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        
        # Lighten
        r = min(int(r + (255 - r) * factor), 255)
        g = min(int(g + (255 - g) * factor), 255)
        b = min(int(b + (255 - b) * factor), 255)
        
        # Convert back to hex
        return f'#{r:02x}{g:02x}{b:02x}'

    @staticmethod
    def _darken_color(color: str, factor: float = 0.1) -> str:
        # Convert hex to RGB
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        
        # Darken
        r = max(int(r * (1 - factor)), 0)
        g = max(int(g * (1 - factor)), 0)
        b = max(int(b * (1 - factor)), 0)
        
        # Convert back to hex
        return f'#{r:02x}{g:02x}{b:02x}'

# List of all chord examples
chord_examples = [
    # Basic major and minor chords
    ("C", "default"), ("Am", "default"), ("F#", "default"), ("Ebm", "default"),
    
    # Seventh chords
    ("G7", "default"), ("Bm7", "default"), ("Dmaj7", "default"), ("F#m7", "default"),
    
    # Extended chords
    ("A9", "default"), ("Cm11", "default"), ("Gmaj13", "default"), ("E7#9", "default"),
    
    # Sus and add chords
    ("Dsus4", "default"), ("Fsus2", "default"), ("Cadd9", "default"), ("G6", "default"),
    
    # Altered chords
    ("Ab7b5", "default"), ("B7#5", "default"), ("F#7b9", "default"), ("C7#9", "default"),
    
    # Diminished and augmented chords
    ("Ddim", "default"), ("F#dim7", "default"), ("Gaug", "default"), ("Baug7", "default"),
    
    # Complex jazz chords
    ("Cmaj9#11", "default"), ("Dm11b5", "default"), ("G13b9", "default"), ("Ebm9#5", "default"),
    
    # Slash chords
    ("C/E", "default"), ("Am/F#", "default"), ("G/B", "default"), ("F#m7/C#", "default"),
    
    # Exotic and rare chords
    ("C7#9#5", "default"), ("Abmaj7#5", "default"), ("E7alt", "default"), ("Bbm6/9", "default"),
    
    # Chords with multiple alterations
    ("D7b9b13", "default"), ("Gmaj13#11", "default"), ("F#7#9b13", "default"), ("Am11b5", "default"),
    
    # Power chords
    ("C5", "default"), ("G5", "default"), ("F#5", "default"), ("Bb5", "default")
]

use_musical_notation = 0
use_generate_html_gallery = 0

if __name__ == "__main__":
    # Ensure the output directories exist
    os.makedirs("guitar_chord_diagrams", exist_ok=True)
    if use_musical_notation:
        os.makedirs("musical_notation", exist_ok=True)

    # Create an instance of the ChordChartGenerator
    generator = ChordChartGenerator()

    # Generate chord diagrams and musical notation
    for i, (chord, color_scheme) in enumerate(chord_examples):
        # Generate guitar chord diagram and musical notation
        guitar_svg, notation_svg = generator.generate_svg(chord, color_scheme=color_scheme, show_notation=True)
        
        # Save guitar chord diagram
        with open(f"guitar_chord_diagrams/chord_{i+1:03d}_{chord.replace('/', '_')}_{color_scheme}.svg", "w") as f:
            f.write(guitar_svg)
        
        if use_musical_notation:
            # Save musical notation if available
            if notation_svg:
                with open(f"musical_notation/notation_{i+1:03d}_{chord.replace('/', '_')}_{color_scheme}.svg", "w") as f:
                    f.write(notation_svg)
        time.sleep(0.2)
    print("All SVG files have been generated.")

    if use_generate_html_gallery:
        # Generate the HTML gallery
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Chord Chart Gallery</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
                h1, h2 { text-align: center; }
                .gallery { display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; }
                .chord-set { text-align: center; margin-bottom: 20px; }
                img { max-width: 300px; height: auto; border: 1px solid #ddd; border-radius: 4px; }
            </style>
        </head>
        <body>
            <h1>Chord Chart Gallery</h1>
        """

        for i, (chord, color_scheme) in enumerate(chord_examples):
            html_content += f"""
                <h2>{chord} ({color_scheme})</h2>
                <div class="gallery">
                    <div class="chord-set">
                        <h3>Guitar Chord Diagram</h3>
                        <img src="guitar_chord_diagrams/chord_{i+1:03d}_{chord.replace('/', '_')}_{color_scheme}.svg" alt="{chord} guitar chord">
                    </div>
                    <div class="chord-set">
                        <h3>Musical Notation</h3>
                        <img src="musical_notation/notation_{i+1:03d}_{chord.replace('/', '_')}_{color_scheme}.svg" alt="{chord} musical notation">
                    </div>
                </div>
                """

        html_content += """
        </body>
        </html>
        """

        with open("chord_chart_gallery.html", "w") as f:
            f.write(html_content)

        print("HTML gallery file has been generated.")