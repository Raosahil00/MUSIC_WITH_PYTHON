
# 🎹 Enhanced Air Piano

**Enhanced Air Piano** is a virtual musical instrument that uses computer vision and MIDI technology to turn your hand gestures into piano chords and notes — no physical keyboard required!

## 📽️ What It Does

- **Tracks hands** using a webcam and [cvzone](https://github.com/cvzone/cvzone)'s HandTrackingModule (built on MediaPipe).
- **Plays chords** with the **left hand** and **individual notes** with the **right hand**, based on finger patterns.
- Uses **pygame.midi** to produce real-time piano sounds.
- Offers visual feedback using OpenCV to show which chord or note is being played.

## 🧠 Controls

- ✋ **Left Hand Gestures → Chords**  
  Raise different combinations of fingers to play:
  - Index → C major  
  - Index + Middle → D minor  
  - Index + Middle + Ring → E minor  
  - All fingers → G major, etc.

- 🤚 **Right Hand Gestures → Notes**  
  - Index → C5  
  - Index + Middle → D5  
  - Pinky → C6, etc.

## 🚀 Requirements

Make sure you have these installed:

```bash
pip install opencv-python mediapipe pygame cvzone numpy
```

Also ensure that your device supports **MIDI output** and has a **webcam**.

## ▶️ How to Run

```bash
python my_game.py
```

Press `q` to exit the program.

## 🧹 Cleanup

The script automatically:
- Releases camera resources  
- Turns off all playing notes  
- Closes the MIDI output and OpenCV window  

## 💡 Future Ideas

- Add support for custom chord/note mappings  
- Integrate with real DAWs (e.g., FL Studio, Ableton)  
- Add visual piano interface  

---
