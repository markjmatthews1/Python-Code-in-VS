from gtts import gTTS

# Create Schwab login audio file
tts_pos = gTTS("Day Trade App is starting, have patience.", lang="en")
tts_pos.save("C:/Users/mjmat/Pythons_Code_Files/day_app_starting.mp3")

print("Audio file created successfully!")