import unittest
from media.mp3_aac_padding_silence_trimmer import MP3AACPaddingSilenceTrimmer


class TestMP3AACPaddingSilenceTrimmer(unittest.TestCase):
    def test_mp3_and_aac_detection(self):
        mp3_res = MP3AACPaddingSilenceTrimmer.analyze_audio_padding(codec="mp3", sample_rate_hz=44100)
        self.assertEqual(mp3_res["status"], "success")
        self.assertEqual(mp3_res["priming_samples_detected"], 576)
        self.assertTrue(mp3_res["re_encoding_avoided"])

        aac_res = MP3AACPaddingSilenceTrimmer.analyze_audio_padding(codec="aac", sample_rate_hz=48000)
        self.assertEqual(aac_res["priming_samples_detected"], 1024)
        self.assertGreater(aac_res["initial_silence_delay_ms"], 10.0)


if __name__ == "__main__":
    unittest.main()
