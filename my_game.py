import cv2
import mediapipe as mp
import pygame.midi
import time
import threading
import numpy as np
from cvzone.HandTrackingModule import HandDetector

class EnhancedAirPiano:
    def __init__(self):
        # Initialize video capture
        self.cap = cv2.VideoCapture(0)
        
        # Initialize hand detector with 2 hands
        self.detector = HandDetector(detectionCon=0.8, maxHands=2)
        
        # Initialize MIDI
        pygame.midi.init()
        self.player = pygame.midi.Output(pygame.midi.get_default_output_id())
        self.player.set_instrument(0)  # Piano instrument
        
        # Extended chord mappings for both hands
        self.left_hand_chords = {
            'C': [60, 64, 67],    # C major
            'Dm': [62, 65, 69],   # D minor
            'Em': [64, 67, 71],   # E minor
            'F': [65, 69, 72],    # F major
            'G': [67, 71, 74],    # G major
            'Am': [69, 72, 76],   # A minor
            'Bdim': [71, 74, 77], # B diminished
        }
        
        self.right_hand_notes = {
            'C5': 72,    # High C
            'D5': 74,    # High D
            'E5': 76,    # High E
            'F5': 77,    # High F
            'G5': 79,    # High G
            'A5': 81,    # High A
            'B5': 83,    # High B
            'C6': 84     # Highest C
        }
        
        self.currently_playing_chords = {}
        self.currently_playing_notes = set()
        self.note_threads = {}

    def play_chord(self, chord_name, hand_id):
        """Play a chord with sustain"""
        chord_key = f"{chord_name}_{hand_id}"
        if chord_key not in self.currently_playing_chords:
            # Stop previous chord for this hand if any
            self.stop_hand_notes(hand_id)
            
            # Play new chord
            chord = self.left_hand_chords[chord_name]
            for note in chord:
                self.player.note_on(note, 100)
            
            # Create sustain thread
            thread = threading.Timer(2.0, self.stop_chord, args=[chord_name, hand_id])
            thread.start()
            self.note_threads[chord_key] = thread
            self.currently_playing_chords[chord_key] = chord

    def play_note(self, note_name):
        """Play a single note"""
        note = self.right_hand_notes[note_name]
        if note not in self.currently_playing_notes:
            self.player.note_on(note, 100)
            self.currently_playing_notes.add(note)
            # Create sustain thread
            thread = threading.Timer(1.0, self.stop_note, args=[note])
            thread.start()
            self.note_threads[note] = thread

    def stop_chord(self, chord_name, hand_id):
        """Stop a specific chord"""
        chord_key = f"{chord_name}_{hand_id}"
        if chord_key in self.currently_playing_chords:
            for note in self.left_hand_chords[chord_name]:
                self.player.note_off(note, 100)
            del self.currently_playing_chords[chord_key]
            if chord_key in self.note_threads:
                del self.note_threads[chord_key]

    def stop_note(self, note):
        """Stop a specific note"""
        if note in self.currently_playing_notes:
            self.player.note_off(note, 100)
            self.currently_playing_notes.remove(note)
            if note in self.note_threads:
                del self.note_threads[note]

    def stop_hand_notes(self, hand_id):
        """Stop all notes for a specific hand"""
        keys_to_remove = [k for k in self.currently_playing_chords.keys() if k.endswith(f"_{hand_id}")]
        for key in keys_to_remove:
            chord_name = key.split('_')[0]
            self.stop_chord(chord_name, hand_id)

    def get_chord_from_fingers(self, fingers):
        """Determine chord based on finger positions for left hand"""
        finger_sum = sum(fingers)
        if finger_sum == 1 and fingers[0]:
            return 'C'
        elif finger_sum == 2 and fingers[0] and fingers[1]:
            return 'Dm'
        elif finger_sum == 3 and fingers[0] and fingers[1] and fingers[2]:
            return 'Em'
        elif finger_sum == 4 and all(fingers[:4]):
            return 'F'
        elif finger_sum == 5:
            return 'G'
        elif finger_sum == 3 and fingers[1] and fingers[2] and fingers[3]:
            return 'Am'
        elif finger_sum == 2 and fingers[1] and fingers[4]:
            return 'Bdim'
        return None

    def get_note_from_fingers(self, fingers):
        """Determine note based on finger positions for right hand"""
        finger_sum = sum(fingers)
        if finger_sum == 1 and fingers[0]:
            return 'C5'
        elif finger_sum == 2 and fingers[0] and fingers[1]:
            return 'D5'
        elif finger_sum == 3 and fingers[0] and fingers[1] and fingers[2]:
            return 'E5'
        elif finger_sum == 4 and all(fingers[:4]):
            return 'F5'
        elif finger_sum == 5:
            return 'G5'
        elif finger_sum == 3 and fingers[1] and fingers[2] and fingers[3]:
            return 'A5'
        elif finger_sum == 2 and fingers[1] and fingers[4]:
            return 'B5'
        elif finger_sum == 1 and fingers[4]:
            return 'C6'
        return None

    def run(self):
        try:
            while True:
                success, img = self.cap.read()
                if not success:
                    break

                # Find hands
                hands, img = self.detector.findHands(img)
                
                if len(hands) > 0:
                    for i, hand in enumerate(hands):
                        # Get finger positions
                        fingers = self.detector.fingersUp(hand)
                        
                        # Check if left or right hand
                        if hand['type'] == 'Left':
                            # Left hand controls chords
                            chord = self.get_chord_from_fingers(fingers)
                            if chord:
                                self.play_chord(chord, i)
                                cv2.putText(img, f"Left: {chord}", (10, 50 + 30*i), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        else:
                            # Right hand controls individual notes
                            note = self.get_note_from_fingers(fingers)
                            if note:
                                self.play_note(note)
                                cv2.putText(img, f"Right: {note}", (10, 50 + 30*i), 
                                          cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                # Display
                cv2.imshow("Enhanced Air Piano", img)
                
                # Exit on 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        finally:
            self.cleanup()

    def cleanup(self):
        """Cleanup resources"""
        # Stop all playing notes
        for chord_key in list(self.currently_playing_chords.keys()):
            chord_name, hand_id = chord_key.split('_')
            self.stop_chord(chord_name, hand_id)
        for note in list(self.currently_playing_notes):
            self.stop_note(note)
            
        self.player.close()
        pygame.midi.quit()
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    piano = EnhancedAirPiano()
    piano.run()