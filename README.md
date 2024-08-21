# Py Chord Chart Generator

**Py Chord Chart Generator** is a Python tool designed to generate customizable guitar chord diagrams and corresponding musical notation in SVG format. This tool is perfect for musicians, educators, and developers looking to create high-quality chord charts with flexibility in styling and configuration.

## Features

- Generate SVG guitar chord diagrams for a wide variety of chord types, including basic, extended, altered, diminished, augmented, and complex jazz chords.
- Customizable color schemes for chord diagrams, with pre-defined options like `default` and `neon`.
- Support for adding musical notation alongside chord diagrams.
- Robust parsing of chord notations using regular expressions to extract root notes, chord qualities, and optional bass notes.
- Handles chord alterations programmatically, allowing for flexible and dynamic chord rendering.
- Easy-to-use interface with options for generating entire galleries of chord charts.

## Installation

To use the **Py Chord Chart Generator**, clone the repository and install the necessary dependencies.

```bash
git clone https://github.com/Dicklesworthstone/py_chord_chart_generator.git
cd py_chord_chart_generator
pip install -r requirements.txt
```

Ensure that you have the necessary fonts (`Roboto-Regular.ttf` and `NotoMusic-Regular.ttf`) available in the same directory as the script.

## Usage

You can generate chord diagrams and musical notation by running the script:

```bash
python py_chord_chart_generator.py
```

### Command Line Execution

The script generates SVG files for each chord specified in the `chord_examples` list. You can configure whether to generate musical notation and HTML gallery through the boolean flags `use_musical_notation` and `use_generate_html_gallery`.

<div align="center">

| ![Sample Chart for Chord Dmaj7](https://github.com/Dicklesworthstone/py_chord_chart_generator/blob/main/chord_Dmaj7_default.svg) | 
|:--:| 
| *Sample Chart for Chord Dmaj7* |

</div>


## In-Depth Understanding of the `parse_chord` Function

The `parse_chord` function is the core of the **Py Chord Chart Generator**. It is designed to meticulously parse chord notation strings, breaking them down into their fundamental components: root note, chord quality, finger positions, and optional bass note. This parsing capability is what makes the **Py Chord Chart Generator** so powerful, allowing it to handle a vast array of chord symbols, from basic triads to complex jazz chords with multiple alterations.

| ![Screenshot 1](https://raw.githubusercontent.com/Dicklesworthstone/py_chord_chart_generator/main/screenshot_01.webp) | ![Screenshot 2](https://raw.githubusercontent.com/Dicklesworthstone/py_chord_chart_generator/main/screenshot_02.webp) |
|:--:|:--:|
| *Part 1 of parse_chord output* | *Part 2 of parse_chord output* |


### Foundation: `_initialize_chord_shapes` Method

Before diving into `parse_chord`, it's essential to understand the groundwork laid by the `_initialize_chord_shapes` method. This method initializes a dictionary of chord shapes, which forms the basis for identifying and rendering different chord qualities.

#### Step-by-Step Process in `_initialize_chord_shapes`

1. **Base Chord Shapes Definition**:
   The method starts by defining a set of **base chord shapes**. These are the canonical finger positions for the most common chord qualities, such as `major`, `minor`, `7`, `dim`, and their variations. Each chord quality is associated with a list of six integers, representing the frets to be pressed on the guitar's six strings, from low E to high E.

   Example:
   ```python
   'major': [0, 2, 2, 1, 0, 0],  # C major chord in open position
   'm7': [0, 1, 0, 0, 0, 0],     # A minor 7 chord in open position
   ```

2. **Programmatic Expansion**:
   To handle the massive variety of chord notations, the `_initialize_chord_shapes` method programmatically expands the base set of chord shapes. This expansion includes:

   - **Synonym Handling**: Chord qualities often have multiple notations. For instance, `major` can be written as `maj`, and `minor` can appear as `m` or `min`. The method automatically creates redundant entries for these synonyms, ensuring that `parse_chord` can recognize and handle different notations seamlessly.

     Example:
     ```python
     if 'major' in chord_name:
         expanded_chord_shapes[chord_name.replace('major', 'maj')] = positions
     if 'minor' in chord_name:
         expanded_chord_shapes[chord_name.replace('minor', 'm')] = positions
     if chord_name.startswith('m'):
         expanded_chord_shapes[chord_name.replace('m', 'min', 1)] = positions
     ```

   - **Extensive Chord Qualities**: The method also includes complex jazz chords, altered chords, and extended chords, such as `maj13#11`, `m7b5`, and `7#9#5`. These are added to the dictionary with predefined finger positions, allowing for accurate rendering of even the most esoteric chord types.

   This expansion process results in a comprehensive dictionary (`self.chord_shapes`) that maps chord qualities to their respective finger positions, covering nearly every chord a guitarist might encounter.

### Detailed Breakdown of `parse_chord` Function

The `parse_chord` function leverages the dictionary created by `_initialize_chord_shapes` to parse and interpret chord notation strings. Here’s an in-depth look at how it accomplishes this:

#### 1. **Initial Analysis and Regex Selection**:

   - **Slash Chords**: The function first checks if the chord notation contains a `/`, indicating a slash chord (e.g., `Cmaj7/G`). If present, it selects a regex pattern designed to capture both the main chord and the bass note.

   - **Special Cases**: For certain specialized chords like `m6/9`, the function uses specific regex patterns to ensure precise matching. These special cases are handled early to avoid misinterpretation.

   - **Default Regex**: If no slash is detected, the function defaults to a regex pattern that matches standard chord notations, capturing the root note and chord quality.

   Example Regex for Slash Chords:
   ```python
   r'^([A-G][b#]?)([^\s/]+)?(?:/([A-G][b#]?))?$'
   ```
   - **Explanation**:
     - `^([A-G][b#]?)` captures the root note (e.g., `C`, `G#`, `Bb`).
     - `([^\s/]+)?` captures the chord quality (e.g., `maj7`, `m7`).
     - `(?:/([A-G][b#]?))?$` captures the optional bass note (e.g., `G` in `Cmaj7/G`).

#### 2. **Regex Matching and Validation**:

   The function applies the selected regex pattern to the chord notation string. If the string matches the pattern, it extracts the root note, chord quality, and bass note (if present). If the notation doesn't match, an error is raised, ensuring only valid chords are processed.

   - **Root Note Extraction**: The root note is the first captured group in the regex. It is the fundamental note on which the chord is built.
   
   - **Chord Quality Extraction**: The second captured group represents the chord quality. If this is missing (e.g., the notation is just `C`), the function defaults to `major`.

   - **Bass Note Extraction**: If the chord contains a bass note (third captured group), it is also extracted and used later in the rendering process.

   Example:
   - Input: `"Cmaj7/G"`
   - Output: `Root: C`, `Quality: maj7`, `Bass: G`

#### 3. **Chord Quality Analysis**:

   After extracting the chord quality, the function analyzes it to determine the base chord type and any alterations. This analysis is critical for handling complex chords accurately.

   - **Iterative Matching**: The function iteratively checks substrings of the chord quality against the dictionary created by `_initialize_chord_shapes`. It starts with the longest possible substring, gradually shortening it until a match is found. This approach ensures that even complex qualities like `maj13#11` are correctly identified.

   - **Alterations Handling**: Once the base quality is identified, any remaining part of the chord quality string is treated as an alteration (e.g., `#5`, `b9`). These alterations are processed programmatically, modifying the base chord's finger positions as needed.

   Example:
   - Input: `"Cmaj7#5"`
   - Analysis:
     - Base Quality: `maj7`
     - Alteration: `#5`
   - Output: The base quality is identified, and the fifth is raised by one semitone.

#### 4. **Finger Position Calculation**:

   The base quality (and any alterations) is then mapped to a set of finger positions on the guitar fretboard. This is where the power of the `_initialize_chord_shapes` method truly shines, as it allows `parse_chord` to retrieve accurate finger positions for a vast array of chord types.

   - **Applying Alterations**: If alterations are present, the function adjusts the finger positions accordingly. For example, if the alteration is `#5`, the fifth note in the chord is raised by one semitone.

   - **Transposition**: The function also transposes the chord based on the root note, ensuring that the chord diagram reflects the correct positioning on the fretboard.

   Example:
   - Input: `"Cmaj7#5"`
   - Finger Positions Before Alteration: `[0, 2, 1, 1, 0, 0]`
   - After `#5` Alteration: `[0, 3, 1, 1, 0, 0]` (fifth raised by one semitone)

#### 5. **Final Adjustments and Output**:

   Once all components are parsed and calculated, the function prepares the final output. This includes the root note, chord quality, finger positions, and optional bass note.

   - **Rendering Information**: The function returns these details as a tuple, which is then used by other parts of the script to generate the SVG diagram.

   Example:
   - Output: `('C', 'maj7#5', [0, 3, 1, 1, 0, 0], 'G')`

### Special and Unique Features of `parse_chord`

- **Programmatic Flexibility**: The function's ability to handle alterations programmatically is a standout feature. By dynamically adjusting the base chord shapes, it can accommodate a wide range of chord variations, from simple to highly complex.

- **Regex-Based Parsing**: The use of regular expressions in the `parse_chord` function enables it to process diverse chord notations with precision. The flexibility of regex allows the function to differentiate between standard chords, slash chords, and specialized chords, ensuring accurate parsing.

- **Comprehensive Chord Handling**: Thanks to the extensive dictionary generated by `_initialize_chord_shapes`, the `parse_chord` function can recognize and parse a massive variety of chord symbols. This includes not only standard major and minor chords but also complex jazz chords, altered chords, and exotic variations.

- **Educational Verbose Mode**: The function includes a verbose mode that provides detailed explanations of each parsing step. This mode is especially useful for educational purposes, helping musicians understand the intricacies of chord notation and how the function interprets it.

## Color Schemes

The **Py Chord Chart Generator** supports customizable color schemes. Two pre-defined color schemes are provided: `default` and `neon`. Users can add their own color schemes by modifying the `self.color_schemes` dictionary in the `ChordChartGenerator` class.

### Example of Default Color Scheme

```python
'default': {
    'background': '#f5f5f5',
    'fretboard': '#8a4b08',
    'text': '#333',
    'finger': '#4CAF50',
    'open': '#1e88e5',
    'muted': '#e53935'
}
```

### Example of Neon Color Scheme

```python
'neon': {
    'background': '#000000',
    'fretboard': '#ffffff',
    'text': '#ffffff',
    'finger': '#00ff00',
    'open': '#00ffff',
    'muted': '#ff00ff'
}
```

## Generating an HTML Gallery

If the `use_generate_html_gallery` flag is set to `True`, the script will generate an HTML gallery of all generated chord diagrams and musical notation. This gallery is a convenient way to view all the chords at a glance and can be used for educational or presentation purposes.

The gallery includes:
- Guitar chord diagrams.
- Musical notation (if generated).
- A clean and responsive layout for easy browsing.

## Contributing

Contributions are welcome! If you would like to contribute to the **Py Chord Chart Generator**, please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
