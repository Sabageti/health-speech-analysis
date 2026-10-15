import torch
import whisper
import soundfile as sf

class AcousticFeatures:
    """
    Stage 1: Acoustic & Temporal Features extraction via Silero VAD and Whisper ASR.
    Includes operations like finding Pause duration, Speech duration, Utterance length and Words Per Minute.
    """
    def __init__(self):
        self.vad_model = None
        self.vad_utils = None
        self.asr_model = None

    def _load_vad_model(self):
        if self.vad_model is None:
            print("Loading Silero VAD model...")
            self.vad_model, self.vad_utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                trust_repo=True
            )

    def _load_asr_model(self):
        if self.asr_model is None:
            print("Loading Whisper ASR model ('base')...")
            self.asr_model = whisper.load_model("base")

    def run_vad(self, audio_path: str):
        self._load_vad_model()
        (get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = self.vad_utils

        print("Running VAD inference...")
        data, sr = sf.read(audio_path)
        if sr != 16000:
            pass # assumed to be 16k due to preprocess_audio
        wav = torch.from_numpy(data).float()
        if len(wav.shape) > 1:
            wav = wav.mean(dim=1)

        speech_timestamps = get_speech_timestamps(wav, self.vad_model, sampling_rate=16000, min_silence_duration_ms=250)

        total_audio_duration_sec = len(wav) / 16000.0
        total_speech_sec = 0.0
        pauses = []

        last_end = 0
        for segment in speech_timestamps:
            start_sec = segment['start'] / 16000.0
            end_sec = segment['end'] / 16000.0
            total_speech_sec += (end_sec - start_sec)

            pause_duration = start_sec - last_end
            if pause_duration >= 0.25:
                pauses.append(pause_duration)
            last_end = end_sec

        num_pauses = len(pauses)
        total_pause_sec = sum(pauses)
        mean_pause_sec = total_pause_sec / num_pauses if num_pauses > 0 else 0

        return {
            "total_audio_duration_sec": total_audio_duration_sec,
            "total_speech_duration_sec": total_speech_sec,
            "total_pause_duration_sec": total_pause_sec,
            "pause_count": num_pauses,
            "mean_pause_duration_sec": mean_pause_sec,
            "pause_time_percentage": (total_pause_sec / total_audio_duration_sec) * 100 if total_audio_duration_sec > 0 else 0,
            "speech_timestamps": speech_timestamps
        }

    def run_asr(self, audio_path: str):
        self._load_asr_model()
        print("Running ASR inference...")
        result = self.asr_model.transcribe(
            audio_path,
            word_timestamps=True,
            fp16=False,
            temperature=0,
            condition_on_previous_text=False,
            no_speech_threshold=0.6,
            initial_prompt="Umm, let me think, uh, okay."
        )

        segments = result.get('segments', [])
        total_words = 0
        words_per_utterance = []

        for segment in segments:
            words_in_segment = len(segment.get('words', []))
            total_words += words_in_segment
            words_per_utterance.append(words_in_segment)

        num_utterances = len(words_per_utterance)
        mean_utterance_length = total_words / num_utterances if num_utterances > 0 else 0

        return {
            "total_words": total_words,
            "total_utterances": num_utterances,
            "mean_utterance_length": mean_utterance_length,
            "text": result['text']
        }

    def extract_features(self, audio_path: str):
        """
        Orchestrates extracting both VAD and ASR metrics and computes joint metrics (e.g., WPM).
        """
        vad_results = self.run_vad(audio_path)
        asr_results = self.run_asr(audio_path)

        speech_minutes = vad_results["total_speech_duration_sec"] / 60.0
        wpm = asr_results["total_words"] / speech_minutes if speech_minutes > 0 else 0

        return {
            "metrics": {
                "Audio_Duration_sec": round(vad_results["total_audio_duration_sec"], 2),
                "Total_Words_Spoken": asr_results["total_words"],
                "Words_Per_Minute (WPM)": round(wpm, 2),
                "Mean_Utterance_Length (Words)": round(asr_results["mean_utterance_length"], 2),
                "Mean_Pause_Duration_sec": round(vad_results["mean_pause_duration_sec"], 2),
                # "Total_Pause_Time_Percentage": f"{round(vad_results['pause_time_percentage'], 2)}%",
                # "Pause_Count": vad_results["pause_count"],
                # "Speech_Duration_sec": round(vad_results["total_speech_duration_sec"], 2),

            },
            "transcript": asr_results["text"].strip()
        }
