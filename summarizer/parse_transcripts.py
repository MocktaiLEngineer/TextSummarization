import json
import pandas as pd

class ParseTranscript:
    def __init__(self, transcript_file=None):
        self.transcript_file = transcript_file
        self.transcript = None
        if self.transcript_file:
            self.read_transcript(self.transcript_file)

    def read_transcript(self, file_path):
        with open(file_path, 'r') as file:
            self.transcript = json.load(file)

    def identify_speakers(self):
        if not self.transcript:
            raise Exception("Transcript not loaded. Please load a transcript using 'read_transcript' method.")
        
        speakers = [item['speaker'] for item in self.transcript['meeting_transcripts']]
        unique_speakers = pd.Series(speakers).unique()
        
        return unique_speakers
    
    def get_conversation_of(self, speaker):
        speaker_conversation = [item['content'] for item in self.transcript['meeting_transcripts'] if item['speaker'] == speaker]
        return ' '.join(speaker_conversation)

    def get_meeting_summary(self):
        if not self.transcript:
            raise Exception("Transcript not loaded. Please load a transcript using 'read_transcript' method.")
        
        return self.transcript['general_query_list'][0]['answer']